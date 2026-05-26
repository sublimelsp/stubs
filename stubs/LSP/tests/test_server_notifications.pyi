from .setup import TextDocumentTestCase as TextDocumentTestCase
from typing import Generator

class ServerNotifications(TextDocumentTestCase):
    def test_publish_diagnostics(self) -> Generator: ...
