import sublime
import weakref
from ...protocol import (
    AnnotatedTextEdit as AnnotatedTextEdit,
    ApplyWorkspaceEditParams,
    ApplyWorkspaceEditResult as ApplyWorkspaceEditResult,
    ChangeAnnotation as ChangeAnnotation,
    ChangeAnnotationIdentifier as ChangeAnnotationIdentifier,
    CodeAction,
    CodeActionKind,
    CodeActionTriggerKind,
    Command,
    ConfigurationParams,
    CreateFile as CreateFile,
    DeleteFile as DeleteFile,
    Diagnostic as Diagnostic,
    DiagnosticOptions as DiagnosticOptions,
    DiagnosticServerCancellationData as DiagnosticServerCancellationData,
    DidChangeWatchedFilesRegistrationOptions as DidChangeWatchedFilesRegistrationOptions,
    DocumentLink,
    DocumentUri,
    ExecuteCommandParams,
    FileEvent as FileEvent,
    FileSystemWatcher as FileSystemWatcher,
    InitializeParams,
    LSPAny,
    LSPObject as LSPObject,
    Location,
    LocationLink,
    LogMessageParams,
    MessageActionItem as MessageActionItem,
    PreviousResultId as PreviousResultId,
    ProgressParams,
    PublishDiagnosticsParams,
    Range,
    RegistrationParams,
    RenameFile as RenameFile,
    ShowDocumentParams,
    ShowDocumentResult,
    ShowMessageParams,
    ShowMessageRequestParams,
    SignatureHelpTriggerKind,
    SnippetTextEdit as SnippetTextEdit,
    TextDocumentContentRefreshParams,
    TextDocumentEdit as TextDocumentEdit,
    TextDocumentSyncKind,
    TextEdit as TextEdit,
    UnregistrationParams,
    WatchKind as WatchKind,
    WorkDoneProgressCreateParams,
    WorkDoneProgressEnd as WorkDoneProgressEnd,
    WorkDoneProgressReport as WorkDoneProgressReport,
    WorkspaceDocumentDiagnosticReport,
    WorkspaceEdit,
    WorkspaceFolder as LspWorkspaceFolder,
    WorkspaceFullDocumentDiagnosticReport as WorkspaceFullDocumentDiagnosticReport,
)
from ..api import (
    APIHandler as APIHandler,
    AbstractPlugin as AbstractPlugin,
    LspPlugin as LspPlugin,
    PostResponseCallback as PostResponseCallback,
    notification_handler as notification_handler,
    request_handler as request_handler,
)
from ..diagnostics import (
    DiagnosticsIdentifier as DiagnosticsIdentifier,
    DiagnosticsStorage as DiagnosticsStorage,
    WORKSPACE_DIAGNOSTICS_RETRIGGER_DELAY as WORKSPACE_DIAGNOSTICS_RETRIGGER_DELAY,
)
from ..locationpicker import LocationPicker as LocationPicker
from .active_request import ActiveRequest as ActiveRequest
from .collections import DottedDict as DottedDict
from .constants import (
    ChangeEventAction as ChangeEventAction,
    MARKO_MD_PARSER_VERSION as MARKO_MD_PARSER_VERSION,
    MarkdownLangMap as MarkdownLangMap,
    RequestFlags as RequestFlags,
    SEMANTIC_TOKENS_MAP as SEMANTIC_TOKENS_MAP,
    SUPPORTED_DIAGNOSTIC_TAGS as SUPPORTED_DIAGNOSTIC_TAGS,
)
from .edit import (
    WorkspaceEditSummary as WorkspaceEditSummary,
    is_create_file as is_create_file,
    is_delete_file as is_delete_file,
    is_rename_file as is_rename_file,
    is_text_document_edit as is_text_document_edit,
)
from .file_watcher import (
    DEFAULT_WATCH_KIND as DEFAULT_WATCH_KIND,
    FileWatcher as FileWatcher,
    FileWatcherEvent as FileWatcherEvent,
    file_watcher_event_type_to_lsp_file_change_type as file_watcher_event_type_to_lsp_file_change_type,
    get_file_watcher_implementation as get_file_watcher_implementation,
    lsp_watch_kind_to_file_watcher_event_types as lsp_watch_kind_to_file_watcher_event_types,
)
from .logging import debug as debug, exception_log as exception_log, printf as printf
from .open import (
    center_selection as center_selection,
    open_externally as open_externally,
    open_file as open_file,
    open_resource as open_resource,
)
from .progress import WindowProgressReporter as WindowProgressReporter
from .promise import PackagedTask as PackagedTask, Promise as Promise
from .protocol import (
    ClientNotification as ClientNotification,
    ClientRequest as ClientRequest,
    ClientResponse as ClientResponse,
    Error as Error,
    JSONRPCMessage as JSONRPCMessage,
    Notification as Notification,
    Point as Point,
    Request as Request,
    ResolvedCodeLens as ResolvedCodeLens,
    Response as Response,
    ResponseError as ResponseError,
    ServerNotification as ServerNotification,
    ServerResponse as ServerResponse,
)
from .settings import globalprefs as globalprefs, userprefs as userprefs
from .transports import (
    TransportCallbacks as TransportCallbacks,
    TransportWrapper as TransportWrapper,
)
from .types import (
    Capabilities as Capabilities,
    ClientConfig as ClientConfig,
    ClientStates as ClientStates,
    DocumentSelectorMatcher as DocumentSelectorMatcher,
    SemanticToken as SemanticToken,
    debounced as debounced,
    diff as diff,
    method2attr as method2attr,
    method_to_capability as method_to_capability,
    sublime_pattern_to_glob as sublime_pattern_to_glob,
)
from .url import (
    filename_to_uri as filename_to_uri,
    normalize_uri as normalize_uri,
    parse_uri as parse_uri,
)
from .version import __version__ as __version__
from .views import (
    MissingUriError as MissingUriError,
    entire_content as entire_content,
    entire_content_region as entire_content_region,
    first_selection_region as first_selection_region,
    get_uri_and_range_from_location as get_uri_and_range_from_location,
    kind_contains_other_kind as kind_contains_other_kind,
    mutable as mutable,
    uri_from_view as uri_from_view,
)
from .workspace import (
    WorkspaceFolder as WorkspaceFolder,
    is_subpath_of as is_subpath_of,
)
from abc import ABC, abstractmethod
from enum import IntFlag
from typing import Any, Callable, Generator, Literal, Protocol, TypeVar, overload
from typing_extensions import TypeAlias, TypeGuard
from weakref import WeakSet
from ...protocol import WorkspaceFolder as LspWorkspaceFolder

