from ...protocol import *
import sublime
from dataclasses import dataclass
from plugin.api import PostResponseCallback as PostResponseCallback
from typing import Any, Callable, Generic, Literal, TypeVar
from typing_extensions import NotRequired, TypeAlias, TypedDict
from typing import Union

INT_MAX: int
UINT_MAX = INT_MAX
P_contra = TypeVar("P_contra", bound=LSPAny, contravariant=True)
R = TypeVar("R", bound=LSPAny)

class RequestMessage(TypedDict, closed=True):
    jsonrpc: str
    id: str | int
    method: str
    params: NotRequired[Any]

class ResponseMessage(TypedDict, closed=True):
    jsonrpc: str
    id: str | int
    result: NotRequired[Any]
    error: NotRequired[ResponseError]

class NotificationMessage(TypedDict, closed=True):
    jsonrpc: str
    method: str
    params: NotRequired[Any]

JSONRPCMessage = RequestMessage | ResponseMessage | NotificationMessage

class Request(Generic[P_contra, R]):
    method: str
    params: P_contra
    view: sublime.View | None
    progress: bool | str
    on_partial_result: Callable[[R], None] | None
    def __init__(
        self,
        method: str,
        params: P_contra = None,
        view: sublime.View | None = None,
        progress: bool = False,
        on_partial_result: Callable[[R], None] | None = None,
    ) -> None: ...
    @classmethod
    def initialize(
        cls, params: InitializeParams
    ) -> Request[InitializeParams, InitializeResult]: ...
    @classmethod
    def complete(
        cls, params: CompletionParams, view: sublime.View
    ) -> Request[CompletionParams, list[CompletionItem] | CompletionList | None]: ...
    @classmethod
    def signatureHelp(
        cls, params: SignatureHelpParams, view: sublime.View
    ) -> Request[SignatureHelpParams, SignatureHelp | None]: ...
    @classmethod
    def codeAction(
        cls, params: CodeActionParams, view: sublime.View, progress: bool = False
    ) -> Request[CodeActionParams, list[Command | CodeAction] | None]: ...
    @classmethod
    def documentColor(
        cls, params: DocumentColorParams, view: sublime.View
    ) -> Request[DocumentColorParams, list[ColorInformation]]: ...
    @classmethod
    def colorPresentation(
        cls, params: ColorPresentationParams, view: sublime.View
    ) -> Request[ColorPresentationParams, list[ColorPresentation]]: ...
    @classmethod
    def executeCommand(
        cls, params: ExecuteCommandParams, *, progress: bool = False
    ) -> Request[ExecuteCommandParams, R]: ...
    @classmethod
    def willSaveWaitUntil(
        cls, params: WillSaveTextDocumentParams, view: sublime.View
    ) -> Request[WillSaveTextDocumentParams, list[TextEdit] | None]: ...
    @classmethod
    def willRenameFiles(
        cls, params: RenameFilesParams
    ) -> Request[RenameFilesParams, WorkspaceEdit | None]: ...
    @classmethod
    def documentSymbols(
        cls, params: DocumentSymbolParams, view: sublime.View
    ) -> Request[
        DocumentSymbolParams, list[DocumentSymbol] | list[SymbolInformation] | None
    ]: ...
    @classmethod
    def documentHighlight(
        cls, params: DocumentHighlightParams, view: sublime.View
    ) -> Request[DocumentHighlightParams, list[DocumentHighlight] | None]: ...
    @classmethod
    def documentLink(
        cls, params: DocumentLinkParams, view: sublime.View
    ) -> Request[DocumentLinkParams, list[DocumentLink]]: ...
    @classmethod
    def semanticTokensFull(
        cls, params: SemanticTokensParams, view: sublime.View
    ) -> Request[SemanticTokensParams, SemanticTokens | None]: ...
    @classmethod
    def semanticTokensFullDelta(
        cls, params: SemanticTokensDeltaParams, view: sublime.View
    ) -> Request[
        SemanticTokensDeltaParams, SemanticTokens | SemanticTokensDelta | None
    ]: ...
    @classmethod
    def semanticTokensRange(
        cls, params: SemanticTokensRangeParams, view: sublime.View
    ) -> Request[SemanticTokensRangeParams, SemanticTokens | None]: ...
    @classmethod
    def prepareCallHierarchy(
        cls, params: CallHierarchyPrepareParams, view: sublime.View
    ) -> Request[CallHierarchyPrepareParams, list[CallHierarchyItem] | None]: ...
    @classmethod
    def incomingCalls(
        cls, params: CallHierarchyIncomingCallsParams
    ) -> Request[
        CallHierarchyIncomingCallsParams, list[CallHierarchyIncomingCall] | None
    ]: ...
    @classmethod
    def outgoingCalls(
        cls, params: CallHierarchyOutgoingCallsParams
    ) -> Request[
        CallHierarchyOutgoingCallsParams, list[CallHierarchyOutgoingCall] | None
    ]: ...
    @classmethod
    def prepareTypeHierarchy(
        cls, params: TypeHierarchyPrepareParams, view: sublime.View
    ) -> Request[TypeHierarchyPrepareParams, list[TypeHierarchyItem] | None]: ...
    @classmethod
    def supertypes(
        cls, params: TypeHierarchySupertypesParams
    ) -> Request[TypeHierarchySupertypesParams, list[TypeHierarchyItem] | None]: ...
    @classmethod
    def subtypes(
        cls, params: TypeHierarchySubtypesParams
    ) -> Request[TypeHierarchySubtypesParams, list[TypeHierarchyItem] | None]: ...
    @classmethod
    def resolveCompletionItem(
        cls, params: CompletionItem, view: sublime.View
    ) -> Request[CompletionItem, CompletionItem]: ...
    @classmethod
    def resolveDocumentLink(
        cls, params: DocumentLink, view: sublime.View
    ) -> Request[DocumentLink, DocumentLink]: ...
    @classmethod
    def inlayHint(
        cls, params: InlayHintParams, view: sublime.View
    ) -> Request[InlayHintParams, list[InlayHint] | None]: ...
    @classmethod
    def resolveInlayHint(
        cls, params: InlayHint, view: sublime.View
    ) -> Request[InlayHint, InlayHint]: ...
    @classmethod
    def onTypeFormatting(
        cls, params: DocumentOnTypeFormattingParams, view: sublime.View
    ) -> Request[DocumentOnTypeFormattingParams, list[TextEdit] | None]: ...
    @classmethod
    def rename(
        cls, params: RenameParams, view: sublime.View, *, progress: bool = False
    ) -> Request[RenameParams, WorkspaceEdit | None]: ...
    @classmethod
    def prepareRename(
        cls, params: PrepareRenameParams, view: sublime.View, progress: bool = False
    ) -> Request[PrepareRenameParams, PrepareRenameResult | None]: ...
    @classmethod
    def selectionRange(
        cls, params: SelectionRangeParams
    ) -> Request[SelectionRangeParams, list[SelectionRange] | None]: ...
    @classmethod
    def foldingRange(
        cls, params: FoldingRangeParams, view: sublime.View
    ) -> Request[FoldingRangeParams, list[FoldingRange] | None]: ...
    @classmethod
    def formatting(
        cls, params: DocumentFormattingParams, view: sublime.View
    ) -> Request[DocumentFormattingParams, list[TextEdit] | None]: ...
    @classmethod
    def range_formatting(
        cls, params: DocumentRangeFormattingParams, view: sublime.View
    ) -> Request[DocumentRangeFormattingParams, list[TextEdit] | None]: ...
    @classmethod
    def ranges_formatting(
        cls, params: DocumentRangesFormattingParams, view: sublime.View
    ) -> Request[DocumentRangesFormattingParams, list[TextEdit] | None]: ...
    @classmethod
    def workspaceSymbol(
        cls, params: WorkspaceSymbolParams
    ) -> Request[
        WorkspaceSymbolParams, list[SymbolInformation] | list[WorkspaceSymbol] | None
    ]: ...
    @classmethod
    def resolveWorkspaceSymbol(
        cls, params: WorkspaceSymbol
    ) -> Request[WorkspaceSymbol, WorkspaceSymbol]: ...
    @classmethod
    def documentDiagnostic(
        cls, params: DocumentDiagnosticParams, view: sublime.View
    ) -> Request[DocumentDiagnosticParams, DocumentDiagnosticReport]: ...
    @classmethod
    def workspaceDiagnostic(
        cls,
        params: WorkspaceDiagnosticParams,
        on_partial_result: Callable[[WorkspaceDiagnosticReport], None],
    ) -> Request[WorkspaceDiagnosticParams, WorkspaceDiagnosticReport]: ...
    @classmethod
    def shutdown(cls) -> Request[None, None]: ...
    def to_payload(self, request_id: int) -> RequestMessage: ...

