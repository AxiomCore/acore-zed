use zed_extension_api as zed;
mod installer;
mod server;
mod settings;

struct AcoreExtension;

const SERVER_ID: &str = "acore-lsp";

fn require_language_server(id: &str) -> zed::Result<()> {
    if id == SERVER_ID {
        Ok(())
    } else {
        Err(format!("Unknown language server: {id}"))
    }
}

impl zed::Extension for AcoreExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<zed::Command> {
        require_language_server(id.as_ref())?;
        let settings = zed::settings::LspSettings::for_worktree(SERVER_ID, worktree)?;
        settings::server_command(
            settings.binary,
            || worktree.which("acore-lsp"),
            || installer::install(id),
        )
    }

    fn language_server_initialization_options(
        &mut self,
        id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<Option<zed::serde_json::Value>> {
        require_language_server(id.as_ref())?;
        let settings = zed::settings::LspSettings::for_worktree(SERVER_ID, worktree)?;
        let options = settings::initialization_options(settings.initialization_options)?;
        // Zed launches an explicit binary override without calling our command
        // hook. Validate here so both override and PATH launches are covered.
        let mut command = settings::server_command(
            settings.binary,
            || worktree.which("acore-lsp"),
            || installer::install(id),
        )?;
        command.command = server::absolute_command(&command.command, &worktree.root_path());
        server::check_compatible(&command, worktree.shell_env())?;
        Ok(Some(options))
    }

    fn language_server_workspace_configuration(
        &mut self,
        id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<Option<zed::serde_json::Value>> {
        require_language_server(id.as_ref())?;
        let settings = zed::settings::LspSettings::for_worktree(SERVER_ID, worktree)?;
        // Zed sends an empty live configuration immediately after initialize.
        // The native server replaces its editor settings with that payload.
        // Retain startup selections, with explicit live values taking priority.
        settings::workspace_configuration(settings.initialization_options, settings.settings)
            .map(Some)
    }
}

zed::register_extension!(AcoreExtension);

#[cfg(test)]
mod tests {
    use super::require_language_server;

    #[test]
    fn only_declared_language_server_can_read_settings_or_launch() {
        assert!(require_language_server("acore-lsp").is_ok());
        for id in ["", "acore", "another-lsp", "ACORE-LSP"] {
            assert_eq!(
                require_language_server(id).unwrap_err(),
                format!("Unknown language server: {id}")
            );
        }
    }
}
