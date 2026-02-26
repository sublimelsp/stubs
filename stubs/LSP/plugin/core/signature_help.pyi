import sublime
from ...protocol import SignatureHelp
from .logging import debug as debug
from .registry import LspTextCommand as LspTextCommand
from .views import FORMAT_MARKUP_CONTENT as FORMAT_MARKUP_CONTENT, FORMAT_STRING as FORMAT_STRING, MarkdownLangMap as MarkdownLangMap, minihtml as minihtml
from typing import TypedDict

class SignatureHelpStyle(TypedDict):
    function_color: str
    active_parameter_color: str
    active_parameter_bold: bool
    active_parameter_underline: bool
    inactive_parameter_color: str

class LspSignatureHelpNavigateCommand(LspTextCommand):
    def want_event(self) -> bool: ...
    def run(self, _: sublime.Edit, forward: bool) -> None: ...

class LspSignatureHelpShowCommand(LspTextCommand):
    def want_event(self) -> bool: ...
    def run(self, _: sublime.Edit) -> None: ...

class SigHelp:
    """
    A quasi state-machine object that maintains which signature (a.k.a. overload) is active. The active signature is
    determined by what the end-user is doing.
    """
    def __init__(self, state: SignatureHelp, language_map: MarkdownLangMap | None, style: SignatureHelpStyle) -> None: ...
    @classmethod
    def from_lsp(cls, sighelp: SignatureHelp | None, language_map: MarkdownLangMap | None, style: SignatureHelpStyle) -> SigHelp | None:
        """Create a SigHelp state object from a server's response to textDocument/signatureHelp."""
    def render(self, view: sublime.View) -> str:
        """Render the signature help content as minihtml."""
    def active_signature_help(self) -> SignatureHelp:
        """
        Extract the state out of this state machine to send back to the language server.
        """
    def has_multiple_signatures(self) -> bool:
        """Does the current signature help state contain more than one overload?"""
    def select_signature(self, forward: bool) -> None:
        """Increment or decrement the active overload; purely chosen by the end-user."""
