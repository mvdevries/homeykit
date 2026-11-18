from .setting_keys import LEGACY_SETTING_KEY_RENAMES
from .settings_access import SettingsAccess


class LegacySettingsMigration:
    def __init__(self, settings_access: SettingsAccess) -> None:
        self._settings_access = settings_access

    async def migrate_all_legacy_keys(self) -> None:
        for legacy_key, current_key in LEGACY_SETTING_KEY_RENAMES.items():
            await self._migrate_key(legacy_key, current_key)

    async def _migrate_key(self, legacy_key: str, current_key: str) -> None:
        legacy_value = self._settings_access.read_raw(legacy_key)
        if legacy_value is None:
            return
        if self._settings_access.read_raw(current_key) is None:
            await self._settings_access.write_raw(current_key, legacy_value)
        await self._settings_access.remove(legacy_key)
