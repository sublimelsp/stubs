import sublime
import sublime_plugin
from ..protocol import FileRename
from .core.aio import run_on_main_thread as run_on_main_thread
from .core.edit import show_summary_message as show_summary_message
from .core.logging import debug as debug
from .core.open import open_file_uri as open_file_uri
from .core.protocol import Error as Error, Request as Request
from .core.registry import LspWindowCommand as LspWindowCommand
from .core.types import match_file_operation_filters as match_file_operation_filters
from .core.url import filename_to_uri as filename_to_uri
from .edit import prompt_for_workspace_edits as prompt_for_workspace_edits
from typing import Any
from typing_extensions import NotRequired, TypedDict
from pathlib import Path

class RenamePathInputHandler(sublime_plugin.TextInputHandler):
    path: Path[str]
    def __init__(self, path: str) -> None: ...
    def name(self) -> str: ...
    def placeholder(self) -> str: ...
    def initial_text(self) -> str: ...
    def initial_selection(self) -> list[tuple[int, int]]: ...
    def validate(self, path: str) -> bool: ...

class LspRenamePathInputArgs(TypedDict, closed=True):
    paths: NotRequired[list[str]]
    new_name: NotRequired[str]
    prompt_workspace_edits: NotRequired[bool]

class LspRenamePathCommand(LspWindowCommand):
    capability: str
    @staticmethod
    def is_case_change(path_a: str, path_b: str) -> bool: ...
    def is_visible(self, **kwargs: dict[str, Any]) -> bool: ...
    def want_event(self) -> bool: ...
    def input(
        self, args: LspRenamePathInputArgs
    ) -> sublime_plugin.TextInputHandler | None: ...
    async def run(
        self,
        new_name: str,
        paths: list[str] | None = None,
        prompt_workspace_edits: bool = True,
    ) -> None: ...
    async def apply_will_rename_edits(
        self, file_rename: FileRename, label: str
    ) -> bool:
        """
        Request and apply the WorkspaceEdit from the workspace/willRenameFiles request.

        Returns whether the file rename should proceed.
        """
    async def rename_path(self, old: str, new: str) -> bool: ...
    def restore_view(
        self,
        selection: list[sublime.Region],
        group: tuple[int, int],
        view: sublime.View | None,
    ) -> None: ...
    def focus_view(self, path: str | None) -> None: ...
