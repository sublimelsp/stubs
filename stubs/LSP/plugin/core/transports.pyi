import asyncio
import asyncio.subprocess
import weakref
from .aio import (
    PortableTimeoutError as PortableTimeoutError,
    TaskContainer as TaskContainer,
)
from .constants import ST_PLATFORM as ST_PLATFORM
from .logging import debug as debug, exception_log as exception_log
from .protocol import JSONRPCMessage as JSONRPCMessage
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Callable
import subprocess

TCP_CONNECT_TIMEOUT: int

class StopLoopError(Exception): ...

class TransportConfig(ABC):
    """Config object that can start the transport."""
    @staticmethod
    def resolve_launch_config(
        command: list[str], env: dict[str, str] | None, variables: dict[str, str]
    ) -> LaunchConfig:
        """
        Given the state of this transport configuration, and the provided command/env/vars, create a small object
        that has resolved all variables to a concrete command to run.
        """
    @abstractmethod
    async def start(
        self,
        command: list[str] | None,
        env: dict[str, str] | None,
        cwd: str | None,
        variables: dict[str, str],
        callbacks: TransportCallbacks,
    ) -> TransportWrapper:
        """Start a communication channel with the language server."""

class StdioTransportConfig(TransportConfig):
    """
    The simplest of transport configs: launch the subprocess and communicate with it over standard I/O. This transport
    config requires a "command". This is the default transport config when only a "command" is specified in the
    ClientConfig.
    """
    async def start(
        self,
        command: list[str] | None,
        env: dict[str, str] | None,
        cwd: str | None,
        variables: dict[str, str],
        callbacks: TransportCallbacks,
    ) -> TransportWrapper: ...

class TcpClientTransportConfig(TransportConfig):
    """
    Transport for communicating to a language server that expects incoming client connections. The language server acts
    as the TCP server, this text editor acts as the TCP client. One can have a "command" with this transport
    configuration. In that case the subprocess is launched, and then the TCP connection is attempted. If no "command" is
    given, a TCP connection is still made. This can be used for cases where the language server is already running as
    part of some larger application, like Godot Editor.
    """
    def __init__(self, port: int | None) -> None: ...
    async def start(
        self,
        command: list[str] | None,
        env: dict[str, str] | None,
        cwd: str | None,
        variables: dict[str, str],
        callbacks: TransportCallbacks,
    ) -> TransportWrapper: ...

class TcpServerTransportConfig(TransportConfig):
    """
    Transport for communicating to a language server over TCP. The difference, however, is that this transport will
    start a TCP listener socket accepting new TCP client connections. Once a client connects to this text editor acting
    as the TCP server, we\'ll assume it\'s the language server we just launched. As such, this tranport requires a
    "command" for starting the language server subprocess.
    """
    def __init__(self, port: int | None) -> None: ...
    cv: Incomplete
    wrapper: Incomplete
    process: Incomplete
    error_reader: Incomplete
    async def start(
        self,
        command: list[str] | None,
        env: dict[str, str] | None,
        cwd: str | None,
        variables: dict[str, str],
        callbacks: TransportCallbacks,
    ) -> TransportWrapper: ...

class TransportCallbacks:
    async def on_transport_close(
        self, exit_code: int, exception: Exception | None
    ) -> None: ...
    async def on_payload(self, payload: JSONRPCMessage) -> None: ...
    def on_stderr_message(self, message: str) -> None: ...

class Transport(ABC):
    def __init__(
        self,
        encoder: Callable[[JSONRPCMessage], bytes],
        decoder: Callable[[bytes], JSONRPCMessage],
    ) -> None: ...
    @abstractmethod
    async def read(self) -> JSONRPCMessage: ...
    @abstractmethod
    async def write(self, payload: JSONRPCMessage) -> None: ...
    @abstractmethod
    async def write_bytes(self, payload: bytes) -> None: ...
    @abstractmethod
    async def close(self) -> None: ...

async def parse_headers(reader: asyncio.StreamReader) -> dict[str, str]: ...
async def parse_content_length(reader: asyncio.StreamReader) -> int | None: ...

class StreamTransport(Transport):
    def __init__(
        self,
        encoder: Callable[[JSONRPCMessage], bytes],
        decoder: Callable[[bytes], JSONRPCMessage],
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None: ...
    async def read(self) -> JSONRPCMessage: ...
    async def write(self, payload: JSONRPCMessage) -> None: ...
    async def write_bytes(self, payload: bytes) -> None: ...
    async def close(self) -> None: ...

class TransportWrapper(TaskContainer):
    """
    Double dispatch-like class that takes a (subclass of) Transport, and provides to a (subclass of) TransportCallbacks
    appropriately decoded messages. The TransportWrapper is also responsible for keeping the spawned child
    process around (if any), and also keeps track of the ErrorReader. It can be the case that there is no ErrorReader,
    for instance when talking to a remote TCP language server. So it can be None.
    """
    def __init__(
        self,
        callback_object: TransportCallbacks,
        transport: Transport,
        process: asyncio.subprocess.Process | None,
        process_args: list[str] | None,
        error_reader: ErrorReader | None,
    ) -> None: ...
    @property
    def process_args(self) -> list[str] | None:
        """
        The arguments for the process launched by this wrapper, or None if there is no process launched (such as with
        a remote TCP/websocket connection).
        """
    async def send(self, payload: JSONRPCMessage) -> None: ...
    async def send_bytes(self, payload: bytes) -> None: ...
    async def close(self) -> None: ...

class LaunchConfig:
    """Small object that can start a process."""

    command: list[str]
    env: dict[str, str]
    def __init__(
        self, command: list[str], env: dict[str, str] | None = None
    ) -> None: ...
    async def start(
        self, cwd: str | None, stdin: int, stdout: int, stderr: int
    ) -> asyncio.subprocess.Process:
        """Start a process."""

class ErrorReader:
    """
    Relays log messages from a raw stream to a (subclass of) TransportCallbacks.

    Because the various transport configurations want to listen to different streams, perhaps completely separate from
    the regular RPC transport, this is wrapped in a different class. For instance, a TCP client transport communicating
    via a socket, while it listens for log messages on the stdout/stderr streams of a spawned child process.
    """
    def __init__(
        self, callback_object: TransportCallbacks, reader: asyncio.StreamReader
    ) -> None: ...
    def on_transport_close(self) -> None: ...

def encode_json(data: JSONRPCMessage) -> bytes: ...
def decode_json(message: bytes) -> JSONRPCMessage: ...

g_subprocesses: weakref.WeakSet[asyncio.subprocess.Process]

async def kill_all_subprocesses() -> None: ...
