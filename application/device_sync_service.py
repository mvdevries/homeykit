import asyncio
from collections.abc import Iterable

from ..domain.homey_device import HomeyDevice
from .background_tasks import TaskSet
from .error_logging import run_logging_errors
from .log_function import LogFunction
from .ports import (
    AccessoryIdRepository,
    DevicesGateway,
    DeviceSupport,
    ExposedDevicesRepository,
    HomeKitBridge,
)


class DeviceSyncService:
    def __init__(
        self,
        *,
        devices_gateway: DevicesGateway,
        exposed_devices_repository: ExposedDevicesRepository,
        accessory_id_repository: AccessoryIdRepository,
        device_support: DeviceSupport,
        log: LogFunction,
    ) -> None:
        self._devices_gateway = devices_gateway
        self._exposed_devices_repository = exposed_devices_repository
        self._accessory_id_repository = accessory_id_repository
        self._device_support = device_support
        self._log = log
        self._bridge: HomeKitBridge | None = None
        self._refresh_tasks = TaskSet()
        self._sync_lock = asyncio.Lock()

    @property
    def exposed_accessory_count(self) -> int:
        if self._bridge is None:
            return 0
        return len(self._bridge.exposed_device_ids)

    def attach_to_bridge(self, bridge: HomeKitBridge) -> None:
        self._bridge = bridge
        bridge.set_device_written_listener(self.refresh_device_soon)

    async def detach_from_bridge(self) -> None:
        await self._refresh_tasks.cancel_all()
        self._bridge = None

    async def populate_accessories_before_publish(self) -> None:
        await run_logging_errors(
            self._log, "First device synchronization failed", self.synchronize_once
        )

    async def save_exposed_device_ids_and_synchronize(
        self, device_ids: Iterable[str]
    ) -> None:
        await self._exposed_devices_repository.save_exposed_device_ids(device_ids)
        if self._bridge is not None:
            await self.synchronize_once()

    async def synchronize_once(self) -> None:
        async with self._sync_lock:
            devices = await self._devices_gateway.fetch_all_devices()
            await self._synchronize_with_devices(devices)

    def refresh_device_soon(self, device_id: str) -> None:
        self._refresh_tasks.start(self._refresh_single_device(device_id))

    async def _synchronize_with_devices(self, devices: dict[str, HomeyDevice]) -> None:
        bridge = self._require_bridge()
        exposed_ids = self._exposed_devices_repository.read_exposed_device_ids()
        removed_any = self._remove_accessories_that_should_not_exist(
            bridge, devices, exposed_ids
        )
        added_any = await self._add_missing_accessories(bridge, devices, exposed_ids)
        self._update_existing_accessories(bridge, devices)
        if removed_any or added_any:
            bridge.announce_configuration_change()

    def _remove_accessories_that_should_not_exist(
        self,
        bridge: HomeKitBridge,
        devices: dict[str, HomeyDevice],
        exposed_ids: frozenset[str],
    ) -> bool:
        obsolete_device_ids = [
            device_id
            for device_id in bridge.exposed_device_ids
            if not self._should_have_accessory(device_id, devices, exposed_ids)
        ]
        for device_id in obsolete_device_ids:
            bridge.remove_device(device_id)
        return bool(obsolete_device_ids)

    def _should_have_accessory(
        self,
        device_id: str,
        devices: dict[str, HomeyDevice],
        exposed_ids: frozenset[str],
    ) -> bool:
        device = devices.get(device_id)
        if device is None or device_id not in exposed_ids:
            return False
        return self._device_support.is_supported(device)

    async def _add_missing_accessories(
        self,
        bridge: HomeKitBridge,
        devices: dict[str, HomeyDevice],
        exposed_ids: frozenset[str],
    ) -> bool:
        added_any = False
        for device_id in sorted(exposed_ids):
            device = devices.get(device_id)
            if device is None or device_id in bridge.exposed_device_ids:
                continue
            if not self._device_support.is_supported(device):
                continue
            await self._add_device(bridge, device)
            added_any = True
        return added_any

    async def _add_device(self, bridge: HomeKitBridge, device: HomeyDevice) -> None:
        accessory_id = await self._accessory_id_repository.get_or_assign_accessory_id(
            device.id
        )
        bridge.add_device(device, accessory_id)

    @staticmethod
    def _update_existing_accessories(
        bridge: HomeKitBridge, devices: dict[str, HomeyDevice]
    ) -> None:
        for device_id in bridge.exposed_device_ids:
            bridge.update_device(devices[device_id])

    async def _refresh_single_device(self, device_id: str) -> None:
        bridge = self._bridge
        if bridge is None or device_id not in bridge.exposed_device_ids:
            return
        device = await run_logging_errors(
            self._log,
            f"Refreshing device {device_id} failed",
            lambda: self._devices_gateway.fetch_device(device_id),
        )
        if device is not None:
            bridge.update_device(device)

    def _require_bridge(self) -> HomeKitBridge:
        if self._bridge is None:
            raise RuntimeError("Device synchronization is not attached to a bridge")
        return self._bridge
