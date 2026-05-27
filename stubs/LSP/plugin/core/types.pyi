import sublime
from ...protocol import (
    DocumentSelector,
    DocumentUri,
    FileOperationFilter,
    ServerCapabilities,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
    URI,
)
from .collections import DottedDict as DottedDict
from .constants import (
    LANGUAGE_IDENTIFIERS as LANGUAGE_IDENTIFIERS,
    MarkdownLangMap as MarkdownLangMap,
)
from .file_watcher import FileWatcherEventType as FileWatcherEventType
from .logging import debug as debug, set_debug_logging as set_debug_logging
from .transports import (
    StdioTransportConfig as StdioTransportConfig,
    TcpClientTransportConfig as TcpClientTransportConfig,
    TcpServerTransportConfig as TcpServerTransportConfig,
    TransportConfig as TransportConfig,
)
from .url import filename_to_uri as filename_to_uri, parse_uri as parse_uri
from .workspace import WorkspaceFolder as WorkspaceFolder
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generator, Iterable, TypeVar, TypedDict
from typing_extensions import NotRequired
from typing import List
from typing_extensions import override
import os
import time

FEATURES_TIMEOUT: int
PANEL_FILE_REGEX: str
PANEL_LINE_REGEX: str
MarkdownLangMapJson = dict[str, list[list[str]]]

class FileWatcherConfig(TypedDict):
    patterns: list[str]
    events: NotRequired[list[FileWatcherEventType]]
    ignores: NotRequired[list[str]]

class ViewStatusHandler(ABC):
    @abstractmethod
    def on_view_status_changed(
        self, config_name: str, view: sublime.View, status: str | None
    ) -> None: ...

def basescope2languageid(base_scope: str) -> str: ...
def runtime(token: str) -> Generator[None, None, None]: ...

T = TypeVar("T")

def diff(old: Iterable[T], new: Iterable[T]) -> tuple[set[T], set[T]]:
    """Return a tuple of (added, removed) items."""

def matches_pattern(path: str, patterns: Any) -> bool: ...
def sublime_pattern_to_glob(
    pattern: str, *, is_directory_pattern: bool, root_path: str | None = None
) -> str:
    """
    Convert a Sublime Text pattern (http://www.sublimetext.com/docs/file_patterns.html)
    to a glob pattern that utilizes globstar extension.
    """

def debounced(
    f: Callable[[], Any],
    timeout_ms: int = 0,
    condition: Callable[[], bool] = ...,
    async_thread: bool = False,
) -> None:
    """
    Possibly run a function at a later point in time, either on the async thread or on the main thread.

    :param      f:             The function to possibly run. Its return type is discarded.
    :param      timeout_ms:    The time in milliseconds after which to possibly to run the function
    :param      condition:     The condition that must evaluate to True in order to run the function
    :param      async_thread:  If true, run the function on the async worker thread, otherwise run the function on the
                               main thread
    """

class SettingsRegistration:
    settings: sublime.Settings
    settings_path: str
    def __init__(
        self,
        settings: sublime.Settings,
        settings_path: str,
        on_change: Callable[[SettingsRegistration], None],
    ) -> None: ...
    def __del__(self) -> None: ...

class DebouncerNonThreadSafe:
    """
    Debouncer for delaying execution of a function until specified timeout time.

    When calling `debounce()` multiple times, if the time span between calls is shorter than the specified `timeout_ms`,
    the callback function will only be called once, after `timeout_ms` since the last call.

    This implementation is not thread safe. You must ensure that `debounce()` is called from the same thread as
    was chosen during initialization through the `async_thread` argument.
    """
    def __init__(self, async_thread: bool) -> None: ...
    def debounce(
        self,
        f: Callable[[], None],
        timeout_ms: int = 0,
        condition: Callable[[], bool] = ...,
    ) -> None:
        """
        Possibly run a function at a later point in time on the thread chosen during initialization.

        :param      f:             The function to possibly run
        :param      timeout_ms:    The time in milliseconds after which to possibly to run the function
        :param      condition:     The condition that must evaluate to True in order to run the function
        """
    def cancel_pending(self) -> None: ...