InitCallback: TypeAlias = Callable[["Session", bool], None]
P = TypeVar("P", bound=LSPAny)
R = TypeVar("R", bound=LSPAny)

class ViewStateActions(IntFlag):
    NONE: int
    SAVE: int
    CLOSE: int

def is_workspace_full_document_diagnostic_report(
    report: WorkspaceDocumentDiagnosticReport,
) -> TypeGuard[WorkspaceFullDocumentDiagnosticReport]: ...
def is_diagnostic_server_cancellation_data(
    data: Any,
) -> TypeGuard[DiagnosticServerCancellationData]: ...
def get_semantic_tokens_map(
    custom_tokens_map: dict[str, str] | None,
) -> tuple[tuple[str, str], ...]: ...
def decode_semantic_token(
    types_legend: tuple[str, ...],
    modifiers_legend: tuple[str, ...],
    tokens_scope_map: tuple[tuple[str, str], ...],
    token_type_encoded: int,
    token_modifiers_encoded: int,
) -> tuple[str, list[str], str | None]:
    """
    Converts the token type and token modifiers from encoded numbers into names, based on the legend from
    the server. It also returns the corresponding scope name, which will be used for the highlighting color, either
    derived from a predefined scope map if the token type is one of the types defined in the LSP specs, or from a scope
    for custom token types if it was added in the client configuration (will be `None` if no scope has been defined for
    the custom token type).
    """

