//! Immutable, byte-verified native assets. Release pins ship with the adapter;
//! a worktree cannot change the URL, digest, platform or active release.
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::{
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
};
use zed_extension_api as zed;

const PINS: &str = include_str!("../releases/server.json");
const MAX_ASSET_BYTES: u64 = 128 * 1024 * 1024;
static NEXT_TEMP: AtomicU64 = AtomicU64::new(0);

#[derive(Deserialize, Clone)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ReleasePins {
    format: String,
    active_release: Option<String>,
    releases: Vec<Release>,
}

#[derive(Deserialize, Clone)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Release {
    id: String,
    server_version: String,
    protocol_version: String,
    compiler_version: String,
    virtual_document_navigation_opt_out: bool,
    assets: Vec<Asset>,
}

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Asset {
    platform: String,
    url: String,
    sha256: String,
    size: u64,
}

fn digest(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
}

fn token(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 100
        && value
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"-_".contains(&c))
}

fn asset_url(url: &str) -> bool {
    // Loopback HTTP is solely for generated private development candidates.
    // Public exports separately require HTTPS and reject loopback/private URLs.
    let tail = url
        .strip_prefix("https://")
        .or_else(|| url.strip_prefix("http://127.0.0.1:"));
    tail.is_some_and(|tail| {
        !tail.is_empty()
            && !tail.contains(['@', '?', '#', '\\'])
            && !tail
                .bytes()
                .any(|b| b.is_ascii_whitespace() || b.is_ascii_control())
            && tail.contains('/')
            && !url.split('/').any(|part| matches!(part, "latest" | ".."))
    })
}

impl ReleasePins {
    pub fn parse(text: &str) -> zed::Result<Self> {
        let pins: Self = zed::serde_json::from_str(text)
            .map_err(|e| format!("Invalid pinned Acore release manifest: {e}"))?;
        if pins.format != "acore-server-releases/v1" {
            return Err("Unsupported Acore release manifest format".into());
        }
        let mut ids = std::collections::HashSet::new();
        for release in &pins.releases {
            if !token(&release.id)
                || !ids.insert(&release.id)
                || !release.server_version.starts_with("acore/")
                || release.server_version.len() <= 6
                || release.protocol_version != "axiom-editor/v1"
                || !digest(&release.compiler_version)
                || !release.virtual_document_navigation_opt_out
                || release.assets.is_empty()
            {
                return Err("Invalid or duplicate pinned Acore release identity".into());
            }
            let mut platforms = std::collections::HashSet::new();
            for asset in &release.assets {
                if !matches!(
                    asset.platform.as_str(),
                    "macos-aarch64"
                        | "macos-x86_64"
                        | "linux-x86_64"
                        | "linux-aarch64"
                        | "windows-x86_64"
                        | "windows-aarch64"
                ) || !platforms.insert(&asset.platform)
                    || !asset_url(&asset.url)
                    || !digest(&asset.sha256)
                    || asset.size == 0
                    || asset.size > MAX_ASSET_BYTES
                {
                    return Err("Invalid or duplicate pinned Acore asset".into());
                }
            }
        }
        if pins
            .active_release
            .as_ref()
            .is_some_and(|active| !ids.contains(active))
        {
            return Err("Active Acore release is not pinned".into());
        }
        Ok(pins)
    }

    fn selected(&self, platform: &str) -> zed::Result<(&Release, &Asset)> {
        let active = self.active_release.as_ref().ok_or("No approved Acore download release is enabled. Set lsp.acore-lsp.binary.path or install a compatible acore-lsp on worktree PATH.")?;
        let release = self.releases.iter().find(|r| &r.id == active).unwrap();
        let asset = release.assets.iter().find(|a| a.platform == platform).ok_or_else(|| format!("No approved Acore asset for {platform}. macOS ARM64 is the current acceptance host; other OS acceptance is pending. Select a compatible user-installed binary with lsp.acore-lsp.binary.path."))?;
        Ok((release, asset))
    }
}

fn platform(os: zed::Os, architecture: zed::Architecture) -> zed::Result<&'static str> {
    match (os, architecture) {
        (zed::Os::Mac, zed::Architecture::Aarch64) => Ok("macos-aarch64"),
        (zed::Os::Mac, zed::Architecture::X8664) => Ok("macos-x86_64"),
        (zed::Os::Linux, zed::Architecture::X8664) => Ok("linux-x86_64"),
        (zed::Os::Linux, zed::Architecture::Aarch64) => Ok("linux-aarch64"),
        (zed::Os::Windows, zed::Architecture::X8664) => Ok("windows-x86_64"),
        (zed::Os::Windows, zed::Architecture::Aarch64) => Ok("windows-aarch64"),
        _ => Err(
            "Acore has no approved 32-bit server asset; select a supported execution host".into(),
        ),
    }
}

