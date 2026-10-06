use zed_extension_api as zed;

pub fn server_command(
    binary: Option<zed::settings::CommandSettings>,
    on_path: impl FnOnce() -> Option<String>,
    install: impl FnOnce() -> zed::Result<String>,
) -> zed::Result<zed::Command> {
    let binary = binary.unwrap_or(zed::settings::CommandSettings {
        path: None,
        arguments: None,
        env: None,
    });
    let command = binary
        .path
        .or_else(on_path)
        .map(Ok)
        .unwrap_or_else(install)?;
    if command.trim().is_empty() {
        return Err(
            "Acore binary.path must name an executable; an empty path cannot start the server"
                .into(),
        );
    }
    Ok(zed::Command {
        command,
        args: binary.arguments.unwrap_or_default(),
        env: binary.env.unwrap_or_default().into_iter().collect(),
    })
}

pub fn initialization_options(
    options: Option<zed::serde_json::Value>,
) -> zed::Result<zed::serde_json::Value> {
    let mut options = options.unwrap_or_else(|| zed::serde_json::json!({}));
    let object = options
        .as_object_mut()
        .ok_or("Acore initialization_options must be an object")?;
    // The host merges the original override after this hook. Reject unsafe
    // overrides rather than relying on replacing them in the returned object.
    if object
        .get("workspaceTrusted")
        .is_some_and(|value| value != false)
    {
        return Err("Acore in Zed uses read-only server mode. Remove initialization_options.workspaceTrusted or set it to false; use explicit CLI tasks for execution.".into());
    }
    if object
        .get("virtualDocumentNavigation")
        .is_some_and(|value| value != false)
    {
        return Err("Acore virtual documents cannot be opened safely by this Zed adapter. Remove initialization_options.virtualDocumentNavigation or set it to false; use hover and physical source navigation.".into());
    }
    object.insert(
        "virtualDocumentNavigation".into(),
        zed::serde_json::Value::Bool(false),
    );
    // Zed's public extension API has no worktree-trust accessor. Retain
    // the server's read-only mode; writes use explicit CLI tasks.
    object.insert(
        "workspaceTrusted".into(),
        zed::serde_json::Value::Bool(false),
    );
    Ok(options)
}

pub fn workspace_configuration(
    startup: Option<zed::serde_json::Value>,
    live: Option<zed::serde_json::Value>,
) -> zed::Result<zed::serde_json::Value> {
    let mut configuration = initialization_options(startup)?;
    let wrapped = live
        .as_ref()
        .is_some_and(|value| value.get("axiom").is_some());
    let live = live.map(|value| value.get("axiom").cloned().unwrap_or(value));
    let updates = initialization_options(live)
        .map_err(|error| error.replace("initialization_options", "settings"))?;
    merge(&mut configuration, updates);
    configuration
        .as_object_mut()
        .unwrap()
        .remove("workspaceTrusted");
    configuration
        .as_object_mut()
        .unwrap()
        .remove("virtualDocumentNavigation");
    // Keep the wrapper shape: Zed merges the original settings after this
    // hook, and the native server reads the wrapped value when it is present.
    Ok(if wrapped {
        zed::serde_json::json!({"axiom": configuration})
    } else {
        configuration
    })
}

