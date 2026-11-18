import httpx
import pytest
from homeykit.config.bridge_defaults import BRIDGE_DEFAULT_NAME
from homeykit.domain.device_row import DeviceRow
from homeykit.domain.errors import SettingsValidationError
from homeykit.gateways.homey_devices_gateway import HomeyDevicesGateway
from homeykit.gateways.homey_web_api import HomeyWebApiClient
from homeykit.repositories.bridge_name_repository import BridgeNameRepository
from homeykit.repositories.exposed_devices_repository import ExposedDevicesRepository
from homeykit.repositories.pincode_repository import PincodeRepository
from homeykit.repositories.settings_storage import JsonSettingsAccess
from homeykit.repositories.startup_delay_repository import StartupDelayRepository
from homeykit.services.bridge_name_service import BridgeNameService
from homeykit.services.device_overview_service import (
    DeviceOverviewService,
    build_sort_key,
)
from homeykit.services.icon_service import IconService, convert_svg_to_data_uri
from homeykit.services.pincode_service import PincodeService
from homeykit.services.startup_delay_service import StartupDelayService

from tests.support.sample_devices import SUPPORTED_DEVICE_IDS


@pytest.fixture
def gateway(fake_homey_api, token_source):
    client = HomeyWebApiClient(token_source, transport=fake_homey_api.build_transport())
    return HomeyDevicesGateway(client)


class TestPincodeService:
    async def test_creates_and_keeps_a_pincode(self, settings):
        service = PincodeService(PincodeRepository(settings))
        first = await service.get_or_create_pincode()
        assert await service.get_or_create_pincode() == first

    async def test_replaces_an_invalid_stored_pincode(self, settings):
        settings.values["bridge_pincode"] = "11111111"
        service = PincodeService(PincodeRepository(settings))
        assert await service.get_or_create_pincode() != "11111111"

    async def test_sets_custom_pincode(self, settings):
        service = PincodeService(PincodeRepository(settings))
        assert await service.set_custom_or_random_pincode("20481357") == "204-81-357"
        assert settings.values["bridge_pincode"] == "204-81-357"

    async def test_rejects_invalid_custom_pincode(self, settings):
        service = PincodeService(PincodeRepository(settings))
        with pytest.raises(SettingsValidationError):
            await service.set_custom_or_random_pincode("1")

    @pytest.mark.parametrize("text", [None, "", "  "])
    async def test_new_random_pincode_differs_from_current(self, settings, text):
        service = PincodeService(PincodeRepository(settings))
        current = await service.get_or_create_pincode()
        assert await service.set_custom_or_random_pincode(text) != current


class TestBridgeNameService:
    @pytest.fixture
    def service(self, settings, gateway, log):
        return BridgeNameService(
            bridge_name_repository=BridgeNameRepository(settings),
            devices_gateway=gateway,
            log=log,
        )

    async def test_defaults_to_fallback_name(self, service):
        assert service.resolve_bridge_name() == BRIDGE_DEFAULT_NAME

    async def test_uses_homey_name_as_default(self, service):
        await service.load_default_name_from_homey()
        assert service.resolve_bridge_name() == "Test Homey"

    async def test_custom_name_wins_and_can_be_cleared(self, service):
        await service.load_default_name_from_homey()
        await service.set_custom_bridge_name("  My   bridge ")
        assert service.resolve_bridge_name() == "My bridge"
        await service.set_custom_bridge_name("")
        assert service.resolve_bridge_name() == "Test Homey"

    async def test_failure_to_read_homey_name_is_logged(
        self, service, fake_homey_api, log
    ):
        fake_homey_api.fail_next_requests_with.append(500)
        await service.load_default_name_from_homey()
        assert service.resolve_bridge_name() == BRIDGE_DEFAULT_NAME
        assert log.contains("Reading the name of Homey failed")


class TestStartupDelayService:
    @pytest.fixture
    def service(self, settings):
        return StartupDelayService(StartupDelayRepository(settings))

    def test_default_is_disabled(self, service):
        delay = service.read_startup_delay()
        assert delay.enabled is False
        assert delay.effective_seconds == 0

    async def test_saves_delay(self, service):
        await service.save_startup_delay(True, 45)
        delay = service.read_startup_delay()
        assert (delay.enabled, delay.seconds) == (True, 45)

    async def test_rejects_invalid_delay(self, service):
        with pytest.raises(SettingsValidationError):
            await service.save_startup_delay(True, 0)