pub fn install(id: &zed::LanguageServerId) -> zed::Result<String> {
    let pins = ReleasePins::parse(PINS)?;
    let (os, arch) = zed::current_platform();
    let (release, asset) = pins.selected(platform(os, arch)?)?;
    let cwd =
        std::env::current_dir().map_err(|e| format!("Acore extension cache unavailable: {e}"))?;
    let result = ensure_asset(
        &cwd,
        release,
        asset,
        |url, sink| {
            zed::set_language_server_installation_status(
                id,
                &zed::LanguageServerInstallationStatus::Downloading,
            );
            let stream = zed::http_client::HttpRequest::builder()
                .method(zed::http_client::HttpMethod::Get)
                .url(url)
                .redirect_policy(zed::http_client::RedirectPolicy::FollowLimit(5))
                .build()?
                .fetch_stream()?;
            while let Some(chunk) = stream.next_chunk()? {
                sink(&chunk)?;
            }
            Ok(())
        },
        |path| zed::make_file_executable(&path.to_string_lossy()),
    );
    match result {
        Ok(path) => {
            zed::set_language_server_installation_status(
                id,
                &zed::LanguageServerInstallationStatus::None,
            );
            Ok(path.to_string_lossy().into_owned())
        }
        Err(error) => {
            let error = format!("Acore server installation failed: {error}. Restart to retry the pinned asset, or select a verified offline binary with lsp.acore-lsp.binary.path. Prior release caches are retained.");
            zed::set_language_server_installation_status(
                id,
                &zed::LanguageServerInstallationStatus::Failed(error.clone()),
            );
            Err(error)
        }
    }
}

fn directory(path: &Path) -> zed::Result<()> {
    match fs::symlink_metadata(path) {
        Ok(meta) if meta.is_dir() && !meta.file_type().is_symlink() => Ok(()),
        Ok(_) => Err(format!(
            "Refusing non-directory/symlink cache path {}",
            path.display()
        )),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            fs::create_dir(path).map_err(|e| e.to_string())
        }
        Err(e) => Err(e.to_string()),
    }
}

fn verified(path: &Path, asset: &Asset) -> zed::Result<bool> {
    let meta = match fs::symlink_metadata(path) {
        Ok(meta) => meta,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(e) => return Err(e.to_string()),
    };
    if !meta.is_file() || meta.file_type().is_symlink() {
        return Err("Refusing non-file/symlink cached server".into());
    }
    if meta.len() != asset.size {
        return Ok(false);
    }
    let mut file = File::open(path).map_err(|e| e.to_string())?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 64 * 1024];
    let mut size = 0;
    loop {
        let n = file.read(&mut buffer).map_err(|e| e.to_string())?;
        if n == 0 {
            break;
        }
        size += n as u64;
        if size > asset.size {
            return Ok(false);
        }
        hasher.update(&buffer[..n]);
    }
    Ok(size == asset.size && format!("{:x}", hasher.finalize()) == asset.sha256)
}

struct Partial(PathBuf);
impl Drop for Partial {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn ensure_asset(
    root: &Path,
    release: &Release,
    asset: &Asset,
    download: impl FnOnce(&str, &mut dyn FnMut(&[u8]) -> zed::Result<()>) -> zed::Result<()>,
    mut executable: impl FnMut(&Path) -> zed::Result<()>,
) -> zed::Result<PathBuf> {
    let mut dir = root.to_path_buf();
    for segment in ["servers", &release.id, &asset.platform, &asset.sha256] {
        dir.push(segment);
        directory(&dir)?;
    }
    let path = dir.join(if asset.platform.starts_with("windows-") {
        "acore-lsp.exe"
    } else {
        "acore-lsp"
    });
    if verified(&path, asset)? {
        executable(&path)?;
        return Ok(path);
    }
    // Exclusive creation tolerates a hard-interrupted prior attempt without
    // following or treating its partial file as a server. Promotion is atomic.
    let (partial, mut file) = loop {
        let temp = dir.join(format!(
            ".download-{}",
            NEXT_TEMP.fetch_add(1, Ordering::Relaxed)
        ));
        match OpenOptions::new().write(true).create_new(true).open(&temp) {
            Ok(file) => break (Partial(temp), file),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => return Err(e.to_string()),
        }
    };
    let mut hasher = Sha256::new();
    let mut size = 0u64;
    download(&asset.url, &mut |bytes| {
        size = size
            .checked_add(bytes.len() as u64)
            .ok_or("Acore download size overflow")?;
        if size > asset.size {
            return Err("Acore download exceeds pinned size".into());
        }
        file.write_all(bytes).map_err(|e| e.to_string())?;
        hasher.update(bytes);
        Ok(())
    })?;
    if size != asset.size || format!("{:x}", hasher.finalize()) != asset.sha256 {
        return Err(
            "Acore download size/SHA-256 mismatch; unverified bytes were not executed".into(),
        );
    }
    file.flush().map_err(|e| e.to_string())?;
    drop(file);
    executable(&partial.0)?;
    // Verify persisted bytes, including after the host permission operation.
    if !verified(&partial.0, asset)? {
        return Err("Acore persisted download failed SHA-256 verification".into());
    }
    fs::rename(&partial.0, &path).map_err(|e| e.to_string())?;
    Ok(path)
}

#[cfg(test)]
mod tests;
