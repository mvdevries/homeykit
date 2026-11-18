import json

import httpx
import pytest
from homeykit.infrastructure.gateways.homey_devices_gateway import (
    HomeyDevicesGateway,
    extract_payload_items,
)
from homeykit.infrastructure.gateways.homey_web_api import HomeyWebApiClient

from tests.support.fake_homey_api import OWNER_TOKEN
from tests.support.sample_devices import ICON_SVG


@pytest.fixture
def client(fake_homey_api, token_source):
    return HomeyWebApiClient(token_source, transport=fake_homey_api.build_transport())


@pytest.fixture
def gateway(client):
    return HomeyDevicesGateway(client)


def test_extract_payload_items_accepts_mapping_and_list():
    assert extract_payload_items({"a": {"id": 1}}) == [{"id": 1}]
    assert extract_payload_items([{"id": 1}]) == [{"id": 1}]
    assert extract_payload_items(None) == []


class TestGateway:
    async def test_fetches_all_devices(self, gateway):
        devices = await gateway.fetch_all_devices()
        assert len(devices) == 10
        assert devices["wall-socket"].name == "Wall socket"

    async def test_fetches_one_device(self, gateway):
        assert (await gateway.fetch_device("plain-lamp")).name == "Plain lamp"

    async def test_fetches_zone_names(self, gateway):
        zones = await gateway.fetch_zone_names()
        assert zones["zone-kitchen"] == "Kitchen"

    async def test_fetches_icon_without_api_prefix(self, gateway, fake_homey_api):
        assert await gateway.fetch_icon_svg("/api/icon/light") == ICON_SVG
        assert fake_homey_api.requests[-1][1] == "/api/icon/light"

    async def test_fetches_homey_name(self, gateway):
        assert await gateway.fetch_homey_name() == "Test Homey"

    @pytest.mark.parametrize("name", [None, "", "   "])
    async def test_unusable_homey_name_is_none(self, gateway, fake_homey_api, name):
        fake_homey_api.homey_name = name
        assert await gateway.fetch_homey_name() is None

    async def test_writes_capability_value(self, gateway, fake_homey_api):
        await gateway.set_capability_value("plain-lamp", "onoff", True)
        assert fake_homey_api.capability_writes == [("plain-lamp", "onoff", True)]


class TestClient:
    async def test_sends_bearer_token(self, client, fake_homey_api):
        assert await client.get_json("/manager/system/name") == "Test Homey"
        assert fake_homey_api.requests[0][1] == "/api/manager/system/name"

    async def test_reconnects_once_after_401(self, fake_homey_api, token_source):
        stale_transport = httpx.MockTransport(lambda request: httpx.Response(401))
        client = HomeyWebApiClient(token_source, transport=stale_transport)
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/manager/system/name")
        assert token_source.token_requests == 2

    async def test_raises_on_server_error(self, client, fake_homey_api):
        fake_homey_api.fail_next_requests_with.append(500)
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/manager/system/name")

    async def test_empty_response_body_is_none(self, token_source):
        transport = httpx.MockTransport(lambda request: httpx.Response(204))
        client = HomeyWebApiClient(token_source, transport=transport)
        assert await client.put_json("/anything", {"value": 1}) is None

    async def test_close_is_idempotent(self, client):
        await client.get_json("/manager/system/name")
        await client.close()
        await client.close()

    async def test_uses_token_from_source(self, token_source, fake_homey_api):
        seen = []

        def handler(request):
            seen.append(request.headers["Authorization"])
            return httpx.Response(200, content=json.dumps("ok"))

        client = HomeyWebApiClient(token_source, transport=httpx.MockTransport(handler))
        await client.get_json("/x")
        assert seen == [f"Bearer {OWNER_TOKEN}"]
