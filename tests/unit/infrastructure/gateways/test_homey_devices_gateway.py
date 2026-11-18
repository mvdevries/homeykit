import pytest
from homeykit.domain.errors import HomeyRateLimitedError, HomeyRequestFailedError
from homeykit.infrastructure.gateways.homey_devices_gateway import extract_payload_items

from tests.support.sample_devices import ICON_SVG


class TestExtractPayloadItems:
    def test_given_a_mapping_a_list_or_nothing_when_extracted_then_a_list_is_returned(
        self,
    ):
        from_mapping = extract_payload_items({"a": {"id": 1}})
        from_list = extract_payload_items([{"id": 1}])
        from_nothing = extract_payload_items(None)

        assert (from_mapping, from_list, from_nothing) == ([{"id": 1}], [{"id": 1}], [])


class TestHomeyDevicesGateway:
    async def test_given_ten_devices_when_fetching_all_then_ten_are_parsed(
        self, gateway
    ):
        devices = await gateway.fetch_all_devices()

        assert len(devices) == 10
        assert devices["wall-socket"].name == "Wall socket"

    async def test_given_a_device_id_when_fetching_one_then_that_device_is_returned(
        self, gateway
    ):
        device = await gateway.fetch_device("plain-lamp")

        assert device.name == "Plain lamp"

    async def test_given_zones_when_fetching_names_then_names_are_keyed_by_id(
        self, gateway
    ):
        zones = await gateway.fetch_zone_names()

        assert zones["zone-kitchen"] == "Kitchen"

    async def test_given_an_icon_path_when_fetching_then_the_api_prefix_is_removed(
        self, gateway, fake_homey_api
    ):
        svg = await gateway.fetch_icon_svg("/api/icon/light")

        assert svg == ICON_SVG
        assert fake_homey_api.requests[-1][1] == "/api/icon/light"

    async def test_given_a_rate_limit_when_fetching_an_icon_then_it_is_reported(
        self, gateway, fake_homey_api
    ):
        fake_homey_api.fail_next_requests_with.append(429)

        with pytest.raises(HomeyRateLimitedError):
            await gateway.fetch_icon_svg("/api/icon/light")

    async def test_given_a_server_error_when_fetching_an_icon_then_the_request_failed(
        self, gateway, fake_homey_api
    ):
        fake_homey_api.fail_next_requests_with.append(500)

        with pytest.raises(HomeyRequestFailedError):
            await gateway.fetch_icon_svg("/api/icon/light")

    async def test_given_a_name_when_fetching_the_homey_name_then_it_is_returned(
        self, gateway
    ):
        name = await gateway.fetch_homey_name()

        assert name == "Test Homey"

    @pytest.mark.parametrize("name", [None, "", "   "], ids=["none", "empty", "blank"])
    async def test_given_an_unusable_name_when_fetching_then_none_is_returned(
        self, gateway, fake_homey_api, name
    ):
        fake_homey_api.homey_name = name

        fetched = await gateway.fetch_homey_name()

        assert fetched is None

    async def test_given_a_value_when_setting_a_capability_then_homey_receives_it(
        self, gateway, fake_homey_api
    ):
        await gateway.set_capability_value("plain-lamp", "onoff", True)

        assert fake_homey_api.capability_writes == [("plain-lamp", "onoff", True)]
