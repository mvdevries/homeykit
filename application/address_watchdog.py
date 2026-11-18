from collections.abc import Awaitable, Callable

from ..domain.defaults import ADDRESS_CHECK_INTERVAL_SECONDS
from .background_tasks import PeriodicTask
from .log_function import LogFunction
from .ports import LocalAddressFinder


class AddressWatchdog:
    def __init__(
        self,
        *,
        read_current_address: Callable[[], str | None],
        on_address_changed: Callable[[str], Awaitable[None]],
        find_address: LocalAddressFinder,
        log: LogFunction,
        interval_seconds: float = ADDRESS_CHECK_INTERVAL_SECONDS,
    ) -> None:
        self._read_current_address = read_current_address
        self._on_address_changed = on_address_changed
        self._find_address = find_address
        self._log = log
        self._periodic_task = PeriodicTask(
            interval_seconds=interval_seconds,
            action=self.check_address_once,
            log=log,
            failure_message="Checking the IP address failed",
        )

    def start(self) -> None:
        self._periodic_task.start()

    async def stop(self) -> None:
        await self._periodic_task.stop()

    async def check_address_once(self) -> bool:
        current_address = self._read_current_address()
        found_address = self._find_address()
        if found_address is None or not self._address_has_changed(
            current_address, found_address
        ):
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