def read_dict_setting(
    settings_obj: sublime.Settings, key: str, default: dict
) -> dict: ...
def read_list_setting(
    settings_obj: sublime.Settings, key: str, default: list
) -> list: ...

class Settings:
    completion_insert_mode: str
    diagnostics_additional_delay_auto_complete_ms: int
    diagnostics_delay_ms: int
    diagnostics_gutter_marker: str
    diagnostics_highlight_style: str | dict[str, str]
    diagnostics_panel_include_severity_level: int
    disabled_capabilities: list[str]
    document_highlight_style: str
    format_on_type: bool
    hover_highlight_style: str
    inhibit_snippet_completions: bool
    inhibit_word_completions: bool
    initially_folded: list[str]
    inlay_hints_max_length: int
    link_highlight_style: str
    log_debug: bool
    log_max_size: int
    log_server: list[str]
    lsp_code_actions_on_format: dict[str, bool]
    lsp_code_actions_on_save: dict[str, bool]
    lsp_format_on_paste: bool
    lsp_format_on_save: bool
    on_save_task_timeout_ms: int
    only_show_lsp_completions: bool
    popup_max_characters_height: int
    popup_max_characters_width: int
    refactoring_auto_save: str
    semantic_highlighting: bool
    show_code_actions: str
    show_code_actions_in_hover: bool
    show_code_lens: str
    show_diagnostics_annotations_severity_level: int
    show_diagnostics_count_in_view_status: bool
    show_diagnostics_in_hover: bool
    show_diagnostics_in_view_status: bool
    show_diagnostics_panel_on_save: int
    show_diagnostics_severity_level: int
    show_inlay_hints: bool
    show_multiline_diagnostics_highlights: bool
    show_multiline_document_highlights: bool
    show_references_in_quick_panel: bool
    show_signature_help: bool
    show_symbol_action_links: bool
    show_view_status: bool
    def __init__(self, s: sublime.Settings) -> None: ...
    def update(self, s: sublime.Settings) -> None: ...
    def highlight_style_region_flags(
        self, style_str: str
    ) -> tuple[sublime.RegionFlags, sublime.RegionFlags]: ...
    def diagnostics_highlight_style_flags(self) -> list[sublime.RegionFlags | None]:
        """Returns flags for highlighting diagnostics on single lines per severity."""

@dataclass
class SemanticToken:
    region: sublime.Region
    type: str
    modifiers: list[str]

class ClientStates:
    STARTING: int
    READY: int
    STOPPING: int

class DocumentFilterMatcher:
    """
    A document filter denotes a document through properties like language, scheme or pattern.

    An example is a filter that applies to TypeScript files on disk. Another example is a filter that applies to JSON
    files with name package.json:

        { "language": "typescript", scheme: "file" }
        { "language": "json", "pattern": "**/package.json" }

    Sublime Text doesn\'t understand what a language ID is, so we have to maintain a global translation map from language
    IDs to selectors. Sublime Text also has no support for patterns. We use the wcmatch library for this.
    """

    scheme: str | None
    pattern: str | None
    language: str | None
    def __init__(
        self,
        language: str | None = None,
        scheme: str | None = None,
        pattern: str | None = None,
    ) -> None: ...
    def __call__(self, view: sublime.View) -> bool:
        """Does this filter match the view? An empty filter matches any view."""

class DocumentSelectorMatcher:
    """
    A DocumentSelector is a list of DocumentFilters. A view matches a DocumentSelector if and only if any one of its
    filters matches against the view.
    """

    filters: list[DocumentFilterMatcher]
    def __init__(self, document_selector: DocumentSelector) -> None: ...
    def __bool__(self) -> bool: ...
    def matches(self, view: sublime.View) -> bool:
        """Does this selector match the view? A selector with no filters matches all views."""

