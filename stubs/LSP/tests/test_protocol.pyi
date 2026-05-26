import unittest
from LSP.protocol import Position, Range

LSP_START_POSITION: Position
LSP_END_POSITION: Position
LSP_RANGE: Range

class PointTests(unittest.TestCase):
    def test_lsp_conversion(self) -> None: ...

class EncodingTests(unittest.TestCase):
    def test_encode(self) -> None: ...

class RequestTests(unittest.TestCase):
    def test_initialize(self) -> None: ...
    def test_shutdown(self) -> None: ...

class NotificationTests(unittest.TestCase):
    def test_initialized(self) -> None: ...
    def test_exit(self) -> None: ...
