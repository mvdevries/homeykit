import json
from typing import Any

import httpx

from tests.support.sample_devices import (
    ICON_SVG,
    ZONES,
    build_sample_device_payloads,
)

DEVICES_PATH = "/api/manager/devices/device"
ZONES_PATH = "/api/manager/zones/zone"
NAME_PATH = "/api/manager/system/name"
CAPABILITY_SEGMENT = "/capability/"
HOMEY_NAME = "Test Homey"
LOCAL_URL = "http://homey.test"
OWNER_TOKEN = "test-token"


class FakeTokenSource:
    def __init__(self) -> None:
        self.token_requests = 0

    async def get_local_url(self) -> str:
        return LOCAL_URL

    async def get_owner_api_token(self) -> str:
        self.token_requests += 1
        return OWNER_TOKEN


class FakeHomeyApi:
    def __init__(self) -> None:
        self.devices = build_sample_device_payloads()
        self.homey_name: str | None = HOMEY_NAME
        self.capability_writes: list[tuple[str, str, Any]] = []
        self.fail_next_requests_with: list[int] = []
        self.requests: list[tuple[str, str]] = []

    def build_transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle_request)

    def set_capability_value(
        self, device_id: str, capability_id: str, value: Any
    ) -> None:
        self.devices[device_id]["capabilitiesObj"][capability_id]["value"] = value

    def remove_device(self, device_id: str) -> None:
        del self.devices[device_id]

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append((request.method, request.url.path))
        if self.fail_next_requests_with:
            return httpx.Response(self.fail_next_requests_with.pop(0))
        if request.headers.get("Authorization") != f"Bearer {OWNER_TOKEN}":
            return httpx.Response(401)
        return self._route(request)

    def _route(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == DEVICES_PATH:
            return httpx.Response(200, json=self.devices)
        if path == ZONES_PATH:
            return httpx.Response(200, json={zone["id"]: zone for zone in ZONES})
        if path == NAME_PATH:
            return httpx.Response(200, json=self.homey_name)
        if path.startswith("/api/icon/"):
            return httpx.Response(200, text=ICON_SVG)
        if path.startswith(DEVICES_PATH + "/"):
            return self._route_device(request, path.removeprefix(DEVICES_PATH + "/"))
        return httpx.Response(404)

    def _route_device(self, request: httpx.Request, relative: str) -> httpx.Response:
        if CAPABILITY_SEGMENT in relative:
            return self._write_capability(request, relative)
        device = self.devices.get(relative)
        if device is None:
            return httpx.Response(404)
        return httpx.Response(200, json=device)

    def _write_capability(
        self, request: httpx.Request, relative: str
    ) -> httpx.Response:
        device_id, capability_id = relative.split(CAPABILITY_SEGMENT)
        value = json.loads(request.content)["value"]
        self.set_capability_value(device_id, capability_id, value)
        self.capability_writes.append((device_id, capability_id, value))
        return httpx.Response(200, json=True)
