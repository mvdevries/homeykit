from ..config.setting_keys import BRIDGE_NAME_SETTING_KEY
from .settings_storage import SettingsStorage


class BridgeNameRepository:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    def read_custom_name(self) -> str | None:
        stored_value = self._storage.get(BRIDGE_NAME_SETTING_KEY)
        if isinstance(stored_value, str) and stored_value.strip():
            return stored_value.strip()
        return None

    async def save_custom_name(self, name: str) -> None:
        await self._storage.set(BRIDGE_NAME_SETTING_KEY, name)

    async def clear_custom_name(self) -> None:
        await self._storage.unset(BRIDGE_NAME_SETTING_KEY)
