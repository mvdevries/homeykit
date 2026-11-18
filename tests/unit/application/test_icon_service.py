import pytest
from homeykit.application.icon_service import IconService, convert_svg_to_data_uri


@pytest.fixture(autouse=True)
def no_pause_between_downloads(monkeypatch):
    monkeypatch.setattr(
        "homeykit.application.icon_service.ICON_DOWNLOAD_PAUSE_SECONDS", 0
    )


class TestConvertSvgToDataUri:
    def test_given_an_svg_when_converted_then_a_base64_data_uri_is_returned(self):
        uri = convert_svg_to_data_uri("<svg></svg>")

        assert uri is not None
        assert uri.startswith("data:image/svg+xml;base64,")

    @pytest.mark.parametrize(
        "text",
        ["not an image", "<svg>" + "x" * 300_000],
        ids=["no svg", "too large"],
    )
    def test_given_no_svg_or_a_huge_one_when_converted_then_nothing_is_returned(
        self, text
    ):
        uri = convert_svg_to_data_uri(text)

        assert uri is None


class TestLoadIconsForCurrentDevices:
    async def test_given_ten_devices_when_loaded_then_one_icon_per_icon_id_is_fetched(
        self, gateway, fake_homey_api
    ):
        service = IconService(devices_gateway=gateway)

        result = await service.load_icons_for_current_devices()

        icon_requests = [r for r in fake_homey_api.requests if "/icon/" in r[1]]
        assert result.missing_count == 0
        assert set(result.icons_by_id) == {
            "icon-light",
            "icon-socket",
            "icon-other",
            "icon-sensor",
            "icon-thermostat",
        }
        assert len(icon_requests) == 5

    async def test_given_loaded_icons_when_loaded_again_then_they_are_not_fetched_again(
        self, gateway, fake_homey_api
    ):
        service = IconService(devices_gateway=gateway)
        await service.load_icons_for_current_devices()
        requests_before = len(fake_homey_api.requests)

        await service.load_icons_for_current_devices()

        new_icon_requests = [
            r for r in fake_homey_api.requests[requests_before:] if "/icon/" in r[1]
        ]
        assert new_icon_requests == []

    async def test_given_a_rate_limit_when_loading_then_it_stops_and_reports_missing(
        self, gateway, fake_homey_api
    ):
        service = IconService(devices_gateway=gateway)
        devices = await gateway.fetch_all_devices()
        fake_homey_api.fail_next_requests_with.append(429)

        result = await service.load_icons_for_devices(devices.values())

        assert result.missing_count == 5
        assert result.to_payload() == {"icons": {}, "missing_count": 5}

    async def test_given_another_http_error_when_loading_then_it_carries_on(
        self, gateway, fake_homey_api
    ):
        service = IconService(devices_gateway=gateway)
        devices = await gateway.fetch_all_devices()
        fake_homey_api.fail_next_requests_with.append(500)

        result = await service.load_icons_for_devices(devices.values())

        assert result.missing_count == 1

    async def test_given_no_devices_when_loading_then_nothing_is_fetched(self, gateway):
        service = IconService(devices_gateway=gateway)

        result = await service.load_icons_for_devices([])

        assert result.icons_by_id == {}