class Manager(ABC):
    """A Manager is a container of Sessions."""
    @property
    @abstractmethod
    def window(self) -> sublime.Window:
        """Get the window associated with this manager."""
    @abstractmethod
    def get_session(
        self, config_name: str, file_path: str | None = None
    ) -> Session | None:
        """Gets the session by name and optional file path."""
    @abstractmethod
    def get_project_path(self, file_path: str) -> str | None:
        """Get the project path for the given file."""
    @abstractmethod
    def should_ignore_diagnostics(
        self, uri: DocumentUri, configuration: ClientConfig
    ) -> str | None:
        """Should the diagnostics for this URI be shown in the view? Return a reason why not."""
    @abstractmethod
    def start_async(
        self, configuration: ClientConfig, initiating_view: sublime.View
    ) -> None:
        """
        Start a new Session with the given configuration. The initiating view is the view that caused this method to
        be called.

        A normal flow of calls would be start -> on_post_initialize -> do language server things -> on_post_exit.
        However, it is possible that the subprocess cannot start, in which case on_post_initialize will never be called.
        """
    @abstractmethod
    def on_diagnostics_updated(self) -> None: ...
    @abstractmethod
    def on_post_exit_async(
        self, session: Session, exit_code: int, exception: Exception | None
    ) -> None:
        """The given Session has stopped with the given exit code."""
    @abstractmethod
    def handle_message_request(
        self, config_name: str, params: ShowMessageRequestParams
    ) -> Promise[MessageActionItem | None]: ...
    @abstractmethod
    def handle_show_message(
        self, config_name: str, params: ShowMessageParams
    ) -> Promise[MessageActionItem | None]: ...
    @abstractmethod
    def handle_log_message(
        self, config_name: str, params: LogMessageParams
    ) -> None: ...
    @abstractmethod
    def handle_stderr_log(self, config_name: str, message: str) -> None: ...

def get_initialize_params(
    variables: dict[str, str],
    workspace_folders: list[WorkspaceFolder],
    config: ClientConfig,
) -> InitializeParams: ...

class SessionViewProtocol(Protocol):
    @property
    def session(self) -> Session: ...
    @property
    def view(self) -> sublime.View: ...
    @property
    def listener(self) -> weakref.ref[AbstractViewListener]: ...
    @property
    def session_buffer(self) -> SessionBufferProtocol: ...
    @property
    def active_requests(self) -> dict[int, ActiveRequest]: ...
    def get_uri(self) -> DocumentUri | None: ...
    def get_language_id(self) -> str | None: ...
    def get_view_for_group(self, group: int) -> sublime.View | None: ...
    def on_capability_added_async(
        self, registration_id: str, capability_path: str, options: dict[str, Any]
    ) -> None: ...
    def on_capability_removed_async(
        self, registration_id: str, discarded_capabilities: dict[str, Any]
    ) -> None: ...
    def has_capability_async(self, capability_path: str) -> bool: ...
    def shutdown_async(self) -> None: ...
    def present_diagnostics_async(self, is_view_visible: bool) -> None: ...
    def on_request_started_async(
        self, request_id: int, request: Request[Any, Any]
    ) -> None: ...
    def on_request_finished_async(self, request_id: int) -> None: ...
    def on_request_progress(self, request_id: int, params: dict[str, Any]) -> None: ...
    def get_code_lenses_for_region(self, region: sublime.Region) -> list[Command]: ...
    def handle_code_lenses_async(self, code_lenses: list[ResolvedCodeLens]) -> None: ...
    def clear_code_lenses_async(self) -> None: ...
    def reset_show_definitions(self) -> None: ...
    def on_userprefs_changed_async(self) -> None: ...
    def on_color_scheme_changed(self) -> None: ...
    def get_request_flags(self) -> RequestFlags: ...

