import sublime
from ...protocol import (
    MessageActionItem,
    MessageType,
    ShowMessageParams,
    ShowMessageRequestParams,
)
from .constants import MESSAGE_TYPE_LEVELS as MESSAGE_TYPE_LEVELS
from .panels import (
    PanelManager as PanelManager,
    PanelName as PanelName,
    buttons_html as buttons_html,
)
from .promise import Promise as Promise, ResolveFunc as ResolveFunc
from _typeshed import Incomplete

MAX_MESSAGES: int
INDENT: str
DISMISS_HREF: str

class MessageEntry:
    id: Incomplete
    config_name: str
    message_type: MessageType
    message: str
    timestamp: Incomplete
    actions: list[MessageActionItem]
    resolve: ResolveFunc[MessageActionItem | None] | None
    outcome: str | None
    def __init__(
        self,
        config_name: str,
        message_type: MessageType,
        message: str,
        actions: list[MessageActionItem] | None = None,
        resolve: ResolveFunc[MessageActionItem | None] | None = None,
    ) -> None: ...
    @property
    def is_pending(self) -> bool: ...
    def conclude(
        self,
        outcome: str,
        response: MessageActionItem | None = None,
        *,
        notify: bool = True,
    ) -> None: ...
    def render(self) -> str: ...
    def render_buttons(self) -> str: ...

class MessagesPanel:
    """
    Shows `window/showMessage` notifications and `window/showMessageRequest` requests in a dedicated output panel.

    Requests are rendered with buttons for each of the actions provided by the server. A request stays pending until
    the user chooses one of the actions or dismisses it, or until the server that sent it exits.

    All the state is only accessed and modified on the main thread.
    """
    def __init__(self, window: sublime.Window, panel_manager: PanelManager) -> None: ...
    def add_message(
        self, config_name: str, params: ShowMessageParams, show_panel: bool
    ) -> None: ...
    def add_request(
        self, config_name: str, params: ShowMessageRequestParams
    ) -> Promise[MessageActionItem | None]: ...
    def expire_requests(self, config_name: str) -> None:
        """Mark pending requests from the given server as no longer answerable, for example because it has exited."""
    def clear(self) -> None:
        """Remove all entries except the requests that still await a response."""
    def toggle(self) -> None: ...
    def destroy(self) -> None: ...
