import asyncio

from ..domain.defaults import ADDRESS_RETRY_INTERVAL_SECONDS
from .background_tasks import cancel_task
from .bridge_name_service import BridgeNameService
from .bridge_service import BridgeService
from .device_poller import DevicePoller
from .device_sync_service import DeviceSyncService
from .error_logging import run_logging_errors
from .log_function import LogFunction
from .ports import HomeKitBridge, LocalAddressFinder
from .startup_delay_service import StartupDelayService


class BridgeSupervisor:
    def __init__(
        self,
        *,
        bridge_service: BridgeService,
        device_sync_service: DeviceSyncService,
        device_poller: DevicePoller,
        bridge_name_service: BridgeNameService,
        startup_delay_service: StartupDelayService,
        find_local_address: LocalAddressFinder,
        log: LogFunction,
    ) -> None:
        self._bridge_service = bridge_service
        self._device_sync_service = device_sync_service
        self._device_poller = device_poller
        self._bridge_name_service = bridge_name_service
        self._startup_delay_service = startup_delay_service
        self._find_local_address = find_local_address
        self._log = log
        self._lifecycle_lock = asyncio.Lock()
        self._delayed_start_task: asyncio.Task[None] | None = None
        self._delayed_start_deadline: float | None = None
        self._current_address: str | None = None

    async def start(self) -> None:
        await self._bridge_name_service.load_default_name_from_homey()
        delay_seconds = (
            self._startup_delay_service.read_startup_delay().effective_seconds
        )
        local_address = self._find_local_address()
        if delay_seconds > 0 or local_address is None:
            self._schedule_delayed_start(delay_seconds)
        else:
            await self._start_bridge(local_address)

    async def shutdown(self) -> None:
        await self._cancel_delayed_start()
        await self._stop_bridge()

    async def restart_bridge(self) -> None:
        async with self._lifecycle_lock:
            await self._stop_bridge()
            await self._start_bridge()

    async def restart_bridge_on_new_address(self, address: str) -> None:
        async with self._lifecycle_lock:
            await self._stop_bridge()
            await self._start_bridge(address)

    def current_address(self) -> str | None:
        return self._current_address

    def seconds_until_start(self) -> int | None:
        if self._delayed_start_deadline is None:
            return None
        remaining_seconds = (
            self._delayed_start_deadline - asyncio.get_running_loop().time()
        )
        return max(0, round(remaining_seconds))

    def _schedule_delayed_start(self, delay_seconds: int) -> None:
        loop = asyncio.get_running_loop()
        if delay_seconds > 0:
            self._delayed_start_deadline = loop.time() + delay_seconds
            self._log(f"The bridge starts in {delay_seconds} seconds")
        self._delayed_start_task = loop.create_task(
            run_logging_errors(
                self._log,
                "Starting the bridge failed",
                lambda: self._run_delayed_start(delay_seconds),
            )
        )

    async def _run_delayed_start(self, delay_seconds: int) -> None:
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
        local_address = await self._wait_for_local_address()
        self._delayed_start_deadline = None
        async with self._lifecycle_lock:
            await self._start_bridge(local_address)

    async def _wait_for_local_address(self) -> str:
        while (local_address := self._find_local_address()) is None:
            self._log("No network address yet, trying again")
            await asyncio.sleep(ADDRESS_RETRY_INTERVAL_SECONDS)
        return local_address

    async def _cancel_delayed_start(self) -> None:
        if self._delayed_start_task is None:
            return
        await cancel_task(self._delayed_start_task)
        self._delayed_start_task = None
        self._delayed_start_deadline = None

    async def _start_bridge(self, address: str | None = None) -> None:
        bridge_address = address or self._require_local_address()
        bridge_name = self._bridge_name_service.resolve_bridge_name()
        bridge = await self._bridge_service.create_bridge(
            name=bridge_name, address=bridge_address
        )
        await self._expose_devices_and_publish(bridge)
        self._current_address = bridge_address

    def _require_local_address(self) -> str:
        local_address = self._find_local_address()
        if local_address is None:
            raise RuntimeError("No network address is available")
        return local_address

    async def _expose_devices_and_publish(self, bridge: HomeKitBridge) -> None:
        self._device_sync_service.attach_to_bridge(bridge)
        await self._device_sync_service.populate_accessories_before_publish()
        await self._bridge_service.publish_bridge()
        self._device_poller.start()
        self._log(
            f"Exposing {self._device_sync_service.exposed_accessory_count} devices"
        )

    async def _stop_bridge(self) -> None:
        self._current_address = None
        await self._device_poller.stop()
        await self._device_sync_service.detach_from_bridge()
        await self._bridge_service.stop_bridge()
