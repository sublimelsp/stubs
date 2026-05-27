import sublime
import sublime_plugin
import weakref
from ..protocol import PrepareRenameResult, Range as Range, WorkspaceEdit
from .core.edit import show_summary_message as show_summary_message
from .core.protocol import Request as Request
from .core.registry import (
    LspTextCommand as LspTextCommand,
    get_position as get_position,
)
from .core.sessions import Session as Session
from .core.views import (
    range_to_region as range_to_region,
    text_document_position_params as text_document_position_params,
)
from .edit import prompt_for_workspace_edits as prompt_for_workspace_edits
from typing_extensions import TypeGuard

PREPARE_RENAME_CAPABILITY: str

def is_range_response(result: PrepareRenameResult) -> TypeGuard[Range]: ...

class LspSymbolRenameCommand(LspTextCommand):
    capability: str
    def is_visible(
        self,
        new_name: str = "",
        placeholder: str = "",
        session_name: str | None = None,
        event: dict | None = None,
        point: int | None = None,
    ) -> bool: ...
    def input(self, args: dict) -> sublime_plugin.TextInputHandler | None: ...
    def run(
        self,
        edit: sublime.Edit,
        new_name: str = "",
        placeholder: str = "",
        session_name: str | None = None,
        event: dict | None = None,
        point: int | None = None,
    ) -> None: ...
    def on_prompt_for_workspace_edits_concluded(
        self,
        weak_session: weakref.ref[Session],
        response: WorkspaceEdit,
        accepted: bool,
    ) -> None: ...

class RenameSymbolInputHandler(sublime_plugin.TextInputHandler):
    def want_event(self) -> bool: ...
    view: sublime.View
    def __init__(self, view: sublime.View, placeholder: str) -> None: ...
    def name(self) -> str: ...
    def placeholder(self) -> str: ...
    def initial_text(self) -> str: ...
    def validate(self, name: str) -> bool: ...
