import sublime_plugin
from .core.registry import windows as windows
from .core.settings import client_configs as client_configs
from .core.windows import WindowManager as WindowManager

class LspEnableLanguageServerGloballyCommand(sublime_plugin.WindowCommand):
    def run(self) -> None: ...

class LspEnableLanguageServerInProjectCommand(sublime_plugin.WindowCommand):
    def run(self) -> None: ...

class LspDisableLanguageServerGloballyCommand(sublime_plugin.WindowCommand):
    def run(self) -> None: ...

class LspDisableLanguageServerInProjectCommand(sublime_plugin.WindowCommand):
    def run(self) -> None: ...
