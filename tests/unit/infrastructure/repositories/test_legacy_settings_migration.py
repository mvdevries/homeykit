from typing import ClassVar

from homeykit.infrastructure.repositories.legacy_settings_migration import (
    LegacySettingsMigration,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess

LEGACY_SETTINGS: dict[str, object] = {
    "aangeboden": '["a", "b"]',
    "aids": '{"a": 2}',
    "bridge_naam": "Home",
    "start_vertraging_aan": True,
    "start_vertraging_seconden": 30,
}


class TestLegacySettingsMigration:
    NO_SETTINGS: ClassVar[dict] = {}

    async def test_given_legacy_keys_when_migrated_then_they_move_to_the_current_keys(
        self, settings
    ):
        settings.values.update(LEGACY_SETTINGS)
        settings.values["bridge_pincode"] = "204-81-357"
        migration = LegacySettingsMigration(SettingsAccess(settings))

        await migration.migrate_all_legacy_keys()

        assert settings.values == {
            "exposed_device_ids": '["a", "b"]',
            "accessory_ids": '{"a": 2}',
            "bridge_name": "Home",
            "startup_delay_enabled": True,
            "startup_delay_seconds": 30,
            "bridge_pincode": "204-81-357",
        }

    async def test_given_a_current_value_when_migrated_then_it_is_never_overwritten(
        self, settings
    ):
        settings.values.update(
            {"aangeboden": '["old"]', "exposed_device_ids": '["new"]'}
        )
        migration = LegacySettingsMigration(SettingsAccess(settings))

        await migration.migrate_all_legacy_keys()

        assert settings.values == {"exposed_device_ids": '["new"]'}

    async def test_given_a_finished_migration_when_run_again_then_nothing_changes(
        self, settings
    ):
        settings.values.update(LEGACY_SETTINGS)
        migration = LegacySettingsMigration(SettingsAccess(settings))
        await migration.migrate_all_legacy_keys()
        after_first_run = dict(settings.values)

        await migration.migrate_all_legacy_keys()

        assert settings.values == after_first_run
