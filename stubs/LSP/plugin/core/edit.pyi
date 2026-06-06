import sublime
from ...protocol import (
    AnnotatedTextEdit,
    ApplyWorkspaceEditResult,
    CreateFile,
    DeleteFile,
    Position,
    RenameFile,
    SnippetTextEdit,
    TextDocumentEdit,
    TextEdit,
    WorkspaceEdit,
)
from .logging import debug as debug, printf as printf
from .promise import Promise as Promise
from .protocol import UINT_MAX as UINT_MAX
from typing import Sequence, TypedDict
from typing_extensions import NotRequired, TypeGuard

WorkspaceChanges = dict[
    str,
    tuple[list[TextEdit | AnnotatedTextEdit | SnippetTextEdit], str | None, int | None],
]

class WorkspaceEditSummary(TypedDict):
    total_changes: int
    edited_files: int
    created_files: NotRequired[int]
    renamed_files: NotRequired[int]
    deleted_files: NotRequired[int]

def is_text_document_edit(
    document_change: TextDocumentEdit | CreateFile | RenameFile | DeleteFile,
) -> TypeGuard[TextDocumentEdit]: ...
def is_create_file(
    document_change: TextDocumentEdit | CreateFile | RenameFile | DeleteFile,
) -> TypeGuard[CreateFile]: ...
def is_rename_file(
    document_change: TextDocumentEdit | CreateFile | RenameFile | DeleteFile,
) -> TypeGuard[RenameFile]: ...
def is_delete_file(
    document_change: TextDocumentEdit | CreateFile | RenameFile | DeleteFile,
) -> TypeGuard[DeleteFile]: ...
def is_snippet_text_edit(
    edit: TextEdit | AnnotatedTextEdit | SnippetTextEdit,
) -> TypeGuard[SnippetTextEdit]: ...
def parse_workspace_edit(
    workspace_edit: WorkspaceEdit, label: str | None = None
) -> WorkspaceChanges: ...
def parse_lsp_position(position: Position) -> tuple[int, int]: ...
def apply_text_edits(
    view: sublime.View,
    edits: Sequence[TextEdit | AnnotatedTextEdit | SnippetTextEdit],
    *,
    label: str | None = None,
    process_placeholders: bool = False,
    required_view_version: int | None = None,
) -> Promise[sublime.View | None]: ...
def show_summary_message(
    window: sublime.Window,
    result: ApplyWorkspaceEditResult,
    summary: WorkspaceEditSummary,
) -> None: ...
