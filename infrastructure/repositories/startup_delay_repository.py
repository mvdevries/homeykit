from .setting_keys import (
    STARTUP_DELAY_ENABLED_SETTING_KEY,
    STARTUP_DELAY_SECONDS_SETTING_KEY,
)
from .settings_access import SettingsAccess


class StartupDelayRepository:
    def __init__(self, settings_access: SettingsAccess) -> None:
        self._settings_access = settings_access

    def read_enabled(self) -> bool:
        return self._settings_access.read_bool(STARTUP_DELAY_ENABLED_SETTING_KEY)

    def read_seconds(self) -> int | None:
        return self._settings_access.read_int(STARTUP_DELAY_SECONDS_SETTING_KEY)

    async def save(self, enabled: bool, seconds: int) -> None:
        await self._settings_access.write_raw(
            STARTUP_DELAY_ENABLED_SETTING_KEY, bool(enabled)
        )
        await self._settings_access.write_raw(
            STARTUP_DELAY_SECONDS_SETTING_KEY, int(seconds)
        )
