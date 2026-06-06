import sublime
from .logging import exception_log as exception_log, printf as printf
from .types import ClientConfig as ClientConfig
from .url import parse_uri as parse_uri
from .workspace import (
    WorkspaceFolder as WorkspaceFolder,
    disable_in_project as disable_in_project,
    enable_in_project as enable_in_project,
)
from abc import ABC, abstractmethod
from typing import Generator
from datetime import timedelta
from typing import Literal

RETRY_MAX_COUNT: int
RETRY_COUNT_TIMEDELTA: timedelta
ConfigChangeType = Literal[
    "added", "removed", "root_changed", "settings_changed", "unchanged"
]

class WindowConfigChangeListener(ABC):
    @abstractmethod
    def on_configs_changed(self, configs: list[ClientConfig]) -> None: ...
    @abstractmethod
    def on_server_settings_changed(self, configs: list[ClientConfig]) -> None: ...

class WindowConfigManager:
    all: dict[str, ClientConfig]
    def __init__(
        self, window: sublime.Window, global_configs: dict[str, ClientConfig]
    ) -> None: ...
    def add_change_listener(self, listener: WindowConfigChangeListener) -> None: ...
    def get_config(self, config_name: str) -> ClientConfig | None: ...
    def get_configs(self) -> list[ClientConfig]: ...
    def match_view(
        self, view: sublime.View, workspace_folders: list[WorkspaceFolder]
    ) -> Generator[ClientConfig]:
        """
        Yields matching configuration.

        Matches if:
        - the configuration\'s "selector" matches with the view\'s base scope, and
        - the view\'s URI scheme is an element of the configuration\'s "schemes".
        """
    def update(self, updated_config_name: str | None = None) -> None: ...
    def enable_config(self, config_name: str) -> None: ...
    def disable_config(
        self, config_name: str, only_for_session: bool = False
    ) -> None: ...
    def record_crash(
        self, config_name: str, exit_code: int, exception: Exception | None
    ) -> bool:
        """
        Signal that a session has crashed.

        Returns True if the session should be restarted automatically.
        """