def match_file_operation_filters(
    filters: list[FileOperationFilter], uri: URI
) -> bool: ...
def method2attr(method: str) -> str: ...
def method_to_capability(method: str) -> tuple[str, str]:
    """
    Given a method, returns the corresponding capability path, and the associated path to stash the registration key.

    Examples:
        textDocument/definition --> (definitionProvider, definitionProvider.id)
        textDocument/references --> (referencesProvider, referencesProvider.id)
        textDocument/didOpen --> (textDocumentSync.didOpen, textDocumentSync.didOpen.id)
    """

def normalize_text_sync(
    textsync: TextDocumentSyncOptions | TextDocumentSyncKind | None,
) -> dict[str, Any]:
    """Brings legacy text sync capabilities to the most modern format."""

class Capabilities(DottedDict):
    """
    Maintains static and dynamic capabilities.

    Static capabilities come from a response to the initialize request (from Client -> Server).
    Dynamic capabilities can be registered at any moment with client/registerCapability and client/unregisterCapability
    (from Server -> Client).
    """
    def register(
        self,
        registration_id: str,
        capability_path: str,
        registration_path: str,
        options: dict[str, Any],
    ) -> None: ...
    def unregister(
        self, registration_id: str, capability_path: str, registration_path: str
    ) -> dict[str, Any] | None: ...
    def assign(self, d: ServerCapabilities) -> None: ...
    def should_notify_did_open(self) -> bool: ...
    def text_sync_kind(self) -> TextDocumentSyncKind: ...
    def should_notify_did_change_configuration(self) -> bool: ...
    def should_notify_did_change_workspace_folders(self) -> bool: ...
    def should_notify_will_save(self) -> bool: ...
    def should_notify_did_save(self) -> tuple[bool, bool]: ...
    def should_notify_did_close(self) -> bool: ...

class PathMap:
    def __init__(self, local: str, remote: str) -> None: ...
    @classmethod
    def parse(cls, json: Any) -> list[PathMap] | None: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def map_from_local_to_remote(self, uri: str) -> tuple[str, bool]: ...
    def map_from_remote_to_local(self, uri: str) -> tuple[str, bool]: ...

class DefaultViewStatusHandler(ViewStatusHandler):
    def on_view_status_changed(
        self, config_name: str, view: sublime.View, status: str | None
    ) -> None: ...

default_status_view_handler: DefaultViewStatusHandler

