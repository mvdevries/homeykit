from homeykit.infrastructure.repositories.exposed_devices_repository import (
    ExposedDevicesRepository,
)
from homeykit.infrastructure.repositories.setting_keys import (
    EXPOSED_DEVICE_IDS_SETTING_KEY,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


class TestExposedDevicesRepository:
    async def test_given_duplicate_ids_when_saved_then_sorted_unique_ids_are_stored(
        self, settings
    ):
        repository = ExposedDevicesRepository(SettingsAccess(settings))

        await repository.save_exposed_device_ids(["b", "a", "b"])

        assert repository.read_exposed_device_ids() == frozenset({"a", "b"})
        assert settings.values[EXPOSED_DEVICE_IDS_SETTING_KEY] == '["a", "b"]'

    def test_given_nothing_saved_when_read_then_no_device_is_exposed(self, settings):
        repository = ExposedDevicesRepository(SettingsAccess(settings))

        exposed = repository.read_exposed_device_ids()

        assert exposed == frozenset()
