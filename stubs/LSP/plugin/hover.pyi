import sublime
import sublime_plugin
from ..protocol import (
    CodeAction as CodeAction,
    Command as Command,
    Diagnostic as Diagnostic,
    Hover as Hover,
    TextDocumentPositionParams as TextDocumentPositionParams,
)
from .code_actions import filter_quickfix_actions as filter_quickfix_actions
from .core.aio import run_coroutine as run_coroutine
from .core.constants import (
    HOVER_ENABLED_KEY as HOVER_ENABLED_KEY,
    MarkdownLangMap as MarkdownLangMap,
    RegionKey as RegionKey,
    SHOW_DEFINITIONS_KEY as SHOW_DEFINITIONS_KEY,
)
from .core.open import (
    lsp_range_from_uri_fragment as lsp_range_from_uri_fragment,
    open_file_uri as open_file_uri,
    open_in_browser as open_in_browser,
)
from .core.protocol import Error as Error, Request as Request
from .core.registry import (
    LspTextCommand as LspTextCommand,
    LspWindowCommand as LspWindowCommand,
    get_position as get_position,
    windows as windows,
)
from .core.sessions import (
    AbstractViewListener as AbstractViewListener,
    Session as Session,
    SessionBufferProtocol as SessionBufferProtocol,
)
from .core.settings import userprefs as userprefs
from .core.type_converters import range_to_region as range_to_region
from .core.url import (
    CODE_ACTION_SCHEME as CODE_ACTION_SCHEME,
    DOCUMENT_LINK_SCHEME as DOCUMENT_LINK_SCHEME,
    decode_code_action_uri as decode_code_action_uri,
    decode_document_link_uri as decode_document_link_uri,
    encode_document_link_uri as encode_document_link_uri,
    parse_uri as parse_uri,
)
from .core.views import (
    FORMAT_MARKED_STRING as FORMAT_MARKED_STRING,
    FORMAT_MARKUP_CONTENT as FORMAT_MARKUP_CONTENT,
    format_diagnostics_for_html as format_diagnostics_for_html,
    html_wrapper as html_wrapper,
    is_location_href as is_location_href,
    make_command_link as make_command_link,
    minihtml as minihtml,
    show_lsp_popup as show_lsp_popup,
    text_document_identifier as text_document_identifier,
    text_document_position_params as text_document_position_params,
    unpack_href_location as unpack_href_location,
    update_lsp_popup as update_lsp_popup,
)

SessionName = str

class LinkKind:
    lsp_name: str
    label: str
    subl_cmd_name: str
    supports_side_by_side: bool
    def __init__(
        self, lsp_name: str, label: str, subl_cmd_name: str, supports_side_by_side: bool
    ) -> None: ...
    def link(self, point: int, view: sublime.View) -> str: ...

link_kinds: list[LinkKind]

class LspHoverCommand(LspTextCommand):
    def __init__(self, view: sublime.View) -> None: ...
    async def run(
        self,
        only_diagnostics: bool = False,
        point: int | None = None,
        event: dict | None = None,
    ) -> None: ...
    async def request_symbol_hover(
        self, listener: AbstractViewListener, point: int
    ) -> None: ...
    async def request_document_link(
        self, listener: AbstractViewListener, point: int
    ) -> None: ...
    async def show_diagnostics_and_request_code_actions(
        self, listener: AbstractViewListener, point: int, only_diagnostics: bool
    ) -> None: ...
    def provider_exists(
        self, listener: AbstractViewListener, link: LinkKind
    ) -> bool: ...
    def symbol_actions_content(
        self, listener: AbstractViewListener, point: int
    ) -> str: ...
    def link_content_and_range(self) -> tuple[str, sublime.Region | None]: ...
    def hover_content(self) -> str: ...
    def hover_range(self) -> sublime.Region | None: ...
    def show_hover(
        self, listener: AbstractViewListener, point: int, only_diagnostics: bool
    ) -> None: ...
    async def try_open_custom_uri(self, uri: str) -> None: ...

class LspToggleHoverPopupsCommand(LspWindowCommand):
    def is_enabled(self) -> bool: ...
    def is_checked(self) -> bool: ...
    async def run(self) -> None: ...

class LspCopyTextCommand(sublime_plugin.WindowCommand):
    def run(self, text: str) -> None: ...
