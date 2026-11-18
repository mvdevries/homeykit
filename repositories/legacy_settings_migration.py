from ..config.setting_keys import LEGACY_SETTING_KEY_RENAMES
from .settings_storage import SettingsStorage


class LegacySettingsMigration:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    async def migrate_all_legacy_keys(self) -> None:
        for legacy_key, current_key in LEGACY_SETTING_KEY_RENAMES.items():
            await self._migrate_key(legacy_key, current_key)

    async def _migrate_key(self, legacy_key: str, current_key: str) -> None:
        legacy_value = self._storage.get(legacy_key)
        if legacy_value is None:
            return
        if self._storage.get(current_key) is None:
            await self._storage.set(current_key, legacy_value)
        await self._storage.unset(legacy_key)
