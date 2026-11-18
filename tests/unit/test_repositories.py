from typing import ClassVar

import pytest
from homeykit.infrastructure.repositories import setting_keys
from homeykit.infrastructure.repositories.accessory_id_repository import (
    AccessoryIdRepository,
)
from homeykit.infrastructure.repositories.bridge_name_repository import (
    BridgeNameRepository,
)
from homeykit.infrastructure.repositories.exposed_devices_repository import (
    ExposedDevicesRepository,
)
from homeykit.infrastructure.repositories.legacy_settings_migration import (
    LegacySettingsMigration,
)
from homeykit.infrastructure.repositories.pincode_repository import PincodeRepository
from homeykit.infrastructure.repositories.settings_storage import JsonSettingsAccess
from homeykit.infrastructure.repositories.startup_delay_repository import (
    StartupDelayRepository,
)


class TestJsonSettingsAccess:
    async def test_round_trips_json(self, settings):
        access = JsonSettingsAccess(settings)
        await access.write_json("key", {"b": 1, "a": [1, 2]})
        assert access.read_json("key", None) == {"a": [1, 2], "b": 1}

    def test_returns_default_when_missing(self, settings):
        assert (
            JsonSettingsAccess(settings).read_json("missing", "fallback") == "fallback"
        )

    @pytest.mark.parametrize("stored", ["{not json", 12, None])
    def test_returns_default_for_unusable_values(self, settings, stored):
        settings.values["key"] = stored
        assert JsonSettingsAccess(settings).read_json("key", []) == []


class TestExposedDevicesRepository:
    async def test_saves_sorted_unique_ids(self, settings):
        repository = ExposedDevicesRepository(JsonSettingsAccess(settings))
        await repository.save_exposed_device_ids(["b", "a", "b"])
        assert repository.read_exposed_device_ids() == frozenset({"a", "b"})
        assert (
            settings.values[setting_keys.EXPOSED_DEVICE_IDS_SETTING_KEY] == '["a", "b"]'
        )

    def test_is_empty_by_default(self, settings):
        repository = ExposedDevicesRepository(JsonSettingsAccess(settings))
        assert repository.read_exposed_device_ids() == frozenset()


class TestAccessoryIdRepository:
    async def test_assigns_stable_ids_skipping_reserved(self, settings):
        repository = AccessoryIdRepository(JsonSettingsAccess(settings))
        assigned = [
            await repository.get_or_assign_accessory_id(f"device-{index}")
            for index in range(7)
        ]
        assert assigned == [2, 3, 4, 5, 6, 8, 9]

    async def test_returns_same_id_for_same_device(self, settings):
        repository = AccessoryIdRepository(JsonSettingsAccess(settings))
        first = await repository.get_or_assign_accessory_id("device")
        assert await repository.get_or_assign_accessory_id("device") == first

    async def test_survives_a_new_repository_instance(self, settings):
        await AccessoryIdRepository(
            JsonSettingsAccess(settings)
        ).get_or_assign_accessory_id("a")
        repository = AccessoryIdRepository(JsonSettingsAccess(settings))
        assert await repository.get_or_assign_accessory_id("a") == 2
        assert await repository.get_or_assign_accessory_id("b") == 3


class TestBridgeNameRepository:
    async def test_saves_and_clears_name(self, settings):
        repository = BridgeNameRepository(settings)
        await repository.save_custom_name("Mine")
        assert repository.read_custom_name() == "Mine"
        await repository.clear_custom_name()
        assert repository.read_custom_name() is None

    @pytest.mark.parametrize("stored", ["", "   ", 5])
    def test_ignores_blank_or_wrong_type(self, settings, stored):
        settings.values[setting_keys.BRIDGE_NAME_SETTING_KEY] = stored
        assert BridgeNameRepository(settings).read_custom_name() is None


class TestPincodeRepository:
    async def test_round_trip(self, settings):
        repository = PincodeRepository(settings)
        assert repository.read_pincode() is None
        await repository.save_pincode("204-81-357")
        assert repository.read_pincode() == "204-81-357"

    def test_ignores_wrong_type(self, settings):
        settings.values[setting_keys.PINCODE_SETTING_KEY] = 20481357
        assert PincodeRepository(settings).read_pincode() is None


class TestStartupDelayRepository:
    async def test_round_trip(self, settings):
        repository = StartupDelayRepository(settings)
        await repository.save(True, 30)
        assert repository.read_enabled() is True
        assert repository.read_seconds() == 30

    def test_defaults(self, settings):
        repository = StartupDelayRepository(settings)
        assert repository.read_enabled() is False
        assert repository.read_seconds() is None

    @pytest.mark.parametrize("stored", [True, "30", None])
    def test_rejects_non_numeric_seconds(self, settings, stored):
        settings.values[setting_keys.STARTUP_DELAY_SECONDS_SETTING_KEY] = stored
        assert StartupDelayRepository(settings).read_seconds() is None


class TestLegacySettingsMigration:
    LEGACY: ClassVar[dict] = {
        "aangeboden": '["a", "b"]',
        "aids": '{"a": 2}',
        "bridge_naam": "Home",
        "start_vertraging_aan": True,
        "start_vertraging_seconden": 30,
    }

    async def test_moves_all_legacy_keys(self, settings):
        settings.values.update(self.LEGACY)
        settings.values["bridge_pincode"] = "204-81-357"
        await LegacySettingsMigration(settings).migrate_all_legacy_keys()
        assert settings.values == {
            "exposed_device_ids": '["a", "b"]',
            "accessory_ids": '{"a": 2}',
            "bridge_name": "Home",
            "startup_delay_enabled": True,
            "startup_delay_seconds": 30,
            "bridge_pincode": "204-81-357",
        }

    async def test_never_overwrites_a_current_value(self, settings):
        settings.values.update(
            {"aangeboden": '["old"]', "exposed_device_ids": '["new"]'}
        )
        await LegacySettingsMigration(settings).migrate_all_legacy_keys()
        assert settings.values == {"exposed_device_ids": '["new"]'}

    async def test_second_run_changes_nothing(self, settings):
        settings.values.update(self.LEGACY)
        migration = LegacySettingsMigration(settings)
        await migration.migrate_all_legacy_keys()
        after_first_run = dict(settings.values)
        await migration.migrate_all_legacy_keys()
        assert settings.values == after_first_run
