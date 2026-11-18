from ..domain.device_row import DeviceRow
from ..domain.homey_device import HomeyDevice
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from ..homekit.service_profiles import is_device_supported
from ..storage.exposed_devices_store import ExposedDevicesStore


def build_sort_key(row: DeviceRow) -> tuple[bool, str, str]:
    has_no_zone = row.zone is None
    return has_no_zone, (row.zone or "").casefold(), row.name.casefold()


class DeviceOverviewService:
    def __init__(
        self,
        *,
        devices_gateway: HomeyDevicesGateway,
        exposed_devices_store: ExposedDevicesStore,
    ) -> None:
        self._devices_gateway = devices_gateway
        self._exposed_devices_store = exposed_devices_store

    async def build_device_rows(self) -> list[DeviceRow]:
        devices = await self._devices_gateway.fetch_all_devices()
        zone_names = await self._devices_gateway.fetch_zone_names()
        exposed_ids = self._exposed_devices_store.read_exposed_device_ids()
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
