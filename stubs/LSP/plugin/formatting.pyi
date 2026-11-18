import sublime
from ..protocol import TextEdit
from .code_actions import CodeActionsOnFormatTask as CodeActionsOnFormatTask
from .core.collections import DottedDict as DottedDict
from .core.edit import apply_text_edits as apply_text_edits
from .core.logging import exception_log as exception_log
from .core.panels import show_quick_panel as show_quick_panel
from .core.protocol import Error as Error
from .core.registry import LspTextCommand as LspTextCommand, windows as windows
from .core.sessions import (
    AbstractViewListener as AbstractViewListener,
    Session as Session,
)
from .core.settings import userprefs as userprefs
from .core.views import (
    entire_content_region as entire_content_region,
    first_selection_region as first_selection_region,
    has_single_nonempty_selection as has_single_nonempty_selection,
    text_document_formatting as text_document_formatting,
    text_document_range_formatting as text_document_range_formatting,
    text_document_ranges_formatting as text_document_ranges_formatting,
    will_save_wait_until as will_save_wait_until,
)
from .lsp_task import (
    LspTask as LspTask,
    LspTextCommandWithTasks as LspTextCommandWithTasks,
)
from typing import Any

FormatResponse = list[TextEdit] | Error | None

def get_formatter(window: sublime.Window | None, base_scope: str) -> str | None: ...
async def format_document(
    text_command: LspTextCommand, formatter: str | None = None
) -> FormatResponse: ...
async def format_selection(listener: AbstractViewListener | None) -> Error | bool: ...

class WillSaveWaitTask(LspTask):
    @classmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...
    async def run(self) -> None: ...

class FormatOnSaveTask(LspTask):
    @classmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...
    async def run(self) -> None: ...

class LspFormatDocumentCommand(LspTextCommandWithTasks):
    capability: str
    label: str
    @property
    def tasks(self) -> list[type[LspTask]]: ...
    def is_enabled(self, event: dict | None = None, select: bool = False) -> bool: ...
    async def on_tasks_completed(
        self, *, select: bool = False, **kwargs: dict[str, Any]
    ) -> None: ...
    async def select_formatter(
        self, base_scope: str, session_names: list[str]
    ) -> None: ...

class LspFormatDocumentRangeCommand(LspTextCommand):
    capability: str
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    async def run(self, event: dict | None = None) -> None: ...

class LspFormatCommand(LspTextCommand):
    def is_enabled(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def is_visible(
        self, event: dict | None = None, point: int | None = None
    ) -> bool: ...
    def description(self, **kwargs: Any) -> str: ...
    def run(self, edit: sublime.Edit, event: dict | None = None) -> None: ...
