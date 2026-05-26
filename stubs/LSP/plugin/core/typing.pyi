from enum import Enum, IntEnum as IntEnum, IntFlag as IntFlag, StrEnum as StrEnum

class StrEnum(str, Enum):
    """
        Naive polyfill for Python 3.11's StrEnum.

        See https://docs.python.org/3.11/library/enum.html#enum.StrEnum
        """
    def __format__(self, __format_spec: str) -> str: ...
