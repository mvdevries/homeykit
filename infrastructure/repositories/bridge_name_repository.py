from .setting_keys import BRIDGE_NAME_SETTING_KEY
from .settings_access import SettingsAccess


class BridgeNameRepository:
    def __init__(self, settings_access: SettingsAccess) -> None:
        self._settings_access = settings_access

    def read_custom_name(self) -> str | None:
        stored_name = self._settings_access.read_text(BRIDGE_NAME_SETTING_KEY)
        if stored_name is None or not stored_name.strip():
            return None
        return stored_name.strip()

    async def save_custom_name(self, name: str) -> None:
        await self._settings_access.write_raw(BRIDGE_NAME_SETTING_KEY, name)

    async def clear_custom_name(self) -> None:
        await self._settings_access.remove(BRIDGE_NAME_SETTING_KEY)
