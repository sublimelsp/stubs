import sublime
from ...protocol import MessageActionItem as MessageActionItem, MessageType, ShowMessageRequestParams
from .promise import PackagedTask as PackagedTask, Promise as Promise, ResolveFunc as ResolveFunc
from .views import show_lsp_popup as show_lsp_popup, text2html as text2html
ICONS: dict[MessageType, str]

class MessageRequestHandler:
    view: sublime.View
    actions: list[MessageActionItem]
    action_titles: list[str]
    message: str
    message_type: MessageType
    source: str
    def __init__(self, view: sublime.View, params: ShowMessageRequestParams, source: str) -> None: ...
    def show(self) -> Promise[MessageActionItem | None]: ...
