from ...protocol import (
    CodeActionKind,
    CompletionItemKind,
    DiagnosticSeverity,
    DiagnosticTag,
    DocumentHighlightKind,
    MessageType,
    SymbolKind,
)
from .typing import StrEnum as StrEnum
from _typeshed import Incomplete
from enum import IntEnum, IntFlag

MarkdownLangMap = dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
SublimeKind = tuple[int, str, str]
ST_CACHE_PATH: Incomplete
ST_INSTALLED_PACKAGES_PATH: Incomplete
ST_PACKAGES_PATH: Incomplete
ST_PLATFORM: Incomplete
ST_VERSION: int
ST_STORAGE_PATH: Incomplete
MARKO_MD_PARSER_VERSION: str | None
AUTO_CLOSE_BRACKETS: Incomplete

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
DIAGNOSTIC_ICON_FLAGS: Incomplete
DOCUMENT_LINK_FLAGS: Incomplete
REGIONS_INITIALIZE_FLAGS: Incomplete
SEMANTIC_TOKEN_FLAGS: Incomplete
KIND_ARRAY: Incomplete
KIND_BOOLEAN: Incomplete
KIND_CLASS: Incomplete
KIND_COLOR: Incomplete
KIND_CONSTANT: Incomplete
KIND_CONSTRUCTOR: Incomplete
KIND_ENUM: Incomplete
KIND_ENUMMEMBER: Incomplete
KIND_EVENT: Incomplete
KIND_FIELD: Incomplete
KIND_FILE: Incomplete
KIND_FOLDER: Incomplete
KIND_FUNCTION: Incomplete
KIND_INTERFACE: Incomplete
KIND_KEY: Incomplete
KIND_KEYWORD: Incomplete
KIND_METHOD: Incomplete
KIND_MODULE: Incomplete
KIND_NAMESPACE: Incomplete
KIND_NULL: Incomplete
KIND_NUMBER: Incomplete
KIND_OBJECT: Incomplete
KIND_OPERATOR: Incomplete
KIND_PACKAGE: Incomplete
KIND_PROPERTY: Incomplete
KIND_REFERENCE: Incomplete
KIND_SNIPPET: Incomplete
KIND_STRING: Incomplete
KIND_STRUCT: Incomplete
KIND_TEXT: Incomplete
KIND_TYPEPARAMETER: Incomplete
KIND_UNIT: Incomplete
KIND_VALUE: Incomplete
KIND_VARIABLE: Incomplete
KIND_ERROR: Incomplete
KIND_WARNING: Incomplete
KIND_INFORMATION: Incomplete
KIND_HINT: Incomplete
KIND_QUICKFIX: Incomplete
KIND_REFACTOR: Incomplete
KIND_SOURCE: Incomplete
COMPLETION_KINDS: dict[CompletionItemKind, SublimeKind]
SYMBOL_KINDS: dict[SymbolKind, SublimeKind]
DIAGNOSTIC_KINDS: dict[DiagnosticSeverity, SublimeKind]
CODE_ACTION_KINDS: dict[CodeActionKind, SublimeKind]
MESSAGE_TYPE_LEVELS: dict[MessageType, str]
SUBLIME_KIND_SCOPES: dict[SublimeKind, str]
DIAGNOSTIC_SEVERITY_SCOPES: dict[DiagnosticSeverity, str]
DIAGNOSTIC_TAG_SCOPES: dict[DiagnosticTag, str]
SUPPORTED_DIAGNOSTIC_TAGS: list
DOCUMENT_HIGHLIGHT_KIND_SCOPES: dict[DocumentHighlightKind, str]
CODE_ACTION_ANNOTATION_SCOPE: str
CODE_LENS_ANNOTATION_SCOPE: str
SIGNATURE_HELP_FUNCTION_SCOPE: str
SIGNATURE_HELP_ACTIVE_PARAMETER_SCOPE: str
SIGNATURE_HELP_INACTIVE_PARAMETER_SCOPE: str
LIGHTBULB_SCOPE: str
COMMAND_TO_CHANGE_EVENT_ACTION: dict[str, ChangeEventAction]
LANGUAGE_IDENTIFIERS: dict[str, str]
SEMANTIC_TOKENS_MAP: dict
