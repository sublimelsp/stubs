import re
import sublime
import sublime_plugin
from ..protocol import AnnotatedTextEdit, SnippetTextEdit, TextEdit, WorkspaceEdit
from .core.constants import ChangeEventAction as ChangeEventAction
from .core.edit import WorkspaceChanges as WorkspaceChanges, is_snippet_text_edit as is_snippet_text_edit, parse_lsp_position as parse_lsp_position, parse_workspace_edit as parse_workspace_edit
from .core.logging import debug as debug
from .core.panels import PanelName as PanelName
from .core.promise import Promise as Promise
from .core.registry import LspWindowCommand as LspWindowCommand, windows as windows
from .core.sessions import Session as Session
from .core.url import parse_uri as parse_uri
from .core.views import get_line as get_line
from .core.windows import WindowManager as WindowManager
from typing import Any, Callable, Generator

TextEditTuple = tuple[tuple[int, int], tuple[int, int], str]
g_workspace_edit_panel_resolvers: dict[int, Callable[[bool], None]]
ROWCOL_PREFIX: str
BUTTONS_TEMPLATE: str

def temporary_setting(settings: sublime.Settings, key: str, val: Any) -> Generator[None, None, None]: ...

class LspApplyWorkspaceEditCommand(LspWindowCommand):
    def run(self, session_name: str, edit: WorkspaceEdit, label: str | None = None, is_refactoring: bool = False) -> None: ...

class LspApplyTextDocumentEditCommand(sublime_plugin.TextCommand):
    def description(self, **kwargs: dict[str, Any]) -> str | None: ...
    def run(self, edit: sublime.Edit, edits: list[TextEdit | AnnotatedTextEdit | SnippetTextEdit], label: str | None = None) -> None: ...

class LspApplyDocumentEditCommand(sublime_plugin.TextCommand):
    re_placeholder: re.Pattern[str]
    def description(self, **kwargs: dict[str, Any]) -> str | None: ...
    def run(self, edit: sublime.Edit, changes: list[TextEdit], label: str | None = None, required_view_version: int | None = None, process_placeholders: bool = False) -> None: ...
    def apply_change(self, region: sublime.Region, replacement: str, edit: sublime.Edit) -> None: ...
    def parse_snippet(self, replacement: str) -> tuple[str, tuple[int, int]] | None: ...

def prompt_for_workspace_edits(session: Session, response: WorkspaceEdit, label: str) -> Promise[bool]: ...
def utf16_to_code_points(s: str, col: int) -> int:
    """Convert a position from UTF-16 code units to Unicode code points, usable for string slicing."""

class LspConcludeWorkspaceEditPanelCommand(sublime_plugin.WindowCommand):
    def run(self, window_id: int, accept: bool) -> None: ...
