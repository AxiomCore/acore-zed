use zed_extension_api as zed;

const PROTOCOL: &str = "axiom-editor/v1";
const MAX_VERSION_BYTES: usize = 16 * 1024;

pub fn absolute_command(command: &str, root: &str) -> String {
    if command.starts_with('/')
        || command.starts_with("\\\\")
        || (command.as_bytes().get(1) == Some(&b':'))
    {
        return command.to_owned();
    }
    let separator = if root.as_bytes().get(1) == Some(&b':') || root.starts_with("\\\\") {
        '\\'
    } else {
        '/'
    };
    format!("{}{separator}{command}", root.trim_end_matches(['/', '\\']))
}

pub fn check_compatible(
    command: &zed::Command,
    mut environment: Vec<(String, String)>,
) -> zed::Result<()> {
    environment.extend(command.env.clone());
    // Version metadata is a separate invocation. Runtime arguments are left
    // untouched for the stdio process; wrappers must implement this flag too.
    let output = zed::process::Command::new(&command.command)
        .arg("--version-json")
        .envs(environment)
        .output()
        .map_err(|error| format!("Acore could not inspect {} with --version-json: {error}. Check the executable path, permissions and host OS/architecture.", command.command))?;
    validate_version(output.status, &output.stdout)
        .map_err(|error| format!("Acore rejected {}: {error}. Select a compatible standalone acore-lsp with lsp.acore-lsp.binary.path or worktree PATH.", command.command))
}

fn validate_version(status: Option<i32>, stdout: &[u8]) -> zed::Result<()> {
    if status != Some(0) {
        return Err(format!("--version-json failed (exit status {status:?})"));
    }
    if stdout.len() > MAX_VERSION_BYTES {
        return Err("--version-json returned excessive output".into());
    }
    let info: zed::serde_json::Value = zed::serde_json::from_slice(stdout)
        .map_err(|_| "--version-json did not return Acore version metadata")?;
    if !info
        .get("serverVersion")
        .and_then(|v| v.as_str())
        .is_some_and(|v| v.starts_with("acore/") && v.len() > 6)
    {
        return Err("executable does not identify itself as acore-lsp".into());
    }
    if info.get("protocolVersion").and_then(|v| v.as_str()) != Some(PROTOCOL) {
        return Err(format!(
            "incompatible editor protocol; this adapter requires {PROTOCOL}"
        ));
    }
    if !info
        .get("compilerVersion")
        .and_then(|v| v.as_str())
        .is_some_and(|v| v.len() == 64 && v.bytes().all(|c| c.is_ascii_hexdigit()))
    {
        return Err("version metadata lacks a valid compiler fingerprint".into());
    }
    if info.pointer("/editorFeatures/virtualDocumentNavigationOptOut")
        != Some(&zed::serde_json::Value::Bool(true))
    {
        return Err("native server lacks the virtual-document navigation opt-out required by Zed; install the Z4-compatible server".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use zed::serde_json::json;

    fn info() -> zed::serde_json::Value {
        json!({"serverVersion": "acore/0.1.0 (E7)", "protocolVersion": PROTOCOL,
               "compilerVersion": "a".repeat(64),
               "editorFeatures": {"virtualDocumentNavigationOptOut": true}})
    }

    fn validate(value: zed::serde_json::Value) -> zed::Result<()> {
        validate_version(Some(0), &zed::serde_json::to_vec(&value).unwrap())
    }

    #[test]
    fn compatible_protocol_accepts_different_compiler_builds() {
        assert!(validate(info()).is_ok());
        let mut next = info();
        next["compilerVersion"] = json!("b".repeat(64));
        next["serverVersion"] = json!("acore/0.2.0");
        assert!(validate(next).is_ok());
    }

    #[test]
    fn rejects_wrong_or_incompatible_binary_metadata() {
        for (key, value, message) in [
            ("serverVersion", json!("another-lsp/1.0"), "identify"),
            (
                "protocolVersion",
                json!("axiom-editor/v2"),
                "incompatible editor protocol",
            ),
            ("compilerVersion", json!("unknown"), "fingerprint"),
        ] {
            let mut metadata = info();
            metadata[key] = value;
            assert!(validate(metadata).unwrap_err().contains(message));
        }
        assert!(validate(json!(null)).is_err());
        assert!(validate_version(Some(0), b"not JSON").is_err());
        assert!(validate_version(Some(0), &vec![b' '; MAX_VERSION_BYTES + 1]).is_err());
        assert!(validate_version(Some(2), b"").is_err());
        assert!(validate_version(None, b"").is_err());
    }

    #[test]
    fn resolves_worktree_relative_paths_without_shell_expansion() {
        assert_eq!(
            absolute_command("bin/acore-lsp", "/project with spaces/"),
            "/project with spaces/bin/acore-lsp"
        );
        assert_eq!(
            absolute_command("/tools/acore-lsp", "/project"),
            "/tools/acore-lsp"
        );
        assert_eq!(
            absolute_command("bin\\acore-lsp.exe", "C:\\project"),
            "C:\\project\\bin\\acore-lsp.exe"
        );
        assert_eq!(
            absolute_command("C:\\tools\\acore-lsp.exe", "C:\\project"),
            "C:\\tools\\acore-lsp.exe"
        );
        assert_eq!(
            absolute_command("\\\\host\\tools\\acore-lsp.exe", "C:\\project"),
            "\\\\host\\tools\\acore-lsp.exe"
        );
        assert_eq!(
            absolute_command("literal;$(value)", "/project"),
            "/project/literal;$(value)"
        );
    }

    #[test]
    fn rejects_servers_that_cannot_suppress_unsafe_virtual_destinations() {
        for value in [json!(null), json!(false), json!("true")] {
            let mut metadata = info();
            metadata["editorFeatures"]["virtualDocumentNavigationOptOut"] = value;
            assert!(validate(metadata).unwrap_err().contains("Z4-compatible"));
        }
        let mut metadata = info();
        metadata.as_object_mut().unwrap().remove("editorFeatures");
        assert!(validate(metadata).is_err());
    }
}
