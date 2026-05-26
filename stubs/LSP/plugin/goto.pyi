import sublime
import sublime_plugin
from ..protocol import Diagnostic, DocumentUri, LocationLink as LocationLink
from .core.constants import DIAGNOSTIC_KINDS as DIAGNOSTIC_KINDS
from .core.input_handlers import PreselectedListInputHandler as PreselectedListInputHandler
from .core.paths import simple_project_path as simple_project_path
from .core.protocol import Point as Point, Request as Request
from .core.registry import LspTextCommand as LspTextCommand, LspWindowCommand as LspWindowCommand, get_position as get_position
from .core.sessions import Session as Session
from .core.settings import userprefs as userprefs
from .core.types import method_to_capability as method_to_capability
from .core.url import parse_uri as parse_uri
from .core.views import diagnostic_severity as diagnostic_severity, first_selection_region as first_selection_region, get_symbol_kind_from_scope as get_symbol_kind_from_scope, position_to_offset as position_to_offset, range_to_region as range_to_region, text_document_position_params as text_document_position_params, to_encoded_filename as to_encoded_filename, uri_from_view as uri_from_view
from .locationpicker import LocationPicker as LocationPicker, open_location_async as open_location_async
from typing import Any, TypedDict

class LspGotoCommand(LspTextCommand):
    method: str
    placeholder_text: str
    fallback_command: str
    def is_enabled(self, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1) -> bool: ...
    def is_visible(self, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1) -> bool: ...
    def run(self, _: sublime.Edit, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1) -> None: ...

class LspSymbolDefinitionCommand(LspGotoCommand):
    method: str
    capability: str
    placeholder_text: str
    fallback_command: str

class LspSymbolTypeDefinitionCommand(LspGotoCommand):
    method: str
    capability: str
    placeholder_text: str

class LspSymbolDeclarationCommand(LspGotoCommand):
    method: str
    capability: str
    placeholder_text: str

class LspSymbolImplementationCommand(LspGotoCommand):
    method: str
    capability: str
    placeholder_text: str

class DiagnosticData(TypedDict):
    session_name: str
    diagnostic: Diagnostic

class LspGotoDiagnosticCommand(LspWindowCommand):
    def run(self, uri: DocumentUri | None, diagnostic: DiagnosticData | None, severity_level: int | None = None) -> None: ...
    def is_enabled(self, **kwargs: dict[str, Any]) -> bool: ...
    def input_description(self) -> str: ...
    def input(self, args: dict[str, Any]) -> sublime_plugin.CommandInputHandler | None: ...

class DiagnosticUriInputHandler(PreselectedListInputHandler):
    window: sublime.Window
    initial_view: sublime.View
    sessions: list[Session]
    uri: DocumentUri | None
    def __init__(self, window: sublime.Window, initial_view: sublime.View, sessions: list[Session], max_severity: int, initial_value: DocumentUri | None = None) -> None: ...
    def name(self) -> str: ...
    def placeholder(self) -> str: ...
    def get_list_items(self) -> tuple[list[sublime.ListInputItem], int]: ...
    def preview(self, value: DocumentUri | None) -> str: ...
    def cancel(self) -> None: ...
    def confirm(self, value: DocumentUri | None) -> None: ...
    def next_input(self, args: dict) -> sublime_plugin.CommandInputHandler | None: ...
    def description(self, value: DocumentUri, text: str) -> str: ...

class DiagnosticInputHandler(sublime_plugin.ListInputHandler):
    window: sublime.Window
    initial_view: sublime.View
    sessions: list[Session]
    uri: DocumentUri
    diagnostics: list[DiagnosticData]
    def __init__(self, window: sublime.Window, initial_view: sublime.View, _preview: sublime.View | None, sessions: list[Session], uri: DocumentUri, diagnostics: list[DiagnosticData]) -> None: ...
    def name(self) -> str: ...
    def list_items(self) -> tuple[list[sublime.ListInputItem], int]: ...
    def preview(self, value: DiagnosticData | None) -> str | sublime.Html: ...
    def cancel(self) -> None: ...
    def confirm(self, value: DiagnosticData | None) -> None: ...
