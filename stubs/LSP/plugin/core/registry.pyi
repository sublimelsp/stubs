import sublime
import sublime_plugin
from ...protocol import Diagnostic as Diagnostic, Location, LocationLink
from .aio import run_coroutine as run_coroutine
from .panels import show_quick_panel as show_quick_panel
from .sessions import AbstractViewListener as AbstractViewListener, Session as Session
from .settings import userprefs as userprefs
from .type_converters import position_to_offset as position_to_offset
from .views import (
    MissingUriError as MissingUriError,
    first_selection_region as first_selection_region,
    get_uri_and_position_from_location as get_uri_and_position_from_location,
    uri_from_view as uri_from_view,
)
from .windows import WindowManager as WindowManager, WindowRegistry as WindowRegistry
from typing import Any, Generator, Iterable

windows: WindowRegistry

def best_session(
    view: sublime.View, sessions: Iterable[Session], point: int | None = None
) -> Session | None: ...
def get_position(
    view: sublime.View, event: dict | None = None, point: int | None = None
) -> int | None: ...

class AsyncCommandMixin: ...

class LspWindowCommand(sublime_plugin.WindowCommand, AsyncCommandMixin):
    """
    Inherit from this class to define requests which are not bound to a particular view. This allows to run requests
    for example from links in HtmlSheets or when an unrelated file has focus.

    A derived class may define its `run` method in one of two ways:

    - As a blocking `def run(self, **kwargs)`. It runs on the main thread, just like a regular
      `sublime_plugin.WindowCommand`.
    - As a coroutine `async def run(self, **kwargs)`. It runs on the asyncio thread. Use this when the command needs to
      await requests to a language server.
    """

    capability: str
    session_name: str
    def __init__(self, window: sublime.Window) -> None: ...
    def run_(self, edit_token: int, args: dict[str, Any] | None) -> None: ...
    def is_enabled(self) -> bool: ...
    def session(self) -> Session | None: ...
    def sessions(self) -> Generator[Session]: ...
    def session_by_name(self, session_name: str) -> Session | None: ...
    def manager(self) -> WindowManager | None: ...

class LspTextCommand(sublime_plugin.TextCommand, AsyncCommandMixin):
    """
    Inherit from this class to define your requests that should be triggered via the command palette and/or a
    keybinding.

    A derived class may define its `run` method in one of two ways:

    - As a blocking `def run(self, edit, **kwargs)`. It runs on the main thread and receives an edit token, just like
      a regular `sublime_plugin.TextCommand`. Use this when the command needs to modify the buffer directly.
    - As a coroutine `async def run(self, **kwargs)`. It runs on the asyncio thread and does not receive an edit
      token, because the token would no longer be valid by the time the coroutine runs. Use this when the command
      needs to await requests to a language server.
    """

    capability: str
    session_name: str
    def __init_subclass__(cls, **kwargs: Any) -> None: ...
    def __init__(self, view: sublime.View) -> None: ...
    def run_(self, edit_token: int, args: dict[str, Any] | None) -> None: ...
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def want_event(self) -> bool: ...
    @staticmethod
    def applies_to_context_menu(event: dict | None) -> bool: ...
    def get_listener(self) -> AbstractViewListener | None: ...
    def best_session(
        self, capability: str, point: int | None = None
    ) -> Session | None: ...
    def session_by_name(
        self, name: str | None = None, capability_path: str | None = None
    ) -> Session | None: ...
    def sessions(
        self, capability_path: str | None = None
    ) -> Generator[Session, None, None]: ...

class LspOpenLocationCommand(LspWindowCommand):
    """A command to be used by third-party ST packages that need to open an URI with some abstract scheme."""
    async def run(
        self,
        location: Location | LocationLink,
        session_name: str | None = None,
        flags: sublime.NewFileFlags = ...,
        group: int = -1,
        event: dict | None = None,
    ) -> None: ...
    def want_event(self) -> bool: ...

class LspRestartServerCommand(LspTextCommand):
    async def run(self, config_name: str | None = None) -> None: ...
    def want_event(self) -> bool: ...

class LspCheckApplicableCommand(LspTextCommand):
    async def run(self, session_name: str) -> None: ...
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def want_event(self) -> bool: ...

def navigate_diagnostics(
    view: sublime.View,
    point: int | None,
    severity_level: int | None,
    *,
    forward: bool = True,
) -> None: ...

class LspNextDiagnosticCommand(LspTextCommand):
    def run(
        self,
        edit: sublime.Edit,
        point: int | None = None,
        severity_level: int | None = None,
    ) -> None: ...
    def want_event(self) -> bool: ...

class LspPrevDiagnosticCommand(LspTextCommand):
    def run(
        self,
        edit: sublime.Edit,
        point: int | None = None,
        severity_level: int | None = None,
    ) -> None: ...
    def want_event(self) -> bool: ...
