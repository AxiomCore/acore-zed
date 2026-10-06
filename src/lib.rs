use zed_extension_api as zed;
mod installer;
mod server;
mod settings;

struct AcoreExtension;

impl zed::Extension for AcoreExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<zed::Command> {
        let settings = zed::settings::LspSettings::for_worktree("acore-lsp", worktree)?;
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
        let settings = zed::settings::LspSettings::for_worktree("acore-lsp", worktree)?;
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
        _id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<Option<zed::serde_json::Value>> {
        let settings = zed::settings::LspSettings::for_worktree("acore-lsp", worktree)?;
        // Zed sends an empty live configuration immediately after initialize.
        // The native server replaces its editor settings with that payload.
        // Retain startup selections, with explicit live values taking priority.
        settings::workspace_configuration(settings.initialization_options, settings.settings)
            .map(Some)
    }
}

zed::register_extension!(AcoreExtension);