class ClientConfig:
    """
    Represents the configuration for a language server.

    Holds all settings needed to start and communicate with a language server, including the command to launch it, the
    file types it applies to, transport options, and LSP-level options such as initialization options and capability
    overrides.

    All root configuration keys from corresponding server configuration (for example the backing LSP-*.sublime-settings
    file) are accessible through attribute access (`.foo`).
    """

    name: str
    selector: str
    priority_selector: str
    schemes: list[str]
    command: list[str]
    tcp_port: int | None
    auto_complete_selector: str | None
    initialization_options: DottedDict
    settings: DottedDict
    env: dict[str, str]
    experimental_capabilities: dict[str, Any] | None
    disabled_capabilities: DottedDict
    file_watcher: FileWatcherConfig
    path_maps: list[PathMap] | None
    semantic_tokens: dict[str, str] | None
    diagnostics_mode: str
    resolved_markdown_language_map: MarkdownLangMap | None
    def __init__(
        self,
        *,
        name: str,
        selector: str,
        priority_selector: str | None = None,
        schemes: list[str] | None = None,
        command: list[str] | None = None,
        tcp_port: int | None = None,
        auto_complete_selector: str | None = None,
        enabled: bool = True,
        initialization_options: DottedDict | None = None,
        settings: DottedDict | None = None,
        env: dict[str, str] | None = None,
        experimental_capabilities: dict[str, Any] | None = None,
        disabled_capabilities: DottedDict | None = None,
        file_watcher: FileWatcherConfig | None = None,
        semantic_tokens: dict[str, str] | None = None,
        diagnostics_mode: str = "all_files",
        markdown_language_map: MarkdownLangMapJson | None = None,
        path_maps: list[PathMap] | None = None,
        settings_registration: SettingsRegistration | None = None,
        all_settings: dict[str, Any] | None = None,
    ) -> None:
        """
        :param name: Unique identifier for this language server.
        :param selector: Sublime Text scope selector that determines which views this server is active for (e.g.
            `"source.python"`).
        :param priority_selector: Selector used when multiple servers match the same view; the highest-scoring server
            takes precedence. Falls back to `selector` when not provided.
        :param schemes: URI schemes this client handles (e.g. `["file", "buffer"]`). Defaults to `["file"]`.
        :param command: Command and arguments used to launch the language server process.
        :param tcp_port: Port for TCP transport. `None` uses stdio. `0` picks a free port. Negative values cause LSP to
            host a TCP server (the language server connects to LSP rather than the other way around); `-1` picks any
            free port, and `-N` binds to port `N`.
        :param auto_complete_selector: Scope selector that restricts when auto-complete suggestions are shown. `None`
             means that the value from the Sublime Text setting of the same name is used.
        :param enabled: Whether this server is enabled.
        :param initialization_options: `initializationOptions` sent to the server during the LSP `initialize` handshake.
        :param settings: Server-specific settings sent via `workspace/didChangeConfiguration` and for
            `workspace/configuration` requests.
        :param env: Additional environment variables for the server process. A list value for the special `"PATH"` key
            is joined with `os.pathsep` and prepended to the existing `PATH`.
        :param experimental_capabilities: Extra capabilities advertised to the server under
            `capabilities.experimental`.
        :param disabled_capabilities: Dotted-path map of capability paths to disable, even if the server advertises
            them.
        :param file_watcher: Configuration for LSP file-watching (glob patterns, etc.).
        :param semantic_tokens: Mapping of semantic token types/modifiers to Sublime Text scopes for syntax
            highlighting.
        :param diagnostics_mode: When to show diagnostics. `"all_files"` (default) shows them for all views;
            `"workspace"` filters out diagnostics for files not within the workspace folders.
        :param markdown_language_map: Optional mapping of markdown language identifiers to aliases and Sublime Text
            syntaxes, used for syntax-highlighting fenced code blocks in popups. Each key is a fenced-code-block
            language tag. Each value is a two-element tuple: aliases and syntax paths or `scope:BASE_SCOPE`
            selectors. Follows the format of mdpopups\' `sublime_user_lang_map` setting. `None` (the default)
            applies no extra mapping.
        :param path_maps: List of :class:`PathMap` entries for translating paths between the local machine and a remote
            server (e.g. inside a container).
        :param settings_registration: The `SettingsRegistration` instance holding resource path and `Settings` instance
            for the plugin settings. Present only for `ClientConfig`s created through `from_sublime_settings()`.
        :param all_settings: The complete raw settings dictionary. Used as a fallback for attribute/key access for
            settings not explicitly modelled above.
        """
    def __getattr__(self, name: str) -> Any:
        """Get property through attribute access (`.foo`) for properties that don't exist natively."""
    @property
    def root_settings(self) -> dict[str, Any]: ...
    @property
    def init_options(self) -> DottedDict: ...
    @property
    def enabled(self) -> bool: ...
    @enabled.setter
    def enabled(self, enabled: bool) -> None: ...
    @property
    def markdown_language_map(self) -> MarkdownLangMapJson | None: ...
    @markdown_language_map.setter
    def markdown_language_map(self, lang_map: MarkdownLangMapJson | None) -> None: ...
    @classmethod
    def from_sublime_settings(
        cls, name: str, settings_registration: SettingsRegistration
    ) -> ClientConfig:
        """
        Create a ClientConfig from a Sublime Text `Settings` object.

        Plugin-defined defaults are read from a resource path to the plugin's `.sublime-settings` file) and user
        overrides are layered on top from `Settings`.

        :param name: Unique server name.
        :param settings_registration: The `SettingsRegistration` object for this client.
        """
    @classmethod
    def from_dict(cls, name: str, d: dict[str, Any]) -> ClientConfig:
        """
        Create a ClientConfig from a plain dictionary.

        :param name: Unique server name.
        :param d: Dictionary of configuration values.
        """
    @classmethod
    def from_config(
        cls, src_config: ClientConfig, override: dict[str, Any]
    ) -> ClientConfig:
        """
        Create a ClientConfig by applying overrides to an existing config.

        Values present in `override` take precedence over those in `src_config`. Structured
        values (`initialization_options`, `settings`) are deep-merged rather than replaced wholesale. The raw
        `_all_settings` dict is shallow-merged.

        :param src_config: The base configuration to start from.
        :param override: Dictionary of values to override.
        """
    def create_transport_config(self) -> TransportConfig:
        """
        Build a :class:`TransportConfig` ready for starting the language server.

        Expands variables in the command arguments and environment, resolves the TCP port (including binding a listener
        socket when LSP is hosting the server), and returns the resulting transport configuration.

        :param variables: Sublime Text variable substitution dict (e.g. from `window.extract_variables()`). A `"port"`
            key is added automatically when a TCP port is in use.
        """
    def set_view_status_handler(self, handler: ViewStatusHandler) -> None: ...
    def set_view_status(self, view: sublime.View, message: str) -> None:
        """
        Update the view status bar entry for this server.

        Shows `"<name> (<message>)"` when `message` is non-empty, or just `"<name>"` otherwise. Does nothing (and erases
        any existing entry) when `show_view_status` is disabled in `LSP.sublime-settings`.

        :param view: The view whose status bar should be updated.
        :param message: A short status string (e.g. `"loading"`). Pass an empty string to show only the client name.
        """
    def erase_view_status(self, view: sublime.View) -> None:
        """
        Remove this server's entry from the view's status bar.

        :param view: The view whose status bar entry should be cleared.
        """
    def match_view(
        self,
        view: sublime.View,
        scheme: str,
        window: sublime.Window,
        workspace_folders: list[WorkspaceFolder],
    ) -> bool:
        """
        Return `True` if this server should be active for the given view.

        Delegates to the registered plugin\'s `is_applicable` method when one is available; otherwise checks that
        `scheme` is in :attr:`schemes` and that the view\'s syntax scope matches :attr:`selector`.

        :param view: The view to test.
        :param scheme: The URI scheme of the view\'s resource (e.g. `"file"`).
        """
    def map_client_path_to_server_uri(self, path: str) -> str:
        """
        Convert a local filesystem path to the URI the language server expects.

        Applies any configured :attr:`path_maps` to translate the path (e.g. from a local path to a container path),
        then converts the result to a `file://` URI.

        :param path: Absolute local filesystem path.
        :returns: URI suitable for sending to the language server.
        """
    def map_server_uri_to_client_path(self, uri: DocumentUri) -> str:
        """
        Convert a URI from the language server to a local filesystem path.

        Only `file://` and `res://` URIs are supported; other schemes raise :exc:`ValueError`. Applies any
        configured :attr:`path_maps` in reverse to translate the server path back to the local path.

        :param uri: URI received from the language server.
        :returns: Absolute local filesystem path.
        :raises ValueError: If the URI scheme is not `"file"` or `"res"`.
        """
    def is_disabled_capability(self, capability_path: str) -> bool:
        """
        Return `True` if the given capability has been disabled in the config.

        Walks :attr:`disabled_capabilities` along `capability_path` (a string such as `"hoverProvider"` or dotted string
        like `textDocumentSync.didOpen`). A capability is considered disabled when the value at that path is `True`, or
        an empty dict (leaf node with no sub-keys).

        :param capability_path: Dotted capability path to check.
        """
    def filter_out_disabled_capabilities(
        self, capability_path: str, options: dict[str, Any]
    ) -> dict[str, Any]: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
