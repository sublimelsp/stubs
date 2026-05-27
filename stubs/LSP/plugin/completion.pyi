import sublime
from ..protocol import (
    CompletionItem,
    CompletionItemDefaults,
    CompletionParams as CompletionParams,
    EditRangeWithInsertReplace as EditRangeWithInsertReplace,
    InsertReplaceEdit,
    Range,
    TextEdit,
)
from .core.constants import (
    COMPLETION_KINDS as COMPLETION_KINDS,
    MarkdownLangMap as MarkdownLangMap,
)
from .core.edit import apply_text_edits as apply_text_edits
from .core.logging import debug as debug
from .core.promise import Promise as Promise
from .core.protocol import Error as Error, Request as Request
from .core.registry import LspTextCommand as LspTextCommand
from .core.sessions import Session as Session
from .core.settings import userprefs as userprefs
from .core.views import (
    FORMAT_MARKUP_CONTENT as FORMAT_MARKUP_CONTENT,
    FORMAT_STRING as FORMAT_STRING,
    html_wrapper as html_wrapper,
    minihtml as minihtml,
    range_to_region as range_to_region,
    show_lsp_popup as show_lsp_popup,
    text_document_position_params as text_document_position_params,
)
from typing import Any, Callable
from typing_extensions import TypeAlias, TypeGuard
from ..protocol import CompletionList
from typing import List
from typing import Tuple
from typing import Union
import weakref

SessionName: TypeAlias = str
CompletionResponse: TypeAlias = Union[List[CompletionItem], CompletionList, Error, None]
ResolvedCompletions: TypeAlias = Tuple[CompletionResponse, "weakref.ref[Session]"]
CompletionsStore: TypeAlias = Tuple[List[CompletionItem], CompletionItemDefaults]

def format_details(detail: str, cutoff_length: int = 80) -> str: ...
def format_completion(
    item: CompletionItem,
    index: int,
    can_resolve_completion_items: bool,
    session_name: str,
    item_defaults: CompletionItemDefaults,
    view_id: int,
) -> sublime.CompletionItem: ...
def get_text_edit_range(text_edit: TextEdit | InsertReplaceEdit) -> Range: ...
def is_range(val: Any) -> TypeGuard[Range]: ...
def is_edit_range(val: Any) -> TypeGuard[EditRangeWithInsertReplace]: ...
def completion_with_defaults(
    item: CompletionItem, item_defaults: CompletionItemDefaults
) -> CompletionItem:
    """Currently supports defaults for: ["editRange", "insertTextFormat", "data"]."""

class QueryCompletionsTask:
    """
    Represents pending completion requests.

    Can be canceled while in progress in which case the "on_done_async" callback will get immediately called with empty
    list and the pending response from the server(s) will be canceled and results ignored.

    All public methods must only be called on the async thread and the "on_done_async" callback will also be called
    on the async thread.
    """
    def __init__(
        self,
        view: sublime.View,
        location: int,
        triggered_manually: bool,
        on_done_async: Callable[
            [list[sublime.CompletionItem], sublime.AutoCompleteFlags], None
        ],
    ) -> None: ...
    def query_completions_async(self, sessions: list[Session]) -> None: ...
    def cancel_async(self) -> None: ...

class LspResolveDocsCommand(LspTextCommand):
    def run(
        self,
        edit: sublime.Edit,
        index: int,
        session_name: str,
        event: dict | None = None,
    ) -> None: ...

class LspCommitCompletionWithOppositeInsertMode(LspTextCommand):
    active: bool
    def run(self, edit: sublime.Edit, event: dict | None = None) -> None: ...

class LspSelectCompletionCommand(LspTextCommand):
    completions: dict[SessionName, CompletionsStore]
    def run(self, edit: sublime.Edit, index: int, session_name: str) -> None: ...
    def want_event(self) -> bool: ...
