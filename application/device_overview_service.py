from ..domain.device_row import DeviceRow
from ..domain.homey_device import HomeyDevice
from ..infrastructure.gateways.homey_devices_gateway import HomeyDevicesGateway
from ..infrastructure.homekit.service_profiles import is_device_supported
from ..infrastructure.repositories.exposed_devices_repository import (
    ExposedDevicesRepository,
)


def build_sort_key(row: DeviceRow) -> tuple[bool, str, str]:
    has_no_zone = row.zone is None
    return has_no_zone, (row.zone or "").casefold(), row.name.casefold()


class DeviceOverviewService:
    def __init__(
        self,
        *,
        devices_gateway: HomeyDevicesGateway,
        exposed_devices_repository: ExposedDevicesRepository,
    ) -> None:
        self._devices_gateway = devices_gateway
        self._exposed_devices_repository = exposed_devices_repository

    async def build_device_rows(self) -> list[DeviceRow]:
        devices = await self._devices_gateway.fetch_all_devices()
        zone_names = await self._devices_gateway.fetch_zone_names()
        exposed_ids = self._exposed_devices_repository.read_exposed_device_ids()
        rows = [
            self._build_row(device, zone_names, exposed_ids)
            for device in devices.values()
        ]
        return sorted(rows, key=build_sort_key)

    @staticmethod
    def _build_row(
        device: HomeyDevice, zone_names: dict[str, str], exposed_ids: frozenset[str]
    ) -> DeviceRow:
        is_supported = is_device_supported(device)
        return DeviceRow(
            id=device.id,
            name=device.name,
            zone=zone_names.get(device.zone_id or ""),
            device_class=device.effective_class,
            icon_id=device.icon_id,
            is_supported=is_supported,
            is_exposed=is_supported and device.id in exposed_ids,
        )
