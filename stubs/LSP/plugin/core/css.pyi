class CSS:
    popups: str
    popups_classname: str
    notification: str
    notification_classname: str
    sheets: str
    sheets_classname: str
    inlay_hints: str
    annotations: str
    def __init__(self) -> None: ...

g_css: CSS | None

def load() -> None: ...
def css() -> CSS: ...
