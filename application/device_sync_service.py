import asyncio
import contextlib
from collections.abc import Iterable

from ..domain.defaults import DEVICE_SYNC_INTERVAL_SECONDS
from ..domain.homey_device import HomeyDevice
from ..infrastructure.gateways.homey_devices_gateway import HomeyDevicesGateway
from ..infrastructure.homekit.bridge_service import RunningBridge
from ..infrastructure.homekit.homey_accessory import HomeyAccessory
from ..infrastructure.homekit.service_profiles import (
    ServiceProfile,
    build_service_profiles,
)
from ..infrastructure.repositories.accessory_id_repository import AccessoryIdRepository
from ..infrastructure.repositories.exposed_devices_repository import (
    ExposedDevicesRepository,
)
from .log_function import LogFunction


class DeviceSyncService:
    def __init__(
        self,
        *,
        devices_gateway: HomeyDevicesGateway,
        exposed_devices_repository: ExposedDevicesRepository,
        accessory_id_repository: AccessoryIdRepository,
        log: LogFunction,
        sync_interval_seconds: float = DEVICE_SYNC_INTERVAL_SECONDS,
    ) -> None:
        self._devices_gateway = devices_gateway
        self._exposed_devices_repository = exposed_devices_repository
        self._accessory_id_repository = accessory_id_repository
        self._log = log
        self._sync_interval_seconds = sync_interval_seconds
        self._accessories_by_device_id: dict[str, HomeyAccessory] = {}
        self._running_bridge: RunningBridge | None = None
        self._is_bridge_published = False
        self._polling_task: asyncio.Task[None] | None = None
        self._background_tasks: set[asyncio.Task[None]] = set()
        self._sync_lock = asyncio.Lock()

    @property
    def exposed_accessory_count(self) -> int:
        return len(self._accessories_by_device_id)

    def attach_to_bridge(self, running_bridge: RunningBridge) -> None:
        self._running_bridge = running_bridge
        self._is_bridge_published = False

    async def populate_accessories_before_publish(self) -> None:
        try:
            await self.synchronize_once()
        except Exception as error:
            self._log(f"First device synchronization failed: {error}")

    def mark_bridge_published(self) -> None:
        self._is_bridge_published = True

    def start_polling(self) -> None:
        if self._polling_task is None:
            self._polling_task = asyncio.get_running_loop().create_task(
                self._polling_loop()
            )

    async def detach_from_bridge(self) -> None:
        await self._stop_polling()
        await self._cancel_pending_writes()
        self._accessories_by_device_id.clear()
        self._running_bridge = None
        self._is_bridge_published = False

    async def save_exposed_device_ids_and_synchronize(
        self, device_ids: Iterable[str]
    ) -> None:
        await self._exposed_devices_repository.save_exposed_device_ids(device_ids)
        if self._running_bridge is not None:
            await self.synchronize_once()

    async def synchronize_once(self) -> None:
        async with self._sync_lock:
            devices = await self._devices_gateway.fetch_all_devices()
            await self._synchronize_with_devices(devices)

    def refresh_device_soon(self, device_id: str) -> None:
        refresh_task = asyncio.get_running_loop().create_task(
            self._refresh_single_device(device_id)
        )
        self._background_tasks.add(refresh_task)
        refresh_task.add_done_callback(self._background_tasks.discard)

    async def _synchronize_with_devices(self, devices: dict[str, HomeyDevice]) -> None:
        exposed_ids = self._exposed_devices_repository.read_exposed_device_ids()
        removed_any = self._remove_accessories_that_should_not_exist(
            devices, exposed_ids
        )
        added_any = await self._add_missing_accessories(devices, exposed_ids)
        self._update_existing_accessories(devices)
        self._announce_configuration_change_if_published(removed_any or added_any)

    def _remove_accessories_that_should_not_exist(
        self, devices: dict[str, HomeyDevice], exposed_ids: frozenset[str]
    ) -> bool:
        obsolete_device_ids = [
            device_id
            for device_id in self._accessories_by_device_id
            if not self._should_have_accessory(device_id, devices, exposed_ids)
        ]
        for device_id in obsolete_device_ids:
            self._remove_accessory(device_id)
        return bool(obsolete_device_ids)

    @staticmethod
    def _should_have_accessory(
        device_id: str, devices: dict[str, HomeyDevice], exposed_ids: frozenset[str]
    ) -> bool:
        device = devices.get(device_id)
        if device is None or device_id not in exposed_ids:
            return False
        return bool(build_service_profiles(device))

    def _remove_accessory(self, device_id: str) -> None:
        accessory = self._accessories_by_device_id.pop(device_id)
        self._require_running_bridge().bridge.accessories.pop(accessory.aid, None)
        self._log(f"'{accessory.homey_device.name}' is no longer exposed")

    async def _add_missing_accessories(
        self, devices: dict[str, HomeyDevice], exposed_ids: frozenset[str]
    ) -> bool:
        added_any = False
        for device_id in sorted(exposed_ids):
            device = devices.get(device_id)
            if device is None or device_id in self._accessories_by_device_id:
                continue
            profiles = build_service_profiles(device)
            if not profiles:
                continue
            await self._add_accessory(device, profiles)
            added_any = True
        return added_any

    async def _add_accessory(
        self, device: HomeyDevice, profiles: tuple[ServiceProfile, ...]
    ) -> None:
        running_bridge = self._require_running_bridge()
        accessory_id = await self._accessory_id_repository.get_or_assign_accessory_id(
            device.id
        )
        accessory = HomeyAccessory(
            driver=running_bridge.driver,
            device=device,
            profiles=profiles,
            devices_gateway=self._devices_gateway,
            accessory_id=accessory_id,
            log=self._log,
            on_capability_written=self.refresh_device_soon,
        )
        running_bridge.bridge.add_accessory(accessory)
        self._accessories_by_device_id[device.id] = accessory
        self._log(f"'{device.name}' is now exposed")

    def _update_existing_accessories(self, devices: dict[str, HomeyDevice]) -> None:
        for device_id, accessory in self._accessories_by_device_id.items():
            accessory.update_from_device(devices[device_id])

    def _announce_configuration_change_if_published(self, changed: bool) -> None:
        if changed and self._is_bridge_published:
            self._require_running_bridge().driver.config_changed()

    async def _refresh_single_device(self, device_id: str) -> None:
        accessory = self._accessories_by_device_id.get(device_id)
        if accessory is None:
            return
        try:
            accessory.update_from_device(
                await self._devices_gateway.fetch_device(device_id)
            )
        except Exception as error:
            self._log(f"Refreshing device {device_id} failed: {error}")

    async def _polling_loop(self) -> None:
        while True:
            await asyncio.sleep(self._sync_interval_seconds)
            await self._synchronize_logging_errors()

    async def _synchronize_logging_errors(self) -> None:
        try:
            await self.synchronize_once()
        except Exception as error:
            self._log(f"Device synchronization failed: {error}")

    async def _stop_polling(self) -> None:
        if self._polling_task is None:
            return
        self._polling_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._polling_task
        self._polling_task = None

    async def _cancel_pending_writes(self) -> None:
        for accessory in self._accessories_by_device_id.values():
            await accessory.cancel_pending_writes()

    def _require_running_bridge(self) -> RunningBridge:
        if self._running_bridge is None:
            raise RuntimeError("Device synchronization is not attached to a bridge")
        return self._running_bridge
