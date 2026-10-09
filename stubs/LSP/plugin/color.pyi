import sublime
from ..protocol import ColorInformation, ColorPresentation as ColorPresentation
from .core.edit import apply_text_edits as apply_text_edits
from .core.protocol import Request as Request
from .core.registry import LspTextCommand as LspTextCommand
from .core.type_converters import range_to_region as range_to_region
from .core.views import text_document_identifier as text_document_identifier

class LspColorPresentationCommand(LspTextCommand):
    capability: str
    def run(self, edit: sublime.Edit, color_information: ColorInformation) -> None: ...
    def want_event(self) -> bool: ...
