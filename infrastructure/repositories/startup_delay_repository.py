from .setting_keys import (
    STARTUP_DELAY_ENABLED_SETTING_KEY,
    STARTUP_DELAY_SECONDS_SETTING_KEY,
)
from .settings_storage import SettingsStorage


class StartupDelayRepository:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    def read_enabled(self) -> bool:
        return bool(self._storage.get(STARTUP_DELAY_ENABLED_SETTING_KEY))

    def read_seconds(self) -> int | None:
        stored_value = self._storage.get(STARTUP_DELAY_SECONDS_SETTING_KEY)
        if isinstance(stored_value, bool) or not isinstance(stored_value, (int, float)):
            return None
        return int(stored_value)

    async def save(self, enabled: bool, seconds: int) -> None:
        await self._storage.set(STARTUP_DELAY_ENABLED_SETTING_KEY, bool(enabled))
        await self._storage.set(STARTUP_DELAY_SECONDS_SETTING_KEY, int(seconds))
