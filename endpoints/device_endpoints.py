from typing import Any

from homey.homey import Homey

from ..domain.device_row import DeviceRow
from .endpoint_types import EmptyBody, JsonBody, EndpointParams, EndpointQuery
from .service_lookup import get_service_container


def build_devices_payload(rows: list[DeviceRow]) -> dict[str, Any]:
    return {"devices": [row.to_payload() for row in rows]}


def read_exposed_device_ids(body: JsonBody) -> list[str]:
    return [str(device_id) for device_id in body.get("exposed_device_ids", [])]


async def get_devices(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: EmptyBody
) -> Any:
    overview_service = get_service_container(homey).device_overview_service
    return build_devices_payload(await overview_service.build_device_rows())


async def set_exposed_devices(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: JsonBody
) -> Any:
    services = get_service_container(homey)
    await services.device_sync_service.save_exposed_device_ids_and_synchronize(
        read_exposed_device_ids(body)
    )
    return build_devices_payload(await services.device_overview_service.build_device_rows())


async def get_icons(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: EmptyBody
) -> Any:
    icon_service = get_service_container(homey).icon_service
    result = await icon_service.load_icons_for_current_devices()
    return result.to_payload()
