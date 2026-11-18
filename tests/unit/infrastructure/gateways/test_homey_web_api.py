import json

import httpx
import pytest
from homeykit.infrastructure.gateways.homey_web_api import HomeyWebApiClient

from tests.support.fake_homey_api import OWNER_TOKEN


class TestHomeyWebApiClient:
    async def test_given_a_token_when_requesting_then_the_bearer_header_is_sent(
        self, client, fake_homey_api
    ):
        name = await client.get_json("/manager/system/name")

        assert name == "Test Homey"
        assert fake_homey_api.requests[0][1] == "/api/manager/system/name"

    async def test_given_a_token_source_when_requesting_then_its_token_is_used(
        self, token_source
    ):
        seen = []

        def handler(request):
            seen.append(request.headers["Authorization"])
            return httpx.Response(200, content=json.dumps("ok"))

        client = HomeyWebApiClient(token_source, transport=httpx.MockTransport(handler))

        await client.get_json("/x")

        assert seen == [f"Bearer {OWNER_TOKEN}"]

    async def test_given_an_unauthorised_answer_when_requesting_then_it_reconnects_once(
        self, token_source
    ):
        stale_transport = httpx.MockTransport(lambda request: httpx.Response(401))
        client = HomeyWebApiClient(token_source, transport=stale_transport)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/manager/system/name")

        assert token_source.token_requests == 2

    async def test_given_a_server_error_when_requesting_then_the_error_is_raised(
        self, client, fake_homey_api
    ):
        fake_homey_api.fail_next_requests_with.append(500)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/manager/system/name")

    async def test_given_an_empty_answer_when_putting_then_none_is_returned(
        self, token_source
    ):
        transport = httpx.MockTransport(lambda request: httpx.Response(204))
        client = HomeyWebApiClient(token_source, transport=transport)

        result = await client.put_json("/anything", {"value": 1})

        assert result is None

    async def test_given_a_connection_when_closed_twice_then_nothing_breaks(
        self, client
    ):
        await client.get_json("/manager/system/name")

        await client.close()
        await client.close()
