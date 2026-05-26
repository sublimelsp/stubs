from .setup import TIMEOUT_TIME as TIMEOUT_TIME, YieldPromise as YieldPromise, add_config as add_config, close_test_view as close_test_view, expand as expand, make_stdio_test_config as make_stdio_test_config, make_tcp_client_test_config as make_tcp_client_test_config, make_tcp_server_test_config as make_tcp_server_test_config, remove_config as remove_config
from _typeshed import Incomplete
from typing import Generator
from unittesting import DeferrableTestCase

class WindowDocumentHandlerTests(DeferrableTestCase):
    def ensure_document_listener_created(self) -> bool: ...
    window: Incomplete
    session1: Incomplete
    session2: Incomplete
    session3: Incomplete
    config1: Incomplete
    config2: Incomplete
    config3: Incomplete
    wm: Incomplete
    def setUp(self) -> Generator: ...
    view: Incomplete
    def test_sends_did_open_to_multiple_sessions(self) -> Generator: ...
    def doCleanups(self) -> Generator: ...
    def await_message(self, method: str) -> Generator: ...
