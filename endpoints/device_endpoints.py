from typing import Any

from ..container import ServiceContainer
from ..domain.device_row import DeviceRow
from .endpoint import endpoint
from .endpoint_types import JsonBody


def build_devices_payload(rows: list[DeviceRow]) -> dict[str, Any]:
    return {"devices": [row.to_payload() for row in rows]}


def read_exposed_device_ids(body: JsonBody) -> list[str]:
    return [str(device_id) for device_id in body.get("exposed_device_ids", [])]


@endpoint
async def get_devices(services: ServiceContainer, body: JsonBody) -> Any:
    return build_devices_payload(
        await services.device_overview_service.build_device_rows()
    )


@endpoint
async def set_exposed_devices(services: ServiceContainer, body: JsonBody) -> Any:
    await services.device_sync_service.save_exposed_device_ids_and_synchronize(
        read_exposed_device_ids(body)
    )
    return build_devices_payload(
        await services.device_overview_service.build_device_rows()
    )


@endpoint
async def get_icons(services: ServiceContainer, body: JsonBody) -> Any:
    result = await services.icon_service.load_icons_for_current_devices()
    return result.to_payload()
