import sublime
from .core.registry import LspTextCommand as LspTextCommand

SemanticTokensInfo = tuple[str, str, str]
POPUP_CSS: str

def copy(view: sublime.View, text: str) -> None: ...

class LspShowScopeNameCommand(LspTextCommand):
    """
    Like the builtin show_scope_name command from Default/show_scope_name.py,
    but will also show semantic tokens if applicable.
    """
    capability: str
    def want_event(self) -> bool: ...
    def run(self, _: sublime.Edit) -> None: ...
    def on_navigate(self, link: str) -> None: ...
