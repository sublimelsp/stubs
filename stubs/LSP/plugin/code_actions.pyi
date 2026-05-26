import sublime
from ..protocol import CodeAction, CodeActionKind, CodeActionParams as CodeActionParams, Command, Diagnostic as Diagnostic
from .core.promise import Promise as Promise
from .core.protocol import Error as Error, Request as Request
from .core.registry import LspTextCommand as LspTextCommand, LspWindowCommand as LspWindowCommand, windows as windows
from .core.sessions import AbstractViewListener as AbstractViewListener, SessionBufferProtocol as SessionBufferProtocol
from .core.settings import userprefs as userprefs
from .core.views import entire_content_region as entire_content_region, first_selection_region as first_selection_region, format_code_actions_for_quick_panel as format_code_actions_for_quick_panel, kind_contains_other_kind as kind_contains_other_kind, text_document_code_action_params as text_document_code_action_params
from .lsp_task import LspTask as LspTask
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing_extensions import TypeGuard

ConfigName = str
CodeActionOrCommand = CodeAction | Command
CodeActionsByConfigName = tuple[ConfigName, list[CodeActionOrCommand]]
MENU_ACTIONS_KINDS: list[str | CodeActionKind]

def is_command(action: CodeActionOrCommand) -> TypeGuard[Command]: ...
def is_code_action_with_diagnostics(action: Command | CodeAction) -> TypeGuard[CodeAction]: ...
def is_quickfix(action: Command | CodeAction) -> bool: ...
def filter_quickfix_actions(only_with_diagnostics: bool, response: list[Command | CodeAction] | Error | None) -> list[Command | CodeAction]: ...

class CodeActionsManager:
    """Manager for per-location caching of code action responses."""
    menu_actions_cache_key: str | None
    refactor_actions_cache: list[tuple[str, CodeAction]]
    source_actions_cache: list[tuple[str, CodeAction]]
    def __init__(self) -> None: ...
    def request_for_region_async(self, view: sublime.View, region: sublime.Region, session_buffer_diagnostics: list[tuple[SessionBufferProtocol, list[Diagnostic]]], only_kinds: list[str | CodeActionKind] | None = None, manual: bool = False) -> Promise[list[CodeActionsByConfigName]]:
        """
        Requests code actions with provided diagnostics and specified region. If there are
        no diagnostics for given session, the request will be made with empty diagnostics list.
        """
    def request_on_save_or_format_async(self, view: sublime.View, code_actions: dict[str, bool]) -> Generator[Promise[CodeActionsByConfigName]]: ...

actions_manager: CodeActionsManager

def get_session_kinds(sb: SessionBufferProtocol) -> list[CodeActionKind]: ...
def get_matching_kinds(code_actions: dict[str, bool], session_kinds: list[CodeActionKind]) -> list[CodeActionKind]:
    """
    Filters user-enabled or disabled actions so that only ones matching the session kinds
    are returned. Returned kinds are those that are enabled and are not overridden by more
    specific, disabled kinds.

    Filtering only returns kinds that exactly match the ones supported by given session.
    If user has enabled a generic action that matches more specific session action
    (for example user's a.b matching session's a.b.c), then the more specific (a.b.c) must be
    returned as servers must receive only kinds that they advertise support for.
    """

class CodeActionsTaskBase(LspTask):
    """The base task that requests code actions from sessions and runs them."""
    SETTING_NAME: str
    @classmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...
    @classmethod
    def format_on_save_enabled(cls, view: sublime.View) -> bool: ...
    @classmethod
    def get_code_action_kinds(cls, view: sublime.View) -> dict[str, bool]: ...
    def run_async(self) -> None: ...

class CodeActionsOnSaveTask(CodeActionsTaskBase):
    """
    Request code actions from sessions before save and run them.

    The amount of time the task is allowed to run is defined by user-controlled setting. If the task
    runs longer, the native save will be triggered before waiting for results.
    """
    SETTING_NAME: str
    @classmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...

class CodeActionsOnFormatTask(CodeActionsTaskBase):
    """Run code actions on format."""
    SETTING_NAME: str

class CodeActionsOnFormatOnSaveTask(CodeActionsOnFormatTask):
    """
    Run code actions on format when format_on_save is enabled.

    Code actions enabled in either 'lsp_code_actions_on_save' or 'lsp_code_actions_on_format' will be run.
    """
    @classmethod
    def get_code_action_kinds(cls, view: sublime.View) -> dict[str, bool]: ...
    @classmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...

class LspCodeActionsCommand(LspTextCommand):
    capability: str
    def is_visible(self, event: dict | None = None, point: int | None = None, only_kinds: list[str | CodeActionKind] | None = None) -> bool: ...
    def run(self, edit: sublime.Edit, event: dict | None = None, only_kinds: list[str | CodeActionKind] | None = None, code_actions_by_config: list[CodeActionsByConfigName] | None = None) -> None: ...

class LspMenuActionCommand(LspWindowCommand, ABC):
    """Handles a particular kind of code actions with the purpose to list them as items in a submenu."""
    capability: str
    @property
    @abstractmethod
    def actions_cache(self) -> list[tuple[str, CodeAction]]: ...
    @property
    def view(self) -> sublime.View | None: ...
    def is_enabled(self, index: int, event: dict | None = None) -> bool: ...
    def is_visible(self, index: int, event: dict | None = None) -> bool: ...
    def description(self, index: int, event: dict | None = None) -> str | None: ...
    def want_event(self) -> bool: ...
    def run(self, index: int, event: dict | None = None) -> None: ...
    def run_async(self, index: int, event: dict | None) -> None: ...
    @staticmethod
    def applies_to_context_menu(event: dict | None) -> bool: ...

class LspRefactorCommand(LspMenuActionCommand):
    @property
    def actions_cache(self) -> list[tuple[str, CodeAction]]: ...

class LspSourceActionCommand(LspMenuActionCommand):
    @property
    def actions_cache(self) -> list[tuple[str, CodeAction]]: ...
