import sublime
from .core.open import (
    open_file_uri as open_file_uri,
    open_in_browser as open_in_browser,
)
from .core.protocol import Request as Request
from .core.registry import (
    LspTextCommand as LspTextCommand,
    get_position as get_position,
)
from .core.sessions import Session as Session
from .core.settings import userprefs as userprefs
from .core.url import parse_uri as parse_uri
from .core.views import (
    range_to_region as range_to_region,
    text_document_identifier as text_document_identifier,
)

class LspOpenLinkCommand(LspTextCommand):
    capability: str
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def run(
        self, edit: sublime.Edit, event: dict | None = None, point: int | None = None
    ) -> None: ...
