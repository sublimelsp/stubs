import sublime
from .types import (
    PANEL_FILE_REGEX as PANEL_FILE_REGEX,
    PANEL_LINE_REGEX as PANEL_LINE_REGEX,
)
from typing import Iterable
from typing import Literal
from typing import Optional
from typing import Tuple

LOG_LINES_LIMIT_SETTING_NAME: str
MAX_LOG_LINES_LIMIT_ON: int
MAX_LOG_LINES_LIMIT_OFF: int
OUTPUT_PANEL_SETTINGS: dict
PanelButton = Tuple[str, str, Optional[Literal["primary", "secondary"]]]
BUTTONS_TEMPLATE: str

def buttons_html(buttons: Iterable[PanelButton]) -> str:
    """
    Render a row of buttons for a phantom in an output panel.

    Each button is given as a tuple of the link target, the label and an optional style, which is either `primary` for
    a highlighted button or `secondary` for a less prominent one.
    """

class PanelName:
    Diagnostics: str
    References: str
    WorkspaceEdit: str
    Log: str
    Messages: str

class PanelManager:
    def __init__(self, window: sublime.Window) -> None: ...
    def destroy_output_panels(self) -> None: ...
    def toggle_output_panel(self, panel_type: str) -> None: ...
    def is_panel_open(self, panel_name: str) -> bool: ...
    def update_log_panel(self, scroll_to_selection: bool = False) -> None: ...
    def ensure_panel(
        self,
        name: str,
        result_file_regex: str,
        result_line_regex: str,
        syntax: str,
        context_menu: str | None = None,
    ) -> sublime.View | None: ...
    def ensure_diagnostics_panel(self) -> sublime.View | None: ...
    def ensure_log_panel(self) -> sublime.View | None: ...
    def ensure_messages_panel(self) -> sublime.View | None: ...
    def ensure_references_panel(self) -> sublime.View | None: ...
    def ensure_workspace_edit_panel(self) -> sublime.View | None: ...
    def get_panel(self, panel_name: str) -> sublime.View | None: ...
    def create_output_panel(self, name: str) -> sublime.View | None: ...
    def show_diagnostics_panel_async(self) -> None: ...
    def hide_diagnostics_panel_async(self) -> None: ...
    def update_workspace_edit_panel_buttons(
        self, phantoms: Iterable[sublime.Phantom]
    ) -> None: ...
