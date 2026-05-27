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
from enum import IntEnum, IntFlag
import sublime

MarkdownLangMap = dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
SublimeKind = tuple[int, str, str]
ST_CACHE_PATH: str
ST_INSTALLED_PACKAGES_PATH: str
ST_PACKAGES_PATH: str
ST_PLATFORM: str
ST_VERSION: int
ST_STORAGE_PATH: str
MARKO_MD_PARSER_VERSION: str | None
AUTO_CLOSE_BRACKETS: tuple[str, str, str]

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
DIAGNOSTIC_ICON_FLAGS: sublime.RegionFlags
DOCUMENT_LINK_FLAGS: sublime.RegionFlags
REGIONS_INITIALIZE_FLAGS: sublime.RegionFlags
SEMANTIC_TOKEN_FLAGS: sublime.RegionFlags
KIND_ARRAY: tuple[sublime.KindId, str, str]
KIND_BOOLEAN: tuple[sublime.KindId, str, str]
KIND_CLASS: tuple[sublime.KindId, str, str]
KIND_COLOR: tuple[sublime.KindId, str, str]
KIND_CONSTANT: tuple[sublime.KindId, str, str]
KIND_CONSTRUCTOR: tuple[sublime.KindId, str, str]
KIND_ENUM: tuple[sublime.KindId, str, str]
KIND_ENUMMEMBER: tuple[sublime.KindId, str, str]
KIND_EVENT: tuple[sublime.KindId, str, str]
KIND_FIELD: tuple[sublime.KindId, str, str]
KIND_FILE: tuple[sublime.KindId, str, str]
KIND_FOLDER: tuple[sublime.KindId, str, str]
KIND_FUNCTION: tuple[sublime.KindId, str, str]
KIND_INTERFACE: tuple[sublime.KindId, str, str]
KIND_KEY: tuple[sublime.KindId, str, str]
KIND_KEYWORD: tuple[sublime.KindId, str, str]
KIND_METHOD: tuple[sublime.KindId, str, str]
KIND_MODULE: tuple[sublime.KindId, str, str]
KIND_NAMESPACE: tuple[sublime.KindId, str, str]
KIND_NULL: tuple[sublime.KindId, str, str]
KIND_NUMBER: tuple[sublime.KindId, str, str]
KIND_OBJECT: tuple[sublime.KindId, str, str]
KIND_OPERATOR: tuple[sublime.KindId, str, str]
KIND_PACKAGE: tuple[sublime.KindId, str, str]
KIND_PROPERTY: tuple[sublime.KindId, str, str]
KIND_REFERENCE: tuple[sublime.KindId, str, str]
KIND_SNIPPET: tuple[sublime.KindId, str, str]
KIND_STRING: tuple[sublime.KindId, str, str]
KIND_STRUCT: tuple[sublime.KindId, str, str]
KIND_TEXT: tuple[sublime.KindId, str, str]
KIND_TYPEPARAMETER: tuple[sublime.KindId, str, str]
KIND_UNIT: tuple[sublime.KindId, str, str]
KIND_VALUE: tuple[sublime.KindId, str, str]
KIND_VARIABLE: tuple[sublime.KindId, str, str]
KIND_ERROR: tuple[sublime.KindId, str, str]
KIND_WARNING: tuple[sublime.KindId, str, str]
KIND_INFORMATION: tuple[sublime.KindId, str, str]
KIND_HINT: tuple[sublime.KindId, str, str]
KIND_QUICKFIX: tuple[sublime.KindId, str, str]
KIND_REFACTOR: tuple[sublime.KindId, str, str]
KIND_SOURCE: tuple[sublime.KindId, str, str]
COMPLETION_KINDS: dict[CompletionItemKind, SublimeKind]
SYMBOL_KINDS: dict[SymbolKind, SublimeKind]
DIAGNOSTIC_KINDS: dict[DiagnosticSeverity, SublimeKind]
CODE_ACTION_KINDS: dict[CodeActionKind, SublimeKind]
MESSAGE_TYPE_LEVELS: dict[MessageType, str]
SUBLIME_KIND_SCOPES: dict[SublimeKind, str]
DIAGNOSTIC_SEVERITY_SCOPES: dict[DiagnosticSeverity, str]
DIAGNOSTIC_TAG_SCOPES: dict[DiagnosticTag, str]
SUPPORTED_DIAGNOSTIC_TAGS: list[DiagnosticTag]
DOCUMENT_HIGHLIGHT_KIND_SCOPES: dict[DocumentHighlightKind, str]
CODE_ACTION_ANNOTATION_SCOPE: str
CODE_LENS_ANNOTATION_SCOPE: str
SIGNATURE_HELP_FUNCTION_SCOPE: str
SIGNATURE_HELP_ACTIVE_PARAMETER_SCOPE: str
SIGNATURE_HELP_INACTIVE_PARAMETER_SCOPE: str
LIGHTBULB_SCOPE: str
COMMAND_TO_CHANGE_EVENT_ACTION: dict[str, ChangeEventAction]
LANGUAGE_IDENTIFIERS: dict[str, str]
SEMANTIC_TOKENS_MAP: dict[str, str]