class Error(Exception):
    def __init__(self, code: int, message: str, data: Any = None) -> None: ...
    @property
    def code(self) -> int: ...
    @property
    def data(self) -> Any: ...
    @classmethod
    def from_lsp(cls, params: ResponseError) -> Error: ...
    def to_lsp(self) -> ResponseError: ...
    @classmethod
    def from_exception(cls, ex: BaseException) -> Error: ...

class Response(Generic[R]):
    request_id: str | int
    result: R
    post_response_callback: PostResponseCallback | None
    def __init__(
        self,
        request_id: str | int,
        result: R,
        post_response_callback: PostResponseCallback | None = None,
    ) -> None: ...
    def to_payload(self) -> ResponseMessage: ...

class Notification(Generic[P_contra]):
    method: str
    params: P_contra
    def __init__(self, method: str, params: P_contra = None) -> None: ...
    @classmethod
    def initialized(cls) -> Notification[InitializedParams]: ...
    @classmethod
    def didOpen(
        cls, params: DidOpenTextDocumentParams
    ) -> Notification[DidOpenTextDocumentParams]: ...
    @classmethod
    def didChange(
        cls, params: DidChangeTextDocumentParams
    ) -> Notification[DidChangeTextDocumentParams]: ...
    @classmethod
    def willSave(
        cls, params: WillSaveTextDocumentParams
    ) -> Notification[WillSaveTextDocumentParams]: ...
    @classmethod
    def didSave(
        cls, params: DidSaveTextDocumentParams
    ) -> Notification[DidSaveTextDocumentParams]: ...
    @classmethod
    def didClose(
        cls, params: DidCloseTextDocumentParams
    ) -> Notification[DidCloseTextDocumentParams]: ...
    @classmethod
    def didCreateFiles(
        cls, params: CreateFilesParams
    ) -> Notification[CreateFilesParams]: ...
    @classmethod
    def didRenameFiles(
        cls, params: RenameFilesParams
    ) -> Notification[RenameFilesParams]: ...
    @classmethod
    def didDeleteFiles(
        cls, params: DeleteFilesParams
    ) -> Notification[DeleteFilesParams]: ...
    @classmethod
    def didChangeConfiguration(
        cls, params: DidChangeConfigurationParams
    ) -> Notification[DidChangeConfigurationParams]: ...
    @classmethod
    def didChangeWatchedFiles(
        cls, params: DidChangeWatchedFilesParams
    ) -> Notification[DidChangeWatchedFilesParams]: ...
    @classmethod
    def didChangeWorkspaceFolders(
        cls, params: DidChangeWorkspaceFoldersParams
    ) -> Notification[DidChangeWorkspaceFoldersParams]: ...
    @classmethod
    def exit(cls) -> Notification[None]: ...
    def to_payload(self) -> NotificationMessage: ...

