from ..protocol import ColorInformation, ColorPresentation as ColorPresentation
from .core.edit import apply_text_edits as apply_text_edits
from .core.panels import show_quick_panel as show_quick_panel
from .core.protocol import Error as Error, Request as Request
from .core.registry import LspTextCommand as LspTextCommand
from .core.type_converters import range_to_region as range_to_region
from .core.views import text_document_identifier as text_document_identifier

class LspColorPresentationCommand(LspTextCommand):
    capability: str
    async def run(self, color_information: ColorInformation) -> None: ...
    def want_event(self) -> bool: ...
