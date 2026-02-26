import sublime
from ...protocol import MessageActionItem as MessageActionItem, MessageType, ShowMessageRequestParams
from .promise import PackagedTask as PackagedTask, Promise as Promise, ResolveFunc as ResolveFunc
from .views import show_lsp_popup as show_lsp_popup, text2html as text2html
from _typeshed import Incomplete

ICONS: dict[MessageType, str]

class MessageRequestHandler:
    view: Incomplete
    actions: Incomplete
    action_titles: Incomplete
    message: Incomplete
    message_type: Incomplete
    source: Incomplete
    def __init__(self, view: sublime.View, params: ShowMessageRequestParams, source: str) -> None: ...
    def show(self) -> Promise[MessageActionItem | None]: ...
