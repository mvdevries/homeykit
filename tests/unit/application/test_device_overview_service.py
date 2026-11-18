import pytest
from homeykit.application.device_overview_service import (
    DeviceOverviewService,
    build_sort_key,
)
from homeykit.domain.device_row import DeviceRow
from homeykit.infrastructure.homekit.device_support import HomeKitDeviceSupport
from homeykit.infrastructure.repositories.exposed_devices_repository import (
    ExposedDevicesRepository,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess

from tests.support.sample_devices import SUPPORTED_DEVICE_IDS


@pytest.fixture
def service(settings, gateway):
    return DeviceOverviewService(
        devices_gateway=gateway,
        exposed_devices_repository=ExposedDevicesRepository(SettingsAccess(settings)),
        device_support=HomeKitDeviceSupport(),
    )


class TestBuildDeviceRows:
    async def test_given_ten_devices_when_rows_are_built_then_they_are_sorted_by_zone(
        self, service
    ):
        rows = await service.build_device_rows()

        zones = [row.zone for row in rows]
        assert len(rows) == 10
        assert zones == sorted(zones)

    async def test_given_the_sample_devices_when_rows_are_built_then_support_is_marked(
        self, service
    ):
        rows = await service.build_device_rows()

        supported = {row.id for row in rows if row.is_supported}
        assert supported == SUPPORTED_DEVICE_IDS

    async def test_given_an_unsupported_chosen_device_when_built_then_it_is_not_exposed(
        self, settings, service
    ):
        settings.values["exposed_device_ids"] = '["radiator-thermostat", "wall-socket"]'

        rows = {row.id: row for row in await service.build_device_rows()}

        assert rows["wall-socket"].is_exposed is True
        assert rows["radiator-thermostat"].is_exposed is False


class TestBuildSortKey:
    def test_given_a_row_without_a_zone_when_sorted_then_it_comes_last(self):
        with_zone = DeviceRow("1", "B", "Zone", "light", None, True, False)
        without_zone = DeviceRow("2", "A", None, "light", None, True, False)

        keys = (build_sort_key(with_zone), build_sort_key(without_zone))

        assert keys[0] < keys[1]
