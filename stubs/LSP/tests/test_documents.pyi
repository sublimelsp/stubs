import sublime
from .setup import TIMEOUT_TIME as TIMEOUT_TIME, YieldPromise as YieldPromise, add_config as add_config, close_test_view as close_test_view, expand as expand, make_stdio_test_config as make_stdio_test_config, make_tcp_client_test_config as make_tcp_client_test_config, make_tcp_server_test_config as make_tcp_server_test_config, remove_config as remove_config
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import ClientConfig
from LSP.plugin.core.windows import WindowManager
from typing import Generator
from unittesting import DeferrableTestCase

class WindowDocumentHandlerTests(DeferrableTestCase):
    def ensure_document_listener_created(self) -> bool: ...
    window: sublime.Window
    session1: Session | None
    session2: Session | None
    session3: Session | None
    config1: ClientConfig
    config2: ClientConfig
    config3: ClientConfig
    wm: WindowManager | None
    def setUp(self) -> Generator: ...
    view: sublime.View
    def test_sends_did_open_to_multiple_sessions(self) -> Generator: ...
    def doCleanups(self) -> Generator: ...
    def await_message(self, method: str) -> Generator: ...
