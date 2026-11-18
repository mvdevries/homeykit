import asyncio
import contextlib
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

from .error_logging import run_logging_errors
from .log_function import LogFunction


async def cancel_task(task: asyncio.Task[Any]) -> None:
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


class TaskSet:
    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()

    def start(self, coroutine: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        task = asyncio.get_running_loop().create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def cancel_all(self) -> None:
        for task in list(self._tasks):
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)


class PeriodicTask:
    def __init__(
        self,
        *,
        interval_seconds: float,
        action: Callable[[], Awaitable[Any]],
        log: LogFunction,
        failure_message: str,
    ) -> None:
        self._interval_seconds = interval_seconds
        self._action = action
        self._log = log
        self._failure_message = failure_message
        self._task: asyncio.Task[None] | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.get_running_loop().create_task(self._run_forever())

    async def stop(self) -> None:
        if self._task is None:
            return
        await cancel_task(self._task)
        self._task = None

    async def _run_forever(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            await run_logging_errors(self._log, self._failure_message, self._action)
