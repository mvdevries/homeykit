from collections.abc import Mapping
from typing import Any

from ...domain.homey_device import HomeyDevice
from .homey_device_parser import parse_homey_device
from .homey_web_api import HomeyWebApiClient

DEVICES_PATH = "/manager/devices/device"
ZONES_PATH = "/manager/zones/zone"
SYSTEM_NAME_PATH = "/manager/system/name"
API_PATH_PREFIX = "/api"


def extract_payload_items(payload: Any) -> list[Mapping[str, Any]]:
    values = payload.values() if isinstance(payload, Mapping) else payload
    return list(values or [])


class HomeyDevicesGateway:
    def __init__(self, web_api_client: HomeyWebApiClient) -> None:
        self._web_api_client = web_api_client

    async def fetch_all_devices(self) -> dict[str, HomeyDevice]:
        payload = await self._web_api_client.get_json(DEVICES_PATH)
        devices = (parse_homey_device(item) for item in extract_payload_items(payload))
        return {device.id: device for device in devices}

    async def fetch_device(self, device_id: str) -> HomeyDevice:
        payload = await self._web_api_client.get_json(f"{DEVICES_PATH}/{device_id}")
        return parse_homey_device(payload)

    async def fetch_zone_names(self) -> dict[str, str]:
        payload = await self._web_api_client.get_json(ZONES_PATH)
        zones = extract_payload_items(payload)
        return {zone["id"]: zone.get("name") or zone["id"] for zone in zones}

    async def fetch_icon_svg(self, icon_path: str) -> str:
        relative_path = icon_path.removeprefix(API_PATH_PREFIX)
        return await self._web_api_client.get_text(relative_path)

    async def fetch_homey_name(self) -> str | None:
        name = await self._web_api_client.get_json(SYSTEM_NAME_PATH)
        if isinstance(name, str) and name.strip():
            return name.strip()
        return None

    async def set_capability_value(
        self, device_id: str, capability_id: str, value: Any
    ) -> None:
        path = f"{DEVICES_PATH}/{device_id}/capability/{capability_id}"
        await self._web_api_client.put_json(path, {"value": value})