class TestDeviceOverviewService:
    @pytest.fixture
    def service(self, settings, gateway):
        return DeviceOverviewService(
            devices_gateway=gateway,
            exposed_devices_repository=ExposedDevicesRepository(
                JsonSettingsAccess(settings)
            ),
        )

    async def test_lists_all_ten_devices_sorted_by_zone_then_name(self, service):
        rows = await service.build_device_rows()
        assert len(rows) == 10
        zones = [row.zone for row in rows]
        assert zones == sorted(zones)

    async def test_marks_support(self, service):
        rows = await service.build_device_rows()
        supported = {row.id for row in rows if row.is_supported}
        assert supported == SUPPORTED_DEVICE_IDS

    async def test_unsupported_device_is_never_marked_exposed(self, settings, service):
        settings.values["exposed_device_ids"] = '["radiator-thermostat", "wall-socket"]'
        rows = {row.id: row for row in await service.build_device_rows()}
        assert rows["wall-socket"].is_exposed is True
        assert rows["radiator-thermostat"].is_exposed is False

    def test_devices_without_zone_sort_last(self):
        with_zone = DeviceRow("1", "B", "Zone", "light", None, True, False)
        without_zone = DeviceRow("2", "A", None, "light", None, True, False)
        assert build_sort_key(with_zone) < build_sort_key(without_zone)


class TestIconService:
    @pytest.fixture(autouse=True)
    def no_pause(self, monkeypatch):
        monkeypatch.setattr(
            "homeykit.services.icon_service.ICON_DOWNLOAD_PAUSE_SECONDS", 0
        )

    def test_converts_svg_to_data_uri(self):
        uri = convert_svg_to_data_uri("<svg></svg>")
        assert uri is not None
        assert uri.startswith("data:image/svg+xml;base64,")

    @pytest.mark.parametrize("text", ["not an image", "<svg>" + "x" * 300_000])
    def test_rejects_non_svg_and_huge_svg(self, text):
        assert convert_svg_to_data_uri(text) is None

    async def test_loads_one_icon_per_icon_id(self, gateway, fake_homey_api):
        result = await IconService(
            devices_gateway=gateway
        ).load_icons_for_current_devices()
        assert result.missing_count == 0
        assert set(result.icons_by_id) == {
            "icon-light",
            "icon-socket",
            "icon-other",
            "icon-sensor",
            "icon-thermostat",
        }
        icon_requests = [r for r in fake_homey_api.requests if "/icon/" in r[1]]
        assert len(icon_requests) == 5

    async def test_caches_downloaded_icons(self, gateway, fake_homey_api):
        service = IconService(devices_gateway=gateway)
        await service.load_icons_for_current_devices()
        before = len(fake_homey_api.requests)
        await service.load_icons_for_current_devices()
        new_icon_requests = [
            r for r in fake_homey_api.requests[before:] if "/icon/" in r[1]
        ]
        assert new_icon_requests == []

    async def test_stops_on_rate_limit_and_reports_missing(
        self, gateway, fake_homey_api
    ):
        service = IconService(devices_gateway=gateway)
        devices = await gateway.fetch_all_devices()
        fake_homey_api.fail_next_requests_with.append(429)
        result = await service.load_icons_for_devices(devices.values())
        assert result.missing_count == 5
        assert result.to_payload() == {"icons": {}, "missing_count": 5}

    async def test_continues_after_other_http_error(self, gateway, fake_homey_api):
        service = IconService(devices_gateway=gateway)
        devices = await gateway.fetch_all_devices()
        fake_homey_api.fail_next_requests_with.append(500)
        result = await service.load_icons_for_devices(devices.values())
        assert result.missing_count == 1

    async def test_network_errors_do_not_fail_loading(self, token_source):
        def refuse(request):
            raise httpx.ConnectError("offline")

        client = HomeyWebApiClient(token_source, transport=httpx.MockTransport(refuse))
        service = IconService(devices_gateway=HomeyDevicesGateway(client))
        result = await service.load_icons_for_devices([])
        assert result.icons_by_id == {}