fn merge(base: &mut zed::serde_json::Value, updates: zed::serde_json::Value) {
    match (base, updates) {
        (zed::serde_json::Value::Object(base), zed::serde_json::Value::Object(updates)) => {
            for (key, value) in updates {
                merge(
                    base.entry(key).or_insert(zed::serde_json::Value::Null),
                    value,
                );
            }
        }
        (base, value) => *base = value,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use zed::serde_json::json;

    #[test]
    fn explicit_command_preserves_arguments_and_environment_without_a_shell() {
        let binary = zed::settings::CommandSettings {
            path: Some("/tools with spaces/acore-lsp".into()),
            arguments: Some(vec!["literal;$(touch sentinel)".into()]),
            env: Some([("ACORE_TEST".into(), "value with spaces".into())].into()),
        };
        let command = server_command(
            Some(binary),
            || panic!("explicit path must win"),
            || panic!("explicit path must win"),
        )
        .unwrap();
        assert_eq!(command.command, "/tools with spaces/acore-lsp");
        assert_eq!(command.args, ["literal;$(touch sentinel)"]);
        assert_eq!(
            command.env,
            [("ACORE_TEST".into(), "value with spaces".into())]
        );
    }

    #[test]
    fn discovery_and_missing_or_empty_binary() {
        assert_eq!(
            server_command(
                None,
                || Some("/bin/acore-lsp".into()),
                || panic!("PATH must win")
            )
            .unwrap()
            .command,
            "/bin/acore-lsp"
        );
        assert!(
            server_command(None, || None, || Err("Set binary.path".into()))
                .unwrap_err()
                .contains("binary.path")
        );
        assert!(server_command(
            Some(zed::settings::CommandSettings {
                path: Some("  ".into()),
                arguments: None,
                env: None,
            }),
            || Some("/bin/acore-lsp".into()),
            || panic!("empty explicit path must fail")
        )
        .is_err());
    }

    #[test]
    fn automatic_selection_preserves_arguments_and_environment() {
        let command = server_command(
            Some(zed::settings::CommandSettings {
                path: None,
                arguments: Some(vec!["--stdio".into()]),
                env: Some([("EXTRACTOR".into(), "literal path".into())].into()),
            }),
            || None,
            || Ok("/verified/cache/acore-lsp".into()),
        )
        .unwrap();
        assert_eq!(command.command, "/verified/cache/acore-lsp");
        assert_eq!(command.args, ["--stdio"]);
        assert_eq!(command.env, [("EXTRACTOR".into(), "literal path".into())]);
    }

    #[test]
    fn initialization_preserves_project_options_and_cannot_grant_execution() {
        let options = initialization_options(Some(json!({
            "workspaceTrusted": false, "database": {"entry": "schema.acore"},
            "projects": {"file:///workspace/nested": {"entry": "main.acore"}}
        })))
        .unwrap();
        assert_eq!(options["workspaceTrusted"], false);
        assert_eq!(options["database"]["entry"], "schema.acore");
        assert_eq!(
            options["projects"]["file:///workspace/nested"]["entry"],
            "main.acore"
        );
        assert_eq!(
            initialization_options(None).unwrap(),
            json!({"workspaceTrusted": false, "virtualDocumentNavigation": false})
        );
        assert!(initialization_options(Some(json!([]))).is_err());
        for value in [json!(true), json!("true"), json!(null), json!(1)] {
            assert!(
                initialization_options(Some(json!({"workspaceTrusted": value})))
                    .unwrap_err()
                    .contains("read-only")
            );
        }
    }

    #[test]
    fn virtual_navigation_is_disabled_and_cannot_be_reenabled_by_host_merge() {
        assert_eq!(
            initialization_options(None).unwrap()["virtualDocumentNavigation"],
            false
        );
        for value in [json!(true), json!("false"), json!(null), json!(1)] {
            assert!(
                initialization_options(Some(json!({"virtualDocumentNavigation": value})))
                    .unwrap_err()
                    .contains("virtual documents")
            );
            assert!(workspace_configuration(
                None,
                Some(json!({"axiom": {"virtualDocumentNavigation": value}}))
            )
            .unwrap_err()
            .contains("settings"));
        }
        assert_eq!(
            workspace_configuration(None, Some(json!({"virtualDocumentNavigation": false})))
                .unwrap(),
            json!({})
        );
    }

    #[test]
    fn empty_live_settings_retain_database_and_frontend_entry_selections() {
        let startup = json!({
            "database": {"entry": "schema.acore"},
            "frontend": {"entry": "main.acore", "targets": ["web"]}
        });
        for live in [None, Some(json!({}))] {
            assert_eq!(
                workspace_configuration(Some(startup.clone()), live).unwrap(),
                startup
            );
        }
        assert_eq!(workspace_configuration(None, None).unwrap(), json!({}));
    }

    #[test]
    fn explicit_live_values_override_without_dropping_other_selections() {
        let startup = json!({
            "frontend": {"entry": "main.acore", "targets": ["web"], "profile": "dev"},
            "projects": {"file:///work/nested": {"entry": "nested.acore", "targets": ["web"]}}
        });
        let live = json!({
            "frontend": {"targets": ["desktop"], "profile": null},
            "projects": {"file:///work/nested": {"entry": "other.acore"}}
        });
        let expected = json!({
            "frontend": {"entry": "main.acore", "targets": ["desktop"], "profile": null},
            "projects": {"file:///work/nested": {"entry": "other.acore", "targets": ["web"]}}
        });
        assert_eq!(
            workspace_configuration(Some(startup.clone()), Some(live.clone())).unwrap(),
            expected
        );
        assert_eq!(
            workspace_configuration(Some(startup), Some(json!({"axiom": live}))).unwrap(),
            json!({"axiom": expected})
        );
        assert!(workspace_configuration(None, Some(json!([])))
            .unwrap_err()
            .contains("settings"));
        assert!(workspace_configuration(None, Some(json!({"workspaceTrusted": true}))).is_err());
    }
}
