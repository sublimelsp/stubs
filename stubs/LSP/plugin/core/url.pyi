import sublime
from ...protocol import CodeAction, Command, DocumentUri, URI
from .constants import (
    ST_INSTALLED_PACKAGES_PATH as ST_INSTALLED_PACKAGES_PATH,
    ST_PACKAGES_PATH as ST_PACKAGES_PATH,
)

CODE_ACTION_SCHEME: str

def normalize_uri(uri: DocumentUri) -> DocumentUri: ...
def filename_to_uri(file_name: str) -> str:
    """Convert a file name obtained from view.file_name() into an URI."""

def view_to_uri(view: sublime.View) -> str: ...
def uri_to_filename(uri: str) -> str:
    """
    DEPRECATED: An URI associated to a view does not necessarily have a "file:" scheme.
    Use parse_uri instead.
    """

def parse_uri(uri: str) -> tuple[str, str]:
    """
    Parses an URI into a tuple where the first element is the URI scheme. The
    second element is the local filesystem path if the URI is a file URI,
    otherwise the second element is the original URI.
    """

def unparse_uri(parsed_uri: tuple[str, str]) -> str:
    """Reverse of `parse_uri()`."""

def encode_code_action_uri(
    session_name: str, version: int, action: Command | CodeAction
) -> URI: ...
def decode_code_action_uri(uri: URI) -> tuple[str, int, Command | CodeAction]: ...
