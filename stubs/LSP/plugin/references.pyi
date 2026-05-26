import sublime
from ..protocol import Location as Location
from .core.constants import RegionKey as RegionKey
from .core.protocol import Point as Point, Request as Request
from .core.registry import LspTextCommand as LspTextCommand, get_position as get_position, windows as windows
from .core.sessions import Session as Session
from .core.settings import userprefs as userprefs
from .core.types import ClientConfig as ClientConfig
from .core.views import get_line as get_line, get_symbol_kind_from_scope as get_symbol_kind_from_scope, get_uri_and_position_from_location as get_uri_and_position_from_location, position_to_offset as position_to_offset, text_document_position_params as text_document_position_params
from .locationpicker import LocationPicker as LocationPicker
from typing import Literal

OutputMode = Literal['output_panel', 'quick_panel']

class LspSymbolReferencesCommand(LspTextCommand):
    capability: str
    def is_enabled(self, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1, include_declaration: bool = False, output_mode: OutputMode | None = None) -> bool: ...
    def is_visible(self, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1, include_declaration: bool = False, output_mode: OutputMode | None = None) -> bool: ...
    def run(self, _: sublime.Edit, event: dict | None = None, point: int | None = None, side_by_side: bool = False, force_group: bool = True, fallback: bool = False, group: int = -1, include_declaration: bool = False, output_mode: OutputMode | None = None) -> None: ...