@dataclass(frozen=True, order=True)
class TextPosition:
    row: int
    col: int
    @classmethod
    def from_lsp(cls, position: Position) -> TextPosition: ...
    def to_lsp(self) -> Position: ...

class Point(TextPosition): ...

class ResponseError(TypedDict, closed=True):
    code: int
    message: str
    data: NotRequired[LSPAny]

class ResolvedCodeLens(TypedDict, closed=True):
    range: Range
    command: Command
    uses_cached_command: NotRequired[bool]

RangeLsp = Range

class ApplyWorkspaceEditRequest(TypedDict, closed=True):
    method: Literal["workspace/applyEdit"]
    params: ApplyWorkspaceEditParams

class CallHierarchyIncomingCallsRequest(TypedDict, closed=True):
    method: Literal["callHierarchy/incomingCalls"]
    params: CallHierarchyIncomingCallsParams

class CallHierarchyOutgoingCallsRequest(TypedDict, closed=True):
    method: Literal["callHierarchy/outgoingCalls"]
    params: CallHierarchyOutgoingCallsParams

class CallHierarchyPrepareRequest(TypedDict, closed=True):
    method: Literal["textDocument/prepareCallHierarchy"]
    params: CallHierarchyPrepareParams

class CodeActionRequest(TypedDict, closed=True):
    method: Literal["textDocument/codeAction"]
    params: CodeActionParams

class CodeActionResolveRequest(TypedDict, closed=True):
    method: Literal["codeAction/resolve"]
    params: CodeAction

class CodeLensRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/codeLens/refresh"]
    params: None

class CodeLensRequest(TypedDict, closed=True):
    method: Literal["textDocument/codeLens"]
    params: CodeLensParams

class CodeLensResolveRequest(TypedDict, closed=True):
    method: Literal["codeLens/resolve"]
    params: CodeLens

class ColorPresentationRequest(TypedDict, closed=True):
    method: Literal["textDocument/colorPresentation"]
    params: ColorPresentationParams

class CompletionRequest(TypedDict, closed=True):
    method: Literal["textDocument/completion"]
    params: CompletionParams

class CompletionResolveRequest(TypedDict, closed=True):
    method: Literal["completionItem/resolve"]
    params: CompletionItem

class ConfigurationRequest(TypedDict, closed=True):
    method: Literal["workspace/configuration"]
    params: ConfigurationParams

class DeclarationRequest(TypedDict, closed=True):
    method: Literal["textDocument/declaration"]
    params: DeclarationParams

class DefinitionRequest(TypedDict, closed=True):
    method: Literal["textDocument/definition"]
    params: DefinitionParams

class DiagnosticRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/diagnostic/refresh"]
    params: None

class DocumentColorRequest(TypedDict, closed=True):
    method: Literal["textDocument/documentColor"]
    params: DocumentColorParams

class DocumentDiagnosticRequest(TypedDict, closed=True):
    method: Literal["textDocument/diagnostic"]
    params: DocumentDiagnosticParams

class DocumentFormattingRequest(TypedDict, closed=True):
    method: Literal["textDocument/formatting"]
    params: DocumentFormattingParams

class DocumentHighlightRequest(TypedDict, closed=True):
    method: Literal["textDocument/documentHighlight"]
    params: DocumentHighlightParams

class DocumentLinkRequest(TypedDict, closed=True):
    method: Literal["textDocument/documentLink"]
    params: DocumentLinkParams

class DocumentLinkResolveRequest(TypedDict, closed=True):
    method: Literal["documentLink/resolve"]
    params: DocumentLink

class DocumentOnTypeFormattingRequest(TypedDict, closed=True):
    method: Literal["textDocument/onTypeFormatting"]
    params: DocumentOnTypeFormattingParams

class DocumentRangeFormattingRequest(TypedDict, closed=True):
    method: Literal["textDocument/rangeFormatting"]
    params: DocumentRangeFormattingParams

class DocumentRangesFormattingRequest(TypedDict, closed=True):
    method: Literal["textDocument/rangesFormatting"]
    params: DocumentRangesFormattingParams

