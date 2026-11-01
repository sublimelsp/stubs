import asyncio
import concurrent.futures
from .logging import debug as debug, exception_log as exception_log
from .promise import Promise as Promise, ResolveFunc as ResolveFunc
from .protocol import Error as Error, LSPErrorCodes as LSPErrorCodes
from contextvars import Context
from sublime_aio import T, Ts as Ts
from typing import Any, Callable, Coroutine
from typing_extensions import ParamSpec, Unpack

P = ParamSpec("P")
PortableTimeoutError = TimeoutError

def run_coroutine(
    coroutine: Coroutine[object, object, T],
) -> concurrent.futures.Future[T]:
    """
    Start the execution of a coroutine in the asyncio thread, from any thread.

    :param coroutine: a coroutine to run.
    :return: a handle to a concurrent future object.

    When you are certain you are already in the asyncio thread, then use one of:

    * [asyncio.create_task](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.create_task). The
    caveat for asyncio.create_task is that the returned [Task](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)
    object must be kept alive manually. The event loop only keeps a weak reference to the Task object.
    * `TaskContainer.create_task`: restricts the lifetime of the task to the lifetime of the `TaskContainer`. Unlike
      `asyncio.create_task`, keeps a (strong) reference to the Task object.
    """

def run_on_asyncio_thread(
    f: Callable[[Unpack[Ts]], Any], *args: Unpack[Ts], context: Context | None = None
) -> asyncio.Handle:
    """Invoke a function in the asyncio thread, from any thread."""

def run_on_threadpool(
    f: Callable[[Unpack[Ts]], T], *args: Unpack[Ts]
) -> asyncio.Future[T]:
    """Invoke a function on the loop's default thread pool. Must be invoked from the asyncio thread."""

def run_on_main_thread(
    f: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> asyncio.Future[T]:
    """
    Run a function in Sublime's main (UI) thread.

    Must be called from the asyncio thread. You must await the returned future.
    """

def run_on_worker_thread(
    f: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> asyncio.Future[T]:
    """
    Run a function in Sublime's async, or worker, thread.

    Must be called from the asyncio thread. You must await the returned future.
    """

def tick() -> asyncio.Future[None]:
    """
    Wait until at least 1 tick has occurred on the main thread.

    Must be called from the asyncio thread. You must await the returned future.
    """

def get_clipboard() -> asyncio.Future[str]:
    """
    Get the clipboard content.

    Must be called from the asyncio thread. You must await the returned future.
    """

async def gather_and_flatten_exceptions(
    *coros: Coroutine[Any, Any, list[Exception]],
) -> list[Exception]:
    """
    Takes a list of coroutines, runs them concurrently using asyncio.gather, collects all exceptions, and returns a
    flattened list of Exceptions that occurred for each coroutine. BaseExceptions are filtered out.
    """

class TaskContainer:
    """
    A [mixin class](https://en.wikipedia.org/wiki/Mixin) for adding "fire-and-forget" functionality to a class for
    starting coroutines.

    Note: don\'t forget to call `super().__init__()` when using this class.

    Ensure the `cancel_all_tasks` async function is ran before this class is destroyed.
    """
    def __init__(self) -> None: ...
    def __del__(self) -> None: ...
    async def cancel_all_tasks(self) -> list[Exception]:
        """Cancel all running tasks."""
    def create_task(
        self, coro: Coroutine[object, object, object], name: str | None = None
    ) -> asyncio.Task:
        """
        Spawn a new coroutine, to be run in the background. Not thread-safe. Must be invoked from the asyncio thread.

        This method saves a strong reference to the spawned task, unlike asyncio.
        Moreover, this method will print any exception that occured during the exception of the coroutine, if any.

        :param coro: The coroutine object to schedule.
        :param name: An optional name to give to the task. If no name has been explicitly assigned to the Task, the
        default asyncio Task implementation generates a default name during instantiation.
        :return: the newly created [Task](https://docs.python.org/3/library/asyncio-task.html#task-object) object.

        """
    def create_task_threadsafe(
        self, coro: Coroutine[object, object, object], name: str | None = None
    ) -> None:
        """
        Spawn a new coroutine, to be run in the background. Thread-safe.

        The parameters and behavior of this method are exactly the same as :py:meth`create_task`.
        """
    def create_task_and_wrap_in_promise(
        self, coro: Coroutine[T, Any, Any], name: str | None = None
    ) -> Promise[T | Error]: ...
    def create_task_and_wrap_in_compat_promise(
        self, coro: Coroutine[Any, Any, T], name: str | None = None
    ) -> Promise[T]:
        """
        Like :py:meth:`create_task_and_wrap_in_promise` but the Promise resolves with the result of the coroutine only.

        Used for keeping backwards-compatibility of Promise-based APIs that have been replaced by coroutines. If the
        coroutine raises (the exception is logged) or is cancelled, the returned Promise never resolves.
        """
