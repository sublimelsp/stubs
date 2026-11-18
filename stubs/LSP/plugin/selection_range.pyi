from .core.protocol import Error as Error, Request as Request
from .core.registry import (
    LspTextCommand as LspTextCommand,
    get_position as get_position,
)
from .core.type_converters import range_to_region as range_to_region
from .core.views import selection_range_params as selection_range_params

class LspExpandSelectionCommand(LspTextCommand):
    capability: str
    def is_enabled(
        self,
        event: dict | None = None,
        point: int | None = None,
        fallback: bool = False,
    ) -> bool: ...
    def is_visible(
        self,
        event: dict | None = None,
        point: int | None = None,
        fallback: bool = False,
    ) -> bool: ...
    async def run(self, event: dict | None = None, fallback: bool = False) -> None: ...
