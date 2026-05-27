from .progress import (
    ProgressReporter as ProgressReporter,
    ViewProgressReporter as ViewProgressReporter,
    WindowProgressReporter as WindowProgressReporter,
)
from .protocol import Request as Request
from .sessions import SessionViewProtocol as SessionViewProtocol
from typing import Any
from weakref import ref

class ActiveRequest:
    """Holds state per request."""

    weaksv: ref[SessionViewProtocol]
    request_id: int
    request: Request[Any, Any]
    canceled: bool
    progress: ProgressReporter | None
    def __init__(
        self, sv: SessionViewProtocol, request_id: int, request: Request[Any, Any]
    ) -> None: ...
    def on_request_canceled_async(self) -> None: ...
    def update_progress_async(self, params: dict[str, Any]) -> None: ...
