from .progress import (
    ProgressReporter as ProgressReporter,
    ViewProgressReporter as ViewProgressReporter,
    WindowProgressReporter as WindowProgressReporter,
)
from .protocol import Request as Request
from .sessions import (
    RequestController as RequestController,
    SessionViewProtocol as SessionViewProtocol,
)
from typing import Any, Coroutine
from weakref import ref

class ActiveRequest:
    """Holds state per request."""

    weaksv: ref[SessionViewProtocol]
    controller: RequestController
    request: Request[Any, Any]
    progress: ProgressReporter | None
    def __init__(
        self,
        sv: SessionViewProtocol,
        controller: RequestController,
        request: Request[Any, Any],
    ) -> None: ...
    def cancel(self) -> Coroutine[None, None, int | None]: ...
    def on_request_canceled_async(self) -> None: ...
    def update_progress_async(self, params: dict[str, Any]) -> None: ...
