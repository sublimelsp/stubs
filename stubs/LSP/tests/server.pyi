import asyncio
import enum
from _typeshed import Incomplete
from typing import Any

__version__: str
StringDict = dict[str, Any]
PayloadLike = list[StringDict] | StringDict | None
ENCODING: str

class ErrorCode(enum.IntEnum):
    ParseError: int
    InvalidRequest: int
    MethodNotFound: int
    InvalidParams: int
    InternalError: int
    serverErrorStart: int
    serverErrorEnd: int
    ServerNotInitialized: int
    UnknownErrorCode: int
    RequestCancelled: int
    ContentModified: int

class Error(Exception):
    code: Incomplete
    def __init__(self, code: ErrorCode, message: str) -> None: ...
    def to_lsp(self) -> StringDict: ...
    @classmethod
    def from_lsp(cls, d: StringDict) -> Error: ...

def jsonrpc() -> StringDict: ...
def make_response(request_id: Any, params: PayloadLike) -> StringDict: ...
def make_error_response(request_id: Any, err: Error) -> StringDict: ...
def make_notification(method: str, params: PayloadLike) -> StringDict: ...
def make_request(method: str, request_id: Any, params: PayloadLike) -> StringDict: ...
def dump(payload: PayloadLike) -> bytes: ...
def content_length(line: bytes) -> int | None: ...

class MessageType:
    error: int
    warning: int
    info: int
    log: int

class StopLoopError(Exception): ...

class Request:
    async def on_error(self, err: Error) -> None: ...
    async def on_result(self, params: PayloadLike) -> None: ...

class SimpleRequest(Request):
    cv: Incomplete
    result: Incomplete
    error: Incomplete
    def __init__(self) -> None: ...
    async def on_result(self, params: PayloadLike) -> None: ...
    async def on_error(self, err: Error) -> None: ...

class Session:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None: ...
    async def request(self, method: str, params: PayloadLike) -> PayloadLike: ...
    async def run_forever(self) -> bool: ...

async def stdio() -> tuple[asyncio.StreamReader, asyncio.StreamWriter]: ...

class Mode(enum.StrEnum):
    server: str
    client: str

async def main(tcp_port: int | None = None, mode: Mode = ...) -> bool: ...
