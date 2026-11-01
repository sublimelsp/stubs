import sublime
from .core.aio import (
    PortableTimeoutError as PortableTimeoutError,
    run_coroutine as run_coroutine,
)
from .core.registry import LspTextCommand as LspTextCommand
from .core.settings import userprefs as userprefs
from abc import ABC, abstractmethod
from typing import Any

class LspTask(ABC):
    """
    Base class for tasks that run from `LspTextCommandWithTasks` command.

    Note: The whole task runs on the asyncio thread.
    """
    @classmethod
    @abstractmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...
    def __init__(self, task_runner: LspTextCommand) -> None: ...
    @property
    def status_key(self) -> str: ...
    async def run(self) -> None: ...

class LspTextCommandWithTasks(LspTextCommand, ABC):
    @property
    @abstractmethod
    def tasks(self) -> list[type[LspTask]]:
        """Tasks to run when the command is run."""
    def __init__(self, view: sublime.View) -> None: ...
    async def on_before_tasks(self) -> None:
        """Override this to execute code before the task handler starts."""
    async def on_tasks_completed(self, **kwargs: dict[str, Any]) -> None:
        """Override this to execute code when all tasks are completed."""
    def run(self, edit: sublime.Edit, **kwargs: dict[str, Any]) -> None: ...
