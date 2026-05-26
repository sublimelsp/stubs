import argparse

PACKAGE_PATH: str
MESSAGE_DIR: str
MESSAGE_PATH: str
CONFIGURATION: str
RELEASE_BRANCH: str
GITHUB_REPO: str
RELEASE_VERSION_PREFIX: str
SETTINGS: str
PYTHON_VERSION_PATH: str

def get_message(fname: str) -> str: ...
def put_message(fname: str, text: str) -> None: ...
def build_messages_json(version_history: list[str]) -> None:
    """Write the version history to the messages.json file."""
def version_history() -> list[str]:
    """Return a list of all releases."""
def parse_version(version: str) -> tuple[int, int, int]:
    """Convert filename to version tuple (major, minor, patch)."""
def get_version_with_prefix(version: str) -> str: ...
def git(*args: str) -> str | None:
    """Run git command within current package path."""
def commit_release(version: str) -> None:
    """Create a 'Cut <version>' commit and tag."""
def build_release(_: argparse.Namespace) -> None:
    """Build the new release locally."""
def publish_release(args: argparse.Namespace) -> None:
    """Publish the new release."""
