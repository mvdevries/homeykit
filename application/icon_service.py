import asyncio
import base64
from dataclasses import dataclass

import httpx

from ..domain.defaults import (
    ICON_DOWNLOAD_PAUSE_SECONDS,
    ICON_MAX_SVG_CHARACTERS,
)
from ..infrastructure.gateways.homey_devices_gateway import HomeyDevicesGateway

HTTP_TOO_MANY_REQUESTS = 429


@dataclass(frozen=True, slots=True)
class IconLoadResult:
    icons_by_id: dict[str, str]
    missing_count: int

    def to_payload(self) -> dict[str, object]:
        return {"icons": self.icons_by_id, "missing_count": self.missing_count}


def convert_svg_to_data_uri(svg: str) -> str | None:
    if "<svg" not in svg or len(svg) > ICON_MAX_SVG_CHARACTERS:
        return None
    encoded_svg = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded_svg}"


class IconService:
    def __init__(self, *, devices_gateway: HomeyDevicesGateway) -> None:
        self._devices_gateway = devices_gateway
        self._data_uris_by_icon_id: dict[str, str] = {}
        self._download_lock = asyncio.Lock()

    async def load_icons_for_current_devices(self) -> IconLoadResult:
        devices = await self._devices_gateway.fetch_all_devices()
        return await self.load_icons_for_devices(devices.values())

    async def load_icons_for_devices(self, devices) -> IconLoadResult:
        requested_icons = self._collect_requested_icons(devices)
        async with self._download_lock:
            await self._download_uncached_icons(requested_icons)
        return self._build_result(requested_icons)

    @staticmethod
    def _collect_requested_icons(devices) -> dict[str, str]:
        return {
            device.icon_id: device.icon_path
            for device in devices
            if device.icon_id and device.icon_path
        }

    async def _download_uncached_icons(self, requested_icons: dict[str, str]) -> None:
        for icon_id, icon_path in requested_icons.items():
            if icon_id in self._data_uris_by_icon_id:
                continue
            should_continue = await self._download_icon(icon_id, icon_path)
            if not should_continue:
                return
            await asyncio.sleep(ICON_DOWNLOAD_PAUSE_SECONDS)

    async def _download_icon(self, icon_id: str, icon_path: str) -> bool:
        try:
            svg = await self._devices_gateway.fetch_icon_svg(icon_path)
        except httpx.HTTPStatusError as error:
            return error.response.status_code != HTTP_TOO_MANY_REQUESTS
        except httpx.HTTPError:
            return True
        self._cache_icon(icon_id, svg)
        return True

    def _cache_icon(self, icon_id: str, svg: str) -> None:
        data_uri = convert_svg_to_data_uri(svg)
        if data_uri is not None:
            self._data_uris_by_icon_id[icon_id] = data_uri

    def _build_result(self, requested_icons: dict[str, str]) -> IconLoadResult:
        available_icons = {
            icon_id: self._data_uris_by_icon_id[icon_id]
            for icon_id in requested_icons
            if icon_id in self._data_uris_by_icon_id
        }
        return IconLoadResult(
            icons_by_id=available_icons,
            missing_count=len(requested_icons) - len(available_icons),
        )