class SessionBufferProtocol(Protocol):
    @property
    def session(self) -> Session: ...
    @property
    def session_views(self) -> WeakSet[SessionViewProtocol]: ...
    @property
    def diagnostics(self) -> list[tuple[Diagnostic, sublime.Region]]: ...
    @property
    def last_synced_version(self) -> int: ...
    def get_uri(self) -> str | None: ...
    def get_language_id(self) -> str | None: ...
    def get_view_in_group(self, group: int = ...) -> sublime.View: ...
    def register_capability_async(
        self,
        registration_id: str,
        capability_path: str,
        registration_path: str,
        options: dict[str, Any],
        suppress_requests: bool,
    ) -> None: ...
    def unregister_capability_async(
        self, registration_id: str, capability_path: str, registration_path: str
    ) -> None: ...
    def get_capability(self, capability_path: str) -> Any | None: ...
    def has_capability(self, capability_path: str) -> bool: ...
    def on_userprefs_changed_async(self) -> None: ...
    def on_diagnostics_async(
        self,
        raw_diagnostics: list[Diagnostic],
        version: int | None,
        visible_session_views: set[SessionViewProtocol],
    ) -> None: ...
    def get_document_link_at_point(
        self, view: sublime.View, point: int
    ) -> DocumentLink | None: ...
    def update_document_link(self, new_link: DocumentLink) -> None: ...
    def do_semantic_tokens_async(self, view: sublime.View) -> None: ...
    def get_semantic_tokens(self) -> list[SemanticToken]: ...
    def on_color_scheme_changed(self, view: sublime.View) -> None: ...
    def do_inlay_hints_async(self, view: sublime.View) -> None: ...
    def remove_inlay_hint_phantom(self, phantom_uuid: str) -> None: ...
    def remove_all_inlay_hints(self) -> None: ...
    def do_document_diagnostic_async(
        self, view: sublime.View, version: int, *, forced_update: bool = ...
    ) -> None: ...
    def request_code_actions_async(
        self,
        view: sublime.View,
        region: sublime.Region,
        diagnostics: list[Diagnostic],
        kinds: list[str | CodeActionKind] | None = ...,
        trigger_kind: CodeActionTriggerKind = ...,
    ) -> Promise[list[Command | CodeAction] | Error | None]: ...
    def do_code_lenses_async(self, view: sublime.View) -> None: ...
    def set_pending_refresh(self, flags: RequestFlags) -> None: ...

class AbstractViewListener(ABC):
    TOTAL_ERRORS_AND_WARNINGS_STATUS_KEY: str
    view: sublime.View
    hover_provider_count: int
    lightbulb_color: str
    @abstractmethod
    def session_async(
        self, capability: str, point: int | None = None
    ) -> Session | None: ...
    @abstractmethod
    def sessions_async(self, capability: str | None = None) -> list[Session]: ...
    @abstractmethod
    def session_buffers_async(
        self, capability: str | None = None
    ) -> list[SessionBufferProtocol]: ...
    @abstractmethod
    def session_views_async(self) -> list[SessionViewProtocol]: ...
    @abstractmethod
    def purge_changes_async(self) -> None: ...
    @abstractmethod
    def trigger_on_pre_save_async(self) -> None: ...
    @abstractmethod
    def on_session_initialized_async(self, session: Session) -> None: ...
    @abstractmethod
    def on_session_shutdown_async(self, session: Session) -> None: ...
    @abstractmethod
    def get_diagnostics_async(
        self, location: sublime.Region | int, max_diagnostic_severity_level: int = ...
    ) -> list[tuple[SessionBufferProtocol, list[Diagnostic]]]: ...
    @abstractmethod
    def on_diagnostics_updated_async(
        self, session_buffer: SessionBufferProtocol, is_view_visible: bool
    ) -> None: ...
    @abstractmethod
    def get_language_id(self) -> str: ...
    @abstractmethod
    def get_uri(self) -> DocumentUri: ...
    @overload
    def do_signature_help_async(
        self,
        trigger_kind: Literal[SignatureHelpTriggerKind.TriggerCharacter],
        trigger_char: str,
    ) -> None: ...
    @overload
    def do_signature_help_async(
        self,
        trigger_kind: Literal[
            SignatureHelpTriggerKind.Invoked, SignatureHelpTriggerKind.ContentChange
        ],
        trigger_char: None = None,
    ) -> None: ...
    @abstractmethod
    def navigate_signature_help(self, forward: bool) -> None: ...
    @abstractmethod
    def on_documentation_popup_toggle(self, *, opened: bool) -> None: ...
    @abstractmethod
    def on_post_move_window_async(self) -> None: ...
    @abstractmethod
    def get_request_flags(self, session: Session) -> RequestFlags: ...
    @abstractmethod
    def on_userprefs_changed_async(self) -> None: ...
    @abstractmethod
    def set_change_event_action(self, action: ChangeEventAction) -> None: ...