class DocumentSymbolRequest(TypedDict, closed=True):
    method: Literal["textDocument/documentSymbol"]
    params: DocumentSymbolParams

class ExecuteCommandRequest(TypedDict, closed=True):
    method: Literal["workspace/executeCommand"]
    params: ExecuteCommandParams

class FoldingRangeRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/foldingRange/refresh"]
    params: None

class FoldingRangeRequest(TypedDict, closed=True):
    method: Literal["textDocument/foldingRange"]
    params: FoldingRangeParams

class HoverRequest(TypedDict, closed=True):
    method: Literal["textDocument/hover"]
    params: HoverParams

class ImplementationRequest(TypedDict, closed=True):
    method: Literal["textDocument/implementation"]
    params: ImplementationParams

class InitializeRequest(TypedDict, closed=True):
    method: Literal["initialize"]
    params: InitializeParams

class InlayHintRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/inlayHint/refresh"]
    params: None

class InlayHintRequest(TypedDict, closed=True):
    method: Literal["textDocument/inlayHint"]
    params: InlayHintParams

class InlayHintResolveRequest(TypedDict, closed=True):
    method: Literal["inlayHint/resolve"]
    params: InlayHint

class InlineCompletionRequest(TypedDict, closed=True):
    method: Literal["textDocument/inlineCompletion"]
    params: InlineCompletionParams

class InlineValueRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/inlineValue/refresh"]
    params: None

class InlineValueRequest(TypedDict, closed=True):
    method: Literal["textDocument/inlineValue"]
    params: InlineValueParams

class LinkedEditingRangeRequest(TypedDict, closed=True):
    method: Literal["textDocument/linkedEditingRange"]
    params: LinkedEditingRangeParams

class MonikerRequest(TypedDict, closed=True):
    method: Literal["textDocument/moniker"]
    params: MonikerParams

class PrepareRenameRequest(TypedDict, closed=True):
    method: Literal["textDocument/prepareRename"]
    params: PrepareRenameParams

class ReferencesRequest(TypedDict, closed=True):
    method: Literal["textDocument/references"]
    params: ReferenceParams

class RegistrationRequest(TypedDict, closed=True):
    method: Literal["client/registerCapability"]
    params: RegistrationParams

class RenameRequest(TypedDict, closed=True):
    method: Literal["textDocument/rename"]
    params: RenameParams

class SelectionRangeRequest(TypedDict, closed=True):
    method: Literal["textDocument/selectionRange"]
    params: SelectionRangeParams

