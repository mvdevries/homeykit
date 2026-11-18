from collections.abc import Awaitable, Callable

from .log_function import LogFunction


async def run_logging_errors[Result](
    log: LogFunction, failure_message: str, action: Callable[[], Awaitable[Result]]
) -> Result | None:
    try:
        return await action()
    except Exception as error:
        log(f"{failure_message}: {error}")
        return None
