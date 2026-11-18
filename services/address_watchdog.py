import asyncio
import contextlib
from collections.abc import Awaitable, Callable

from ..config.network_defaults import ADDRESS_CHECK_INTERVAL_SECONDS
from ..domain.log_function import LogFunction
from ..network.local_address import find_local_ip_address


class AddressWatchdog:
    def __init__(
        self,
        *,
        read_current_address: Callable[[], str | None],
        on_address_changed: Callable[[str], Awaitable[None]],
        log: LogFunction,
        interval_seconds: float = ADDRESS_CHECK_INTERVAL_SECONDS,
        find_address: Callable[[], str | None] | None = None,
    ) -> None:
        self._read_current_address = read_current_address
        self._on_address_changed = on_address_changed
        self._log = log
        self._interval_seconds = interval_seconds
        self._find_address = find_address or find_local_ip_address
        self._watch_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._watch_task is None:
            self._watch_task = asyncio.get_running_loop().create_task(
                self._watch_loop()
            )

    async def stop(self) -> None:
        if self._watch_task is None:
            return
        self._watch_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._watch_task
        self._watch_task = None

    async def check_address_once(self) -> bool:
        current_address = self._read_current_address()
        found_address = self._find_address()
        if not self._address_has_changed(current_address, found_address):
            return False
        self._log(
            f"IP address changed from {current_address} to {found_address}, "
            "the bridge is restarted"
        )
        await self._on_address_changed(found_address)
        return True

    @staticmethod
    def _address_has_changed(current: str | None, found: str | None) -> bool:
        if current is None or found is None:
            return False
        return found != current

    async def _watch_loop(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            await self._check_logging_errors()

    async def _check_logging_errors(self) -> None:
        try:
            await self.check_address_once()
        except Exception as error:
            self._log(f"Checking the IP address failed: {error}")
