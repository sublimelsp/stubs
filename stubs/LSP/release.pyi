import argparse
from _typeshed import Incomplete
import re
from typing import Any

PACKAGE_PATH: Incomplete
MESSAGE_DIR: str
MESSAGE_PATH: Incomplete
VERSION_PATH: Incomplete
CONFIGURATION: Any
RELEASE_VERSION_PREFIX: str
PYTHON_VERSION_PATH: Any
SECTIONS: dict[str, str]
OTHER_SECTION: str
COMMIT_PATTERN: re.Pattern[str]
VERSION_PATTERN: re.Pattern[str]
BUMPS: tuple[str, str, str]

def build_messages_json(version_history: list[str]) -> None:
    """Write the version history to the messages.json file."""

def version_history() -> list[str]:
    """Return a list of all releases."""

def parse_version(version: str) -> tuple[int, int, int]:
    """Convert filename to version tuple (major, minor, patch)."""

def get_version_with_prefix(version: str) -> str: ...
def current_version() -> str: ...
def next_version(current: str, target: str) -> str:
    """Return the version for `target`, which is either a bump type or an exact version."""

def git(*args: str) -> str:
    """Run git command within current package path."""

def draft_message(version: str, previous_tag: str) -> str:
    """Draft the release message from the commits since `previous_tag`, grouped by conventional commit type."""

def prepare_release(args: argparse.Namespace) -> None:
    """Bump the version files and draft the release message for the new version."""

def print_tag(_: argparse.Namespace) -> None:
    """Print the git tag name of the current version."""

def print_notes(_: argparse.Namespace) -> None:
    """Print the GitHub release notes of the current version."""

def fail(message: str) -> None: ...
