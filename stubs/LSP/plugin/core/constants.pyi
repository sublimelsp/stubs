from ...protocol import CodeActionKind, CompletionItemKind, DiagnosticSeverity, DiagnosticTag, DocumentHighlightKind, MessageType, SymbolKind
from .typing import StrEnum as StrEnum
from enum import IntEnum, IntFlag

MarkdownLangMap = dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
SublimeKind = tuple[int, str, str]
ST_CACHE_PATH: str
ST_INSTALLED_PACKAGES_PATH: str
ST_PACKAGES_PATH: str
ST_PLATFORM: str
ST_VERSION: str
ST_STORAGE_PATH: str
MARKO_MD_PARSER_VERSION: str | None
AUTO_CLOSE_BRACKETS: bool

class RequestFlags(IntFlag):
    """
    A bitflag that holds information about selecting a subset of request types.

    This is used for example to prioritize certain requests between different sessions in a multi-session configuration,
    and to mark some requests as pending for refresh in a given document.
    """
    NONE: int
    DOCUMENT_COLOR: int
    INLAY_HINT: int
    SEMANTIC_TOKENS: int
    ON_TYPE_FORMATTING: int
    CODE_LENS: int
    DIAGNOSTIC: int

class RegionKey(StrEnum):
    """Key names for use with the `View.add_regions` method."""
    CODE_ACTION: str
    DOCUMENT_LINK: str
    HOVER_HIGHLIGHT: str
    REFERENCE_HIGHLIGHT: str

class ChangeEventAction(IntEnum):
    CUT: int
    INSERT_NEWLINE: int
    OTHER: int
    PASTE: int
    REDO: int
    TYPE: int
    UNDO: int

CODE_LENS_ENABLED_KEY: str
HOVER_ENABLED_KEY: str
SHOW_DEFINITIONS_KEY: str
DIAGNOSTIC_ICON_FLAGS: int
DOCUMENT_LINK_FLAGS: int
REGIONS_INITIALIZE_FLAGS: int
SEMANTIC_TOKEN_FLAGS: int
KIND_ARRAY: SublimeKind
KIND_BOOLEAN: SublimeKind
KIND_CLASS: SublimeKind
KIND_COLOR: SublimeKind
KIND_CONSTANT: SublimeKind
KIND_CONSTRUCTOR: SublimeKind
KIND_ENUM: SublimeKind
KIND_ENUMMEMBER: SublimeKind
KIND_EVENT: SublimeKind
KIND_FIELD: SublimeKind
KIND_FILE: SublimeKind
KIND_FOLDER: SublimeKind
KIND_FUNCTION: SublimeKind
KIND_INTERFACE: SublimeKind
KIND_KEY: SublimeKind
KIND_KEYWORD: SublimeKind
KIND_METHOD: SublimeKind
KIND_MODULE: SublimeKind
KIND_NAMESPACE: SublimeKind
KIND_NULL: SublimeKind
KIND_NUMBER: SublimeKind
KIND_OBJECT: SublimeKind
KIND_OPERATOR: SublimeKind
KIND_PACKAGE: SublimeKind
KIND_PROPERTY: SublimeKind
KIND_REFERENCE: SublimeKind
KIND_SNIPPET: SublimeKind
KIND_STRING: SublimeKind
KIND_STRUCT: SublimeKind
KIND_TEXT: SublimeKind
KIND_TYPEPARAMETER: SublimeKind
KIND_UNIT: SublimeKind
KIND_VALUE: SublimeKind
KIND_VARIABLE: SublimeKind
KIND_ERROR: SublimeKind
KIND_WARNING: SublimeKind
KIND_INFORMATION: SublimeKind
KIND_HINT: SublimeKind
KIND_QUICKFIX: SublimeKind
KIND_REFACTOR: SublimeKind
KIND_SOURCE: SublimeKind
COMPLETION_KINDS: dict[CompletionItemKind, SublimeKind]
SYMBOL_KINDS: dict[SymbolKind, SublimeKind]
DIAGNOSTIC_KINDS: dict[DiagnosticSeverity, SublimeKind]
CODE_ACTION_KINDS: dict[CodeActionKind, SublimeKind]
MESSAGE_TYPE_LEVELS: dict[MessageType, str]
SUBLIME_KIND_SCOPES: dict[SublimeKind, str]
DIAGNOSTIC_SEVERITY_SCOPES: dict[DiagnosticSeverity, str]
DIAGNOSTIC_TAG_SCOPES: dict[DiagnosticTag, str]
SUPPORTED_DIAGNOSTIC_TAGS: set[DiagnosticTag]
DOCUMENT_HIGHLIGHT_KIND_SCOPES: dict[DocumentHighlightKind, str]
CODE_ACTION_ANNOTATION_SCOPE: str
CODE_LENS_ANNOTATION_SCOPE: str
SIGNATURE_HELP_FUNCTION_SCOPE: str
SIGNATURE_HELP_ACTIVE_PARAMETER_SCOPE: str
SIGNATURE_HELP_INACTIVE_PARAMETER_SCOPE: str
LIGHTBULB_SCOPE: str
COMMAND_TO_CHANGE_EVENT_ACTION: dict[str, ChangeEventAction]
LANGUAGE_IDENTIFIERS: dict[str, str]
SEMANTIC_TOKENS_MAP: dict[str, SublimeKind]