class Logger(ABC):
    @abstractmethod
    def stderr_message(self, message: str) -> None: ...
    @abstractmethod
    def outgoing_response(self, request_id: int | str, params: Any) -> None: ...
    @abstractmethod
    def outgoing_error_response(self, request_id: int | str, error: Error) -> None: ...
    @abstractmethod
    def outgoing_request(self, request_id: int, method: str, params: Any) -> None: ...
    @abstractmethod
    def outgoing_notification(self, method: str, params: Any) -> None: ...
    @abstractmethod
    def incoming_response(
        self, request_id: int | str, params: Any, is_error: bool
    ) -> None: ...
    @abstractmethod
    def incoming_request(
        self, request_id: int | str, method: str, params: Any
    ) -> None: ...
    @abstractmethod
    def incoming_notification(
        self, method: str, params: Any, unhandled: bool
    ) -> None: ...

def print_to_status_bar(error: ResponseError) -> None: ...

class _RegistrationData:
    registration_id: str
    registration_path: str
    capability_path: str
    selector: DocumentSelectorMatcher
    options: dict[str, Any]
    session_buffers: WeakSet[SessionBufferProtocol]
    def __init__(
        self,
        registration_id: str,
        capability_path: str,
        registration_path: str,
        options: dict[str, Any],
    ) -> None: ...
    def __del__(self) -> None: ...
    def check_applicable(
        self, sb: SessionBufferProtocol, *, suppress_requests: bool = False
    ) -> None: ...

