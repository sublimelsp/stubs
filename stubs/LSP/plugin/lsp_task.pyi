import sublime
from .core.registry import LspTextCommand as LspTextCommand
from .core.settings import userprefs as userprefs
from abc import ABC, abstractmethod
from typing import Any, Callable

class LspTask(ABC):
    """
    Base class for tasks that run from `LspTextCommandWithTasks` command.

    Note: The whole task runs on the async thread.
    """
    @classmethod
    @abstractmethod
    def is_applicable(cls, view: sublime.View) -> bool: ...
    def __init__(
        self, task_runner: LspTextCommand, on_done: Callable[[], None]
    ) -> None: ...
    def run_async(self) -> None: ...
    def cancel(self) -> None: ...

class TasksRunner:
    def __init__(
        self,
        text_command: LspTextCommand,
        tasks: list[type[LspTask]],
        on_complete: Callable[[], None],
    ) -> None: ...
    def run(self) -> None: ...
    def cancel(self) -> None: ...

class LspTextCommandWithTasks(LspTextCommand, ABC):
    @property
    @abstractmethod
    def tasks(self) -> list[type[LspTask]]:
        """Returns tasks to run when command is run."""
    def __init__(self, view: sublime.View) -> None: ...
    def on_before_tasks(self) -> None:
        """Override this to execute code before the task handler starts."""
    def on_tasks_completed(self, **kwargs: dict[str, Any]) -> None:
        """Override this to execute code when all tasks are completed."""
    def run(self, edit: sublime.Edit, **kwargs: dict[str, Any]) -> None: ...
