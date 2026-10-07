use super::*;
use zed::serde_json::{json, Value};

struct Temp(PathBuf);
impl Temp {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "acore-installer-{}-{}",
            std::process::id(),
            NEXT_TEMP.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
}
impl Drop for Temp {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

const BYTES: &[u8] = b"reviewed test server, never executed";
fn manifest() -> Value {
    json!({"format":"acore-server-releases/v1","activeRelease":"release-1","releases":[{
    "id":"release-1","serverVersion":"acore/0.1.2 (E7)","protocolVersion":"axiom-editor/v1",
    "compilerVersion":"a".repeat(64),"virtualDocumentNavigationOptOut":true,"assets":[{
        "platform":"macos-aarch64","url":"https://example.org/releases/release-1/acore-lsp",
        "sha256":format!("{:x}",Sha256::digest(BYTES)),"size":BYTES.len()
    }]}]})
}
fn pins() -> ReleasePins {
    ReleasePins::parse(&manifest().to_string()).unwrap()
}
fn good(_: &str, sink: &mut dyn FnMut(&[u8]) -> zed::Result<()>) -> zed::Result<()> {
    for bytes in BYTES.chunks(3) {
        sink(bytes)?;
    }
    Ok(())
}
fn no_exec(_: &Path) -> zed::Result<()> {
    Ok(())
}

#[test]
fn disabled_release_and_unaccepted_platform_have_actionable_errors() {
    let empty = ReleasePins::parse(
        r#"{"format":"acore-server-releases/v1","activeRelease":null,"releases":[]}"#,
    )
    .unwrap();
    assert!(empty
        .selected("macos-aarch64")
        .err()
        .unwrap()
        .contains("binary.path"));
    assert!(pins()
        .selected("linux-x86_64")
        .err()
        .unwrap()
        .contains("pending"));
    assert!(platform(zed::Os::Mac, zed::Architecture::X86).is_err());
    assert_eq!(
        platform(zed::Os::Linux, zed::Architecture::Aarch64).unwrap(),
        "linux-aarch64"
    );
    assert_eq!(
        platform(zed::Os::Windows, zed::Architecture::X8664).unwrap(),
        "windows-x86_64"
    );
}

#[test]
fn pins_reject_mutable_unknown_or_unsafe_identities() {
    let original = manifest();
    for (pointer, bad) in [
        ("/format", json!("future")),
        ("/activeRelease", json!("missing")),
        ("/releases/0/id", json!("../escape")),
        ("/releases/0/compilerVersion", json!("unknown")),
        ("/releases/0/protocolVersion", json!("axiom-editor/v2")),
        ("/releases/0/virtualDocumentNavigationOptOut", json!(false)),
        ("/releases/0/assets/0/platform", json!("universal")),
        ("/releases/0/assets/0/size", json!(MAX_ASSET_BYTES + 1)),
        ("/releases/0/assets/0/size", json!(0)),
        ("/releases/0/assets/0/sha256", json!("Z".repeat(64))),
        ("/releases/0/assets/0/url", json!("http://remote/asset")),
        (
            "/releases/0/assets/0/url",
            json!("https://user:token@example.org/asset"),
        ),
        (
            "/releases/0/assets/0/url",
            json!("https://example.org/latest/acore-lsp"),
        ),
    ] {
        let mut value = original.clone();
        *value.pointer_mut(pointer).unwrap() = bad;
        assert!(ReleasePins::parse(&value.to_string()).is_err(), "{pointer}");
    }
    let mut value = original.clone();
    value["credential"] = json!("no");
    assert!(ReleasePins::parse(&value.to_string()).is_err());
    let mut value = original.clone();
    value["releases"]
        .as_array_mut()
        .unwrap()
        .push(original["releases"][0].clone());
    assert!(ReleasePins::parse(&value.to_string()).is_err());
    let mut value = original.clone();
    value["releases"][0]["assets"]
        .as_array_mut()
        .unwrap()
        .push(original["releases"][0]["assets"][0].clone());
    assert!(ReleasePins::parse(&value.to_string()).is_err());
}

#[test]
fn verifies_stream_promotes_and_reuses_cache_without_network() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    let path = ensure_asset(&temp.0, r, a, good, |p| {
        assert_eq!(fs::read(p).unwrap(), BYTES);
        Ok(())
    })
    .unwrap();
    assert_eq!(fs::read(&path).unwrap(), BYTES);
    assert_eq!(
        ensure_asset(
            &temp.0,
            r,
            a,
            |_, _| panic!("offline reuse must not download"),
            no_exec
        )
        .unwrap(),
        path
    );
    assert!(fs::read_dir(path.parent().unwrap()).unwrap().all(|p| !p
        .unwrap()
        .file_name()
        .to_string_lossy()
        .starts_with(".download-")));
}