class Session(APIHandler, TransportCallbacks):
    transport: TransportWrapper | None
    working_directory: str | None
    request_id: int
    config: ClientConfig
    config_status_message: str
    manager: ref[Manager]
    window: sublime.Window
    state: ClientStates
    capabilities: Capabilities
    diagnostics: DiagnosticsStorage
    diagnostics_result_ids: dict[tuple[DocumentUri, DiagnosticsIdentifier], str | None]
    workspace_diagnostics_pending_responses: dict[DiagnosticsIdentifier, int | None]
    exiting: bool
    def __init__(
        self,
        manager: Manager,
        logger: Logger,
        workspace_folders: list[WorkspaceFolder],
        config: ClientConfig,
        plugin_class: type[AbstractPlugin | LspPlugin] | None,
    ) -> None: ...
    def get_workspace_folders(self) -> list[WorkspaceFolder]: ...
    @property
    def plugin(self) -> AbstractPlugin | LspPlugin | None: ...
    def register_session_view_async(self, sv: SessionViewProtocol) -> None: ...
    def unregister_session_view_async(self, sv: SessionViewProtocol) -> None: ...
    def session_views_async(self) -> Generator[SessionViewProtocol, None, None]:
        """It is only safe to iterate over this in the async thread."""
    def session_view_for_view_async(
        self, view: sublime.View
    ) -> SessionViewProtocol | None: ...
    def set_config_status_async(self, message: str) -> None:
        """
        Sets the message that is shown in parenthesis within the permanent language server status.

        :param message: The message
        """
    def register_session_buffer_async(self, sb: SessionBufferProtocol) -> None: ...
    def unregister_session_buffer_async(self, sb: SessionBufferProtocol) -> None: ...
    def session_buffers_async(self) -> Generator[SessionBufferProtocol, None, None]:
        """It is only safe to iterate over this in the async thread."""
    def get_session_buffer_for_uri_async(
        self, uri: DocumentUri
    ) -> SessionBufferProtocol | None: ...
    def can_handle(
        self,
        view: sublime.View,
        scheme: str,
        capability: str | None,
        inside_workspace: bool,
    ) -> bool: ...
    def has_capability(self, capability: str, *, check_views: bool = False) -> bool:
        """
        Check whether this `Session` has the given `capability`. If `check_views` is set to `True`, this includes
        capabilities from dynamic registration restricted to certain views if at least one such view is open and matches
        the corresponding `DocumentSelector`.
        """
    def get_capability(self, capability: str, default: Any = None) -> Any: ...
    def should_notify_did_open(self) -> bool: ...
    def text_sync_kind(self) -> TextDocumentSyncKind: ...
    def should_notify_did_change_configuration(self) -> bool: ...
    def should_notify_did_change_workspace_folders(self) -> bool: ...
    def should_notify_will_save(self) -> bool: ...
    def should_notify_did_save(self) -> tuple[bool, bool]: ...
    def should_notify_did_close(self) -> bool: ...
    def on_file_event_async(self, events: list[FileWatcherEvent]) -> None: ...
    def on_userprefs_changed_async(self) -> None: ...
    def markdown_language_id_to_st_syntax_map(self) -> MarkdownLangMap | None: ...
    def handles_path(self, file_path: str | None, inside_workspace: bool) -> bool: ...
    def update_folders(self, folders: list[WorkspaceFolder]) -> None: ...
    def initialize_async(
        self,
        variables: dict[str, str],
        working_directory: str | None,
        transport: TransportWrapper,
        init_callback: InitCallback,
    ) -> None: ...
    def on_stderr_message(self, message: str) -> None: ...
    def execute_command(
        self,
        command: ExecuteCommandParams,
        *,
        progress: bool = False,
        view: sublime.View | None = None,
        is_refactoring: bool = False,
    ) -> Promise[R | Error | None]:
        """Run a command from any thread. Your .then() continuations will run in Sublime's worker thread."""
    def check_log_unsupported_command(self, command: str) -> None: ...
    def run_code_action_async(
        self,
        code_action: Command | CodeAction,
        progress: bool,
        view: sublime.View | None = None,
    ) -> Promise[None]: ...
    def try_open_uri_async(
        self,
        uri: DocumentUri,
        r: Range | None = None,
        flags: sublime.NewFileFlags = ...,
        group: int = -1,
    ) -> Promise[sublime.View | None] | None: ...
    def open_uri_async(
        self,
        uri: DocumentUri,
        r: Range | None = None,
        flags: sublime.NewFileFlags = ...,
        group: int = -1,
    ) -> Promise[sublime.View | None]: ...
    def open_scratch_buffer(
        self,
        title: str,
        content: str,
        syntax: str,
        flags: sublime.NewFileFlags = ...,
        group: int = -1,
    ) -> Promise[sublime.View]: ...
    def open_location_async(
        self,
        location: Location | LocationLink,
        flags: sublime.NewFileFlags = ...,
        group: int = -1,
    ) -> Promise[sublime.View | None]: ...
    def notify_plugin_on_session_buffer_change(
        self, session_buffer: SessionBufferProtocol
    ) -> None: ...
    def apply_document_changes_async(
        self,
        document_changes: list[TextDocumentEdit | CreateFile | RenameFile | DeleteFile],
        change_annotations: dict[ChangeAnnotationIdentifier, ChangeAnnotation],
        *,
        label: str | None = None,
        is_refactoring: bool = False,
    ) -> Promise[ApplyWorkspaceEditResult]: ...
    def apply_workspace_edit_async(
        self,
        edit: WorkspaceEdit,
        *,
        label: str | None = None,
        is_refactoring: bool = False,
    ) -> Promise[tuple[ApplyWorkspaceEditResult, WorkspaceEditSummary]]:
        """
        Apply a WorkspaceEdit, and return a promise that resolves on the async thread again after the edits have been
        applied. The resolved promise contains the ApplyWorkspaceEditResult and a summary of the changes in the
        WorkspaceEdit.
        """
    def decode_semantic_token(
        self,
        types_legend: tuple[str, ...],
        modifiers_legend: tuple[str, ...],
        token_type_encoded: int,
        token_modifiers_encoded: int,
    ) -> tuple[str, list[str], str | None]: ...
    def session_buffers_by_visibility(
        self,
    ) -> tuple[
        list[tuple[SessionBufferProtocol, SessionViewProtocol]],
        list[SessionBufferProtocol],
    ]: ...
    def visible_session_views(self) -> set[SessionViewProtocol]: ...
    def do_workspace_diagnostics_async(self) -> None: ...
    def on_server_settings_changed(self, settings: DottedDict) -> None: ...
    def on_window_show_message_request(
        self, params: ShowMessageRequestParams
    ) -> Promise[MessageActionItem | None]: ...
    def on_window_show_message(self, params: ShowMessageParams) -> None: ...
    def on_window_log_message(self, params: LogMessageParams) -> None: ...
    def on_workspace_workspace_folders(
        self, _: None
    ) -> Promise[list[LspWorkspaceFolder]]: ...
    def on_workspace_configuration(
        self, params: ConfigurationParams
    ) -> Promise[list[LSPAny]]: ...
    def on_workspace_apply_edit(
        self, params: ApplyWorkspaceEditParams
    ) -> Promise[ApplyWorkspaceEditResult]: ...
    def on_workspace_code_lens_refresh(
        self, _: None
    ) -> tuple[Promise[None], PostResponseCallback]: ...
    def on_workspace_semantic_tokens_refresh(
        self, _: None
    ) -> tuple[Promise[None], PostResponseCallback]: ...
    def on_workspace_inlay_hint_refresh(
        self, _: None
    ) -> tuple[Promise[None], PostResponseCallback]: ...
    def on_workspace_diagnostic_refresh(
        self, _: None
    ) -> tuple[Promise[None], PostResponseCallback]: ...
    def on_workspace_text_document_content_refresh(
        self, params: TextDocumentContentRefreshParams
    ) -> Promise[None]: ...
    def on_text_document_publish_diagnostics(
        self, params: PublishDiagnosticsParams
    ) -> None: ...
    def handle_diagnostics_async(
        self,
        uri: DocumentUri,
        identifier: DiagnosticsIdentifier,
        version: int | None,
        diagnostics: list[Diagnostic],
    ) -> None: ...
    def clear_diagnostics_for_uri(self, uri: DocumentUri) -> None: ...
    def on_client_register_capability(
        self, params: RegistrationParams
    ) -> tuple[Promise[None], PostResponseCallback]: ...
    def on_client_unregister_capability(
        self, params: UnregistrationParams
    ) -> Promise[None]: ...
    def register_file_system_watchers(
        self, registration_id: str, watchers: list[FileSystemWatcher]
    ) -> None: ...
    def unregister_file_system_watchers(self, registration_id: str) -> None: ...
    def on_window_show_document(
        self, params: ShowDocumentParams
    ) -> Promise[ShowDocumentResult]: ...
    def on_window_work_done_progress_create(
        self, params: WorkDoneProgressCreateParams
    ) -> Promise[None]: ...
    def on_progress(self, params: ProgressParams) -> None: ...
    def end_async(self) -> None: ...
    def shutdown_session_view_async(
        self, session_view: SessionViewProtocol
    ) -> None: ...
    def on_transport_close(
        self, exit_code: int, exception: Exception | None
    ) -> None: ...
    def send_request_async(
        self,
        request: Request[P, R],
        on_result: Callable[[R], None],
        on_error: Callable[[ResponseError], None] | None = None,
    ) -> int:
        """You must call this method from Sublime's worker thread. Callbacks will run in Sublime's worker thread."""
    def send_request(
        self,
        request: Request[P, R],
        on_result: Callable[[R], None],
        on_error: Callable[[ResponseError], None] | None = None,
    ) -> None:
        """You can call this method from any thread. Callbacks will run in Sublime's worker thread."""
    def send_request_task(self, request: Request[P, R]) -> Promise[R | Error]: ...
    def send_request_task_2(
        self, request: Request[P, R]
    ) -> tuple[Promise[R | Error], int]: ...
    def cancel_request_async(self, request_id: int) -> None: ...
    def send_notification(self, notification: Notification[P]) -> None: ...
    def send_response(self, response: Response[P]) -> None: ...
    def send_error_response(self, request_id: int | str, error: Error) -> None: ...
    def exit(self) -> None: ...
    def send_payload(self, payload: JSONRPCMessage) -> None: ...
    def deduce_payload(
        self, payload: JSONRPCMessage
    ) -> tuple[Callable | None, Any, str | int | None, str | None, str | None]: ...
    def on_payload(self, payload: JSONRPCMessage) -> None: ...
    def response_handler(
        self, response_id: str | int, response: JSONRPCMessage
    ) -> tuple[Callable[[ResponseError], None], str | None, Any, bool]: ...