class SemanticTokensDeltaRequest(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/full/delta"]
    params: SemanticTokensDeltaParams

class SemanticTokensRangeRequest(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/range"]
    params: SemanticTokensRangeParams

class SemanticTokensRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/semanticTokens/refresh"]
    params: None

class SemanticTokensRequest(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/full"]
    params: SemanticTokensParams

class ShowDocumentRequest(TypedDict, closed=True):
    method: Literal["window/showDocument"]
    params: ShowDocumentParams

class ShowMessageRequest(TypedDict, closed=True):
    method: Literal["window/showMessageRequest"]
    params: ShowMessageRequestParams

class ShutdownRequest(TypedDict, closed=True):
    method: Literal["shutdown"]
    params: None

class SignatureHelpRequest(TypedDict, closed=True):
    method: Literal["textDocument/signatureHelp"]
    params: SignatureHelpParams

class TextDocumentContentRefreshRequest(TypedDict, closed=True):
    method: Literal["workspace/textDocumentContent/refresh"]
    params: TextDocumentContentRefreshParams

class TextDocumentContentRequest(TypedDict, closed=True):
    method: Literal["workspace/textDocumentContent"]
    params: TextDocumentContentParams

class TypeDefinitionRequest(TypedDict, closed=True):
    method: Literal["textDocument/typeDefinition"]
    params: TypeDefinitionParams

class TypeHierarchyPrepareRequest(TypedDict, closed=True):
    method: Literal["textDocument/prepareTypeHierarchy"]
    params: TypeHierarchyPrepareParams

class TypeHierarchySubtypesRequest(TypedDict, closed=True):
    method: Literal["typeHierarchy/subtypes"]
    params: TypeHierarchySubtypesParams

class TypeHierarchySupertypesRequest(TypedDict, closed=True):
    method: Literal["typeHierarchy/supertypes"]
    params: TypeHierarchySupertypesParams

class UnregistrationRequest(TypedDict, closed=True):
    method: Literal["client/unregisterCapability"]
    params: UnregistrationParams

class WillCreateFilesRequest(TypedDict, closed=True):
    method: Literal["workspace/willCreateFiles"]
    params: CreateFilesParams

class WillDeleteFilesRequest(TypedDict, closed=True):
    method: Literal["workspace/willDeleteFiles"]
    params: DeleteFilesParams

class WillRenameFilesRequest(TypedDict, closed=True):
    method: Literal["workspace/willRenameFiles"]
    params: RenameFilesParams

class WillSaveTextDocumentWaitUntilRequest(TypedDict, closed=True):
    method: Literal["textDocument/willSaveWaitUntil"]
    params: WillSaveTextDocumentParams

class WorkDoneProgressCreateRequest(TypedDict, closed=True):
    method: Literal["window/workDoneProgress/create"]
    params: WorkDoneProgressCreateParams

class WorkspaceDiagnosticRequest(TypedDict, closed=True):
    method: Literal["workspace/diagnostic"]
    params: WorkspaceDiagnosticParams

class WorkspaceFoldersRequest(TypedDict, closed=True):
    method: Literal["workspace/workspaceFolders"]
    params: None

class WorkspaceSymbolRequest(TypedDict, closed=True):
    method: Literal["workspace/symbol"]
    params: WorkspaceSymbolParams

class WorkspaceSymbolResolveRequest(TypedDict, closed=True):
    method: Literal["workspaceSymbol/resolve"]
    params: WorkspaceSymbol

ClientRequest: TypeAlias = Union[
    CallHierarchyIncomingCallsRequest,
    CallHierarchyOutgoingCallsRequest,
    CallHierarchyPrepareRequest,
    CodeActionRequest,
    CodeActionResolveRequest,
    CodeLensRequest,
    CodeLensResolveRequest,
    ColorPresentationRequest,
    CompletionRequest,
    CompletionResolveRequest,
    DeclarationRequest,
    DefinitionRequest,
    DocumentColorRequest,
    DocumentDiagnosticRequest,
    DocumentFormattingRequest,
    DocumentHighlightRequest,
    DocumentLinkRequest,
    DocumentLinkResolveRequest,
    DocumentOnTypeFormattingRequest,
    DocumentRangeFormattingRequest,
    DocumentRangesFormattingRequest,
    DocumentSymbolRequest,
    ExecuteCommandRequest,
    FoldingRangeRequest,
    HoverRequest,
    ImplementationRequest,
    InitializeRequest,
    InlayHintRequest,
    InlayHintResolveRequest,
    InlineCompletionRequest,
    InlineValueRequest,
    LinkedEditingRangeRequest,
    MonikerRequest,
    PrepareRenameRequest,
    ReferencesRequest,
    RenameRequest,
    SelectionRangeRequest,
    SemanticTokensDeltaRequest,
    SemanticTokensRangeRequest,
    SemanticTokensRequest,
    ShutdownRequest,
    SignatureHelpRequest,
    TextDocumentContentRequest,
    TypeDefinitionRequest,
    TypeHierarchyPrepareRequest,
    TypeHierarchySubtypesRequest,
    TypeHierarchySupertypesRequest,
    WillCreateFilesRequest,
    WillDeleteFilesRequest,
    WillRenameFilesRequest,
    WillSaveTextDocumentWaitUntilRequest,
    WorkspaceDiagnosticRequest,
    WorkspaceSymbolRequest,
    WorkspaceSymbolResolveRequest,
]
ServerRequest: TypeAlias = Union[
    ApplyWorkspaceEditRequest,
    CodeLensRefreshRequest,
    ConfigurationRequest,
    DiagnosticRefreshRequest,
    FoldingRangeRefreshRequest,
    InlayHintRefreshRequest,
    InlineValueRefreshRequest,
    RegistrationRequest,
    SemanticTokensRefreshRequest,
    ShowDocumentRequest,
    ShowMessageRequest,
    TextDocumentContentRefreshRequest,
    UnregistrationRequest,
    WorkDoneProgressCreateRequest,
    WorkspaceFoldersRequest,
]

class ApplyWorkspaceEditResponse(TypedDict, closed=True):
    method: Literal["workspace/applyEdit"]
    params: ApplyWorkspaceEditParams
    result: ApplyWorkspaceEditResult

class CallHierarchyIncomingCallsResponse(TypedDict, closed=True):
    method: Literal["callHierarchy/incomingCalls"]
    result: list[CallHierarchyIncomingCall] | None

class CallHierarchyOutgoingCallsResponse(TypedDict, closed=True):
    method: Literal["callHierarchy/outgoingCalls"]
    result: list[CallHierarchyOutgoingCall] | None

class CallHierarchyPrepareResponse(TypedDict, closed=True):
    method: Literal["textDocument/prepareCallHierarchy"]
    result: list[CallHierarchyItem] | None

class CodeActionResponse(TypedDict, closed=True):
    method: Literal["textDocument/codeAction"]
    result: list[Command | CodeAction] | None

class CodeActionResolveResponse(TypedDict, closed=True):
    method: Literal["codeAction/resolve"]
    result: CodeAction

class CodeLensRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/codeLens/refresh"]
    params: None
    result: None

class CodeLensResponse(TypedDict, closed=True):
    method: Literal["textDocument/codeLens"]
    result: list[CodeLens] | None

class CodeLensResolveResponse(TypedDict, closed=True):
    method: Literal["codeLens/resolve"]
    result: CodeLens

class ColorPresentationResponse(TypedDict, closed=True):
    method: Literal["textDocument/colorPresentation"]
    result: list[ColorPresentation]

class CompletionResponse(TypedDict, closed=True):
    method: Literal["textDocument/completion"]
    result: list[CompletionItem] | CompletionList | None

class CompletionResolveResponse(TypedDict, closed=True):
    method: Literal["completionItem/resolve"]
    result: CompletionItem

class ConfigurationResponse(TypedDict, closed=True):
    method: Literal["workspace/configuration"]
    params: ConfigurationParams
    result: list[LSPAny]

class DeclarationResponse(TypedDict, closed=True):
    method: Literal["textDocument/declaration"]
    result: Declaration | list[DeclarationLink] | None

class DefinitionResponse(TypedDict, closed=True):
    method: Literal["textDocument/definition"]
    result: Definition | list[DefinitionLink] | None

class DiagnosticRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/diagnostic/refresh"]
    params: None
    result: None

class DocumentColorResponse(TypedDict, closed=True):
    method: Literal["textDocument/documentColor"]
    result: list[ColorInformation]

class DocumentDiagnosticResponse(TypedDict, closed=True):
    method: Literal["textDocument/diagnostic"]
    result: DocumentDiagnosticReport

class DocumentFormattingResponse(TypedDict, closed=True):
    method: Literal["textDocument/formatting"]
    result: list[TextEdit] | None

class DocumentHighlightResponse(TypedDict, closed=True):
    method: Literal["textDocument/documentHighlight"]
    result: list[DocumentHighlight] | None

class DocumentLinkResponse(TypedDict, closed=True):
    method: Literal["textDocument/documentLink"]
    result: list[DocumentLink] | None

class DocumentLinkResolveResponse(TypedDict, closed=True):
    method: Literal["documentLink/resolve"]
    result: DocumentLink

class DocumentOnTypeFormattingResponse(TypedDict, closed=True):
    method: Literal["textDocument/onTypeFormatting"]
    result: list[TextEdit] | None

class DocumentRangeFormattingResponse(TypedDict, closed=True):
    method: Literal["textDocument/rangeFormatting"]
    result: list[TextEdit] | None

class DocumentRangesFormattingResponse(TypedDict, closed=True):
    method: Literal["textDocument/rangesFormatting"]
    result: list[TextEdit] | None

class DocumentSymbolResponse(TypedDict, closed=True):
    method: Literal["textDocument/documentSymbol"]
    result: list[SymbolInformation] | list[DocumentSymbol] | None

class ExecuteCommandResponse(TypedDict, closed=True):
    method: Literal["workspace/executeCommand"]
    result: LSPAny | None

class FoldingRangeRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/foldingRange/refresh"]
    params: None
    result: None

class FoldingRangeResponse(TypedDict, closed=True):
    method: Literal["textDocument/foldingRange"]
    result: list[FoldingRange] | None

class HoverResponse(TypedDict, closed=True):
    method: Literal["textDocument/hover"]
    result: Hover | None

class ImplementationResponse(TypedDict, closed=True):
    method: Literal["textDocument/implementation"]
    result: Definition | list[DefinitionLink] | None

class InitializeResponse(TypedDict, closed=True):
    method: Literal["initialize"]
    result: InitializeResult

class InlayHintRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/inlayHint/refresh"]
    params: None
    result: None

class InlayHintResponse(TypedDict, closed=True):
    method: Literal["textDocument/inlayHint"]
    result: list[InlayHint] | None

class InlayHintResolveResponse(TypedDict, closed=True):
    method: Literal["inlayHint/resolve"]
    result: InlayHint

class InlineCompletionResponse(TypedDict, closed=True):
    method: Literal["textDocument/inlineCompletion"]
    result: InlineCompletionList | list[InlineCompletionItem] | None

class InlineValueRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/inlineValue/refresh"]
    params: None
    result: None

class InlineValueResponse(TypedDict, closed=True):
    method: Literal["textDocument/inlineValue"]
    result: list[InlineValue] | None

class LinkedEditingRangeResponse(TypedDict, closed=True):
    method: Literal["textDocument/linkedEditingRange"]
    result: LinkedEditingRanges | None

class MonikerResponse(TypedDict, closed=True):
    method: Literal["textDocument/moniker"]
    result: list[Moniker] | None

class PrepareRenameResponse(TypedDict, closed=True):
    method: Literal["textDocument/prepareRename"]
    result: PrepareRenameResult | None

class ReferencesResponse(TypedDict, closed=True):
    method: Literal["textDocument/references"]
    result: list[Location] | None

class RegistrationResponse(TypedDict, closed=True):
    method: Literal["client/registerCapability"]
    params: RegistrationParams
    result: None

class RenameResponse(TypedDict, closed=True):
    method: Literal["textDocument/rename"]
    result: WorkspaceEdit | None

class SelectionRangeResponse(TypedDict, closed=True):
    method: Literal["textDocument/selectionRange"]
    result: list[SelectionRange] | None

class SemanticTokensDeltaResponse(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/full/delta"]
    result: SemanticTokens | SemanticTokensDelta | None

class SemanticTokensRangeResponse(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/range"]
    result: SemanticTokens | None

class SemanticTokensRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/semanticTokens/refresh"]
    params: None
    result: None

class SemanticTokensResponse(TypedDict, closed=True):
    method: Literal["textDocument/semanticTokens/full"]
    result: SemanticTokens | None

class ShowDocumentResponse(TypedDict, closed=True):
    method: Literal["window/showDocument"]
    params: ShowDocumentParams
    result: ShowDocumentResult

class ShowMessageResponse(TypedDict, closed=True):
    method: Literal["window/showMessageRequest"]
    params: ShowMessageRequestParams
    result: MessageActionItem | None

class ShutdownResponse(TypedDict, closed=True):
    method: Literal["shutdown"]
    result: None

class SignatureHelpResponse(TypedDict, closed=True):
    method: Literal["textDocument/signatureHelp"]
    result: SignatureHelp | None

class TextDocumentContentRefreshResponse(TypedDict, closed=True):
    method: Literal["workspace/textDocumentContent/refresh"]
    params: TextDocumentContentRefreshParams
    result: None

class TextDocumentContentResponse(TypedDict, closed=True):
    method: Literal["workspace/textDocumentContent"]
    result: TextDocumentContentResult

class TypeDefinitionResponse(TypedDict, closed=True):
    method: Literal["textDocument/typeDefinition"]
    result: Definition | list[DefinitionLink] | None

class TypeHierarchyPrepareResponse(TypedDict, closed=True):
    method: Literal["textDocument/prepareTypeHierarchy"]
    result: list[TypeHierarchyItem] | None

class TypeHierarchySubtypesResponse(TypedDict, closed=True):
    method: Literal["typeHierarchy/subtypes"]
    result: list[TypeHierarchyItem] | None

class TypeHierarchySupertypesResponse(TypedDict, closed=True):
    method: Literal["typeHierarchy/supertypes"]
    result: list[TypeHierarchyItem] | None

class UnregistrationResponse(TypedDict, closed=True):
    method: Literal["client/unregisterCapability"]
    params: UnregistrationParams
    result: None

class WillCreateFilesResponse(TypedDict, closed=True):
    method: Literal["workspace/willCreateFiles"]
    result: WorkspaceEdit | None

class WillDeleteFilesResponse(TypedDict, closed=True):
    method: Literal["workspace/willDeleteFiles"]
    result: WorkspaceEdit | None

class WillRenameFilesResponse(TypedDict, closed=True):
    method: Literal["workspace/willRenameFiles"]
    result: WorkspaceEdit | None

class WillSaveTextDocumentWaitUntilResponse(TypedDict, closed=True):
    method: Literal["textDocument/willSaveWaitUntil"]
    result: list[TextEdit] | None

class WorkDoneProgressCreateResponse(TypedDict, closed=True):
    method: Literal["window/workDoneProgress/create"]
    params: WorkDoneProgressCreateParams
    result: None

class WorkspaceDiagnosticResponse(TypedDict, closed=True):
    method: Literal["workspace/diagnostic"]
    result: WorkspaceDiagnosticReport

class WorkspaceFoldersResponse(TypedDict, closed=True):
    method: Literal["workspace/workspaceFolders"]
    params: None
    result: list[WorkspaceFolder] | None

class WorkspaceSymbolResponse(TypedDict, closed=True):
    method: Literal["workspace/symbol"]
    result: list[SymbolInformation] | list[WorkspaceSymbol] | None

class WorkspaceSymbolResolveResponse(TypedDict, closed=True):
    method: Literal["workspaceSymbol/resolve"]
    result: WorkspaceSymbol

ServerResponse: TypeAlias = Union[
    CallHierarchyIncomingCallsResponse,
    CallHierarchyOutgoingCallsResponse,
    CallHierarchyPrepareResponse,
    CodeActionResponse,
    CodeActionResolveResponse,
    CodeLensResponse,
    CodeLensResolveResponse,
    ColorPresentationResponse,
    CompletionResponse,
    CompletionResolveResponse,
    DeclarationResponse,
    DefinitionResponse,
    DocumentColorResponse,
    DocumentDiagnosticResponse,
    DocumentFormattingResponse,
    DocumentHighlightResponse,
    DocumentLinkResponse,
    DocumentLinkResolveResponse,
    DocumentOnTypeFormattingResponse,
    DocumentRangeFormattingResponse,
    DocumentRangesFormattingResponse,
    DocumentSymbolResponse,
    ExecuteCommandResponse,
    FoldingRangeResponse,
    HoverResponse,
    ImplementationResponse,
    InitializeResponse,
    InlayHintResponse,
    InlayHintResolveResponse,
    InlineCompletionResponse,
    InlineValueResponse,
    LinkedEditingRangeResponse,
    MonikerResponse,
    PrepareRenameResponse,
    ReferencesResponse,
    RenameResponse,
    SelectionRangeResponse,
    SemanticTokensDeltaResponse,
    SemanticTokensRangeResponse,
    SemanticTokensResponse,
    ShutdownResponse,
    SignatureHelpResponse,
    TextDocumentContentResponse,
    TypeDefinitionResponse,
    TypeHierarchyPrepareResponse,
    TypeHierarchySubtypesResponse,
    TypeHierarchySupertypesResponse,
    WillCreateFilesResponse,
    WillDeleteFilesResponse,
    WillRenameFilesResponse,
    WillSaveTextDocumentWaitUntilResponse,
    WorkspaceDiagnosticResponse,
    WorkspaceSymbolResponse,
    WorkspaceSymbolResolveResponse,
]
ClientResponse: TypeAlias = Union[
    ApplyWorkspaceEditResponse,
    CodeLensRefreshResponse,
    ConfigurationResponse,
    DiagnosticRefreshResponse,
    FoldingRangeRefreshResponse,
    InlayHintRefreshResponse,
    InlineValueRefreshResponse,
    RegistrationResponse,
    SemanticTokensRefreshResponse,
    ShowDocumentResponse,
    ShowMessageResponse,
    TextDocumentContentRefreshResponse,
    UnregistrationResponse,
    WorkDoneProgressCreateResponse,
    WorkspaceFoldersResponse,
]

class CancelNotification(TypedDict, closed=True):
    method: Literal["$/cancelRequest"]
    params: CancelParams

class DidChangeConfigurationNotification(TypedDict, closed=True):
    method: Literal["workspace/didChangeConfiguration"]
    params: DidChangeConfigurationParams

class DidChangeNotebookDocumentNotification(TypedDict, closed=True):
    method: Literal["notebookDocument/didChange"]
    params: DidChangeNotebookDocumentParams

class DidChangeTextDocumentNotification(TypedDict, closed=True):
    method: Literal["textDocument/didChange"]
    params: DidChangeTextDocumentParams

class DidChangeWatchedFilesNotification(TypedDict, closed=True):
    method: Literal["workspace/didChangeWatchedFiles"]
    params: DidChangeWatchedFilesParams

class DidChangeWorkspaceFoldersNotification(TypedDict, closed=True):
    method: Literal["workspace/didChangeWorkspaceFolders"]
    params: DidChangeWorkspaceFoldersParams

class DidCloseNotebookDocumentNotification(TypedDict, closed=True):
    method: Literal["notebookDocument/didClose"]
    params: DidCloseNotebookDocumentParams

class DidCloseTextDocumentNotification(TypedDict, closed=True):
    method: Literal["textDocument/didClose"]
    params: DidCloseTextDocumentParams

class DidCreateFilesNotification(TypedDict, closed=True):
    method: Literal["workspace/didCreateFiles"]
    params: CreateFilesParams

class DidDeleteFilesNotification(TypedDict, closed=True):
    method: Literal["workspace/didDeleteFiles"]
    params: DeleteFilesParams

class DidOpenNotebookDocumentNotification(TypedDict, closed=True):
    method: Literal["notebookDocument/didOpen"]
    params: DidOpenNotebookDocumentParams

class DidOpenTextDocumentNotification(TypedDict, closed=True):
    method: Literal["textDocument/didOpen"]
    params: DidOpenTextDocumentParams

class DidRenameFilesNotification(TypedDict, closed=True):
    method: Literal["workspace/didRenameFiles"]
    params: RenameFilesParams

class DidSaveNotebookDocumentNotification(TypedDict, closed=True):
    method: Literal["notebookDocument/didSave"]
    params: DidSaveNotebookDocumentParams

class DidSaveTextDocumentNotification(TypedDict, closed=True):
    method: Literal["textDocument/didSave"]
    params: DidSaveTextDocumentParams

class ExitNotification(TypedDict, closed=True):
    method: Literal["exit"]
    params: None

class InitializedNotification(TypedDict, closed=True):
    method: Literal["initialized"]
    params: InitializedParams

class LogMessageNotification(TypedDict, closed=True):
    method: Literal["window/logMessage"]
    params: LogMessageParams

class LogTraceNotification(TypedDict, closed=True):
    method: Literal["$/logTrace"]
    params: LogTraceParams

class ProgressNotification(TypedDict, closed=True):
    method: Literal["$/progress"]
    params: ProgressParams

class PublishDiagnosticsNotification(TypedDict, closed=True):
    method: Literal["textDocument/publishDiagnostics"]
    params: PublishDiagnosticsParams

class SetTraceNotification(TypedDict, closed=True):
    method: Literal["$/setTrace"]
    params: SetTraceParams

class ShowMessageNotification(TypedDict, closed=True):
    method: Literal["window/showMessage"]
    params: ShowMessageParams

class TelemetryEventNotification(TypedDict, closed=True):
    method: Literal["telemetry/event"]
    params: LSPAny

class WillSaveTextDocumentNotification(TypedDict, closed=True):
    method: Literal["textDocument/willSave"]
    params: WillSaveTextDocumentParams

class WorkDoneProgressCancelNotification(TypedDict, closed=True):
    method: Literal["window/workDoneProgress/cancel"]
    params: WorkDoneProgressCancelParams

ClientNotification: TypeAlias = Union[
    CancelNotification,
    DidChangeConfigurationNotification,
    DidChangeNotebookDocumentNotification,
    DidChangeTextDocumentNotification,
    DidChangeWatchedFilesNotification,
    DidChangeWorkspaceFoldersNotification,
    DidCloseNotebookDocumentNotification,
    DidCloseTextDocumentNotification,
    DidCreateFilesNotification,
    DidDeleteFilesNotification,
    DidOpenNotebookDocumentNotification,
    DidOpenTextDocumentNotification,
    DidRenameFilesNotification,
    DidSaveNotebookDocumentNotification,
    DidSaveTextDocumentNotification,
    ExitNotification,
    InitializedNotification,
    ProgressNotification,
    SetTraceNotification,
    WillSaveTextDocumentNotification,
    WorkDoneProgressCancelNotification,
]
ServerNotification: TypeAlias = Union[
    CancelNotification,
    LogMessageNotification,
    LogTraceNotification,
    ProgressNotification,
    PublishDiagnosticsNotification,
    ShowMessageNotification,
    TelemetryEventNotification,
]