#[test]
fn corrupt_and_truncated_downloads_never_reach_permission_or_promotion() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    for bytes in [
        vec![b'x'; BYTES.len()],
        BYTES[..3].to_vec(),
        vec![b'x'; BYTES.len() + 1],
    ] {
        assert!(ensure_asset(
            &temp.0,
            r,
            a,
            |_, sink| sink(&bytes),
            |_| panic!("unverified bytes")
        )
        .is_err());
    }
    let path = temp
        .0
        .join("servers")
        .join(&r.id)
        .join(&a.platform)
        .join(&a.sha256);
    assert_eq!(fs::read_dir(path).unwrap().count(), 0);
}

#[test]
fn interruption_and_network_failure_preserve_old_releases_and_recover() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    let old = ensure_asset(&temp.0, r, a, good, no_exec).unwrap();
    let mut next = r.clone();
    next.id = "release-2".into();
    assert!(ensure_asset(
        &temp.0,
        &next,
        a,
        |_, sink| {
            sink(&BYTES[..4])?;
            Err("interrupted download".into())
        },
        |_| panic!("must not execute")
    )
    .is_err());
    assert!(ensure_asset(&temp.0, &next, a, |_, _| Err("HTTP 404".into()), no_exec).is_err());
    assert_eq!(fs::read(&old).unwrap(), BYTES);
    let new = ensure_asset(&temp.0, &next, a, good, no_exec).unwrap();
    assert_ne!(new, old);
    assert_eq!(
        ensure_asset(
            &temp.0,
            r,
            a,
            |_, _| panic!("rollback reuses old cache"),
            no_exec
        )
        .unwrap(),
        old
    );
}

#[test]
fn corrupted_cache_is_rehashed_and_failed_repair_never_runs_it() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    let path = ensure_asset(&temp.0, r, a, good, no_exec).unwrap();
    fs::write(&path, vec![b'x'; BYTES.len()]).unwrap();
    assert!(ensure_asset(
        &temp.0,
        r,
        a,
        |_, _| Err("offline".into()),
        |_| panic!("must not execute corrupt cache")
    )
    .is_err());
    assert_eq!(fs::read(&path).unwrap(), vec![b'x'; BYTES.len()]);
    assert_eq!(ensure_asset(&temp.0, r, a, good, no_exec).unwrap(), path);
    assert_eq!(fs::read(path).unwrap(), BYTES);
}

#[test]
fn permission_failure_is_visible_and_removes_partial_artifact() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    assert!(
        ensure_asset(&temp.0, r, a, good, |_| Err("permission denied".into()))
            .unwrap_err()
            .contains("permission denied")
    );
    let path = ensure_asset(&temp.0, r, a, good, no_exec).unwrap();
    assert!(ensure_asset(
        &temp.0,
        r,
        a,
        |_, _| panic!("no download"),
        |_| Err("permission denied".into())
    )
    .is_err());
    assert_eq!(fs::read(path).unwrap(), BYTES);
}

#[test]
fn leftover_partial_and_host_mutated_bytes_are_not_promoted() {
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    assert!(ensure_asset(&temp.0, r, a, good, |p| {
        fs::write(p, b"changed by host").unwrap();
        Ok(())
    })
    .is_err());
    let dir = temp
        .0
        .join("servers")
        .join(&r.id)
        .join(&a.platform)
        .join(&a.sha256);
    fs::write(dir.join(".download-old"), BYTES).unwrap();
    assert!(ensure_asset(
        &temp.0,
        r,
        a,
        |_, _| Err("network unavailable".into()),
        no_exec
    )
    .is_err());
    assert!(!dir.join("acore-lsp").exists());
    assert!(ensure_asset(&temp.0, r, a, good, no_exec).is_ok());
}

#[cfg(unix)]
#[test]
fn symlink_cache_entries_and_directories_are_rejected() {
    use std::os::unix::fs::symlink;
    let temp = Temp::new();
    let pins = pins();
    let (r, a) = pins.selected("macos-aarch64").unwrap();
    let path = ensure_asset(&temp.0, r, a, good, no_exec).unwrap();
    fs::remove_file(&path).unwrap();
    let external = temp.0.join("external");
    fs::write(&external, BYTES).unwrap();
    symlink(&external, &path).unwrap();
    assert!(ensure_asset(&temp.0, r, a, |_, _| panic!("symlink must fail"), no_exec).is_err());
    assert_eq!(fs::read(&external).unwrap(), BYTES);
    let another = Temp::new();
    symlink(&temp.0, another.0.join("servers")).unwrap();
    assert!(ensure_asset(&another.0, r, a, good, no_exec).is_err());
}

#[test]
fn withdrawn_versions_and_native_digests_cannot_be_restored_as_valid_pins() {
    for version in ["acore/0.1.0 (E7)", "acore/0.1.1 (E7)"] {
        let mut value = manifest(); value["releases"][0]["serverVersion"] = json!(version);
        assert!(ReleasePins::parse(&value.to_string()).is_err());
    }
    for hash in crate::server::WITHDRAWN_SHA256 {
        let mut value = manifest(); value["releases"][0]["assets"][0]["sha256"] = json!(hash);
        assert!(ReleasePins::parse(&value.to_string()).is_err());
    }
}
