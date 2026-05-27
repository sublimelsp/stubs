import sublime
from ..protocol import URI
from .core.logging import debug as debug
from .core.open import (
    open_file_uri as open_file_uri,
    open_in_browser as open_in_browser,
)
from .core.protocol import Request as Request
from .core.registry import (
    LspTextCommand as LspTextCommand,
    get_position as get_position,
)

class LspOpenLinkCommand(LspTextCommand):
    capability: str
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def run(self, edit: sublime.Edit, event: dict | None = None) -> None: ...
    def open_target(self, target: URI) -> None: ...
