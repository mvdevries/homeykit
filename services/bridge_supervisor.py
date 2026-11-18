from ..config.bridge_defaults import BRIDGE_DEFAULT_NAME
from ..domain.log_function import LogFunction
from .bridge_service import BridgeService, RunningBridge
from .device_sync_service import DeviceSyncService


class BridgeSupervisor:
    def __init__(
        self,
        *,
        bridge_service: BridgeService,
        device_sync_service: DeviceSyncService,
        log: LogFunction,
    ) -> None:
        self._bridge_service = bridge_service
        self._device_sync_service = device_sync_service
        self._log = log

    async def start(self) -> None:
        await self._start_bridge()

    async def shutdown(self) -> None:
        await self._stop_bridge()

    async def _start_bridge(self) -> None:
        running_bridge = await self._bridge_service.create_bridge(name=BRIDGE_DEFAULT_NAME)
        await self._expose_devices_and_publish(running_bridge)

    async def _expose_devices_and_publish(self, running_bridge: RunningBridge) -> None:
        self._device_sync_service.attach_to_bridge(running_bridge)
        await self._device_sync_service.populate_accessories_before_publish()
        await self._bridge_service.publish_bridge()
        self._device_sync_service.mark_bridge_published()
        self._device_sync_service.start_polling()
        self._log(f"Exposing {self._device_sync_service.exposed_accessory_count} devices")

    async def _stop_bridge(self) -> None:
        await self._device_sync_service.detach_from_bridge()
        await self._bridge_service.stop_bridge()
