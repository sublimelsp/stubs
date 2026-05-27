import sublime
from ..protocol import DocumentUri as DocumentUri, Location, LocationLink, Position
from .core.constants import (
    ST_PACKAGES_PATH as ST_PACKAGES_PATH,
    SublimeKind as SublimeKind,
)
from .core.logging import debug as debug
from .core.sessions import Session as Session
from .core.views import (
    get_uri_and_position_from_location as get_uri_and_position_from_location,
    location_to_human_readable as location_to_human_readable,
    to_encoded_filename as to_encoded_filename,
)

def open_location_async(
    session: Session,
    location: Location | LocationLink,
    side_by_side: bool,
    force_group: bool,
    group: int = -1,
) -> None: ...
def open_basic_file(
    session: Session,
    uri: str,
    position: Position,
    flags: sublime.NewFileFlags = ...,
    group: int | None = None,
) -> sublime.View | None: ...

class LocationPicker:
    def __init__(
        self,
        view: sublime.View,
        session: Session,
        locations: list[Location] | list[LocationLink],
        side_by_side: bool,
        force_group: bool = True,
        group: int = -1,
        placeholder: str = "",
        kind: SublimeKind = ...,
        selected_index: int = -1,
    ) -> None: ...
