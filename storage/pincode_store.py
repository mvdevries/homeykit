from ..config.setting_keys import PINCODE_SETTING_KEY
from .settings_storage import SettingsStorage


class PincodeStore:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    def read_pincode(self) -> str | None:
        stored_value = self._storage.get(PINCODE_SETTING_KEY)
        if isinstance(stored_value, str):
            return stored_value
        return None

    async def save_pincode(self, pincode: str) -> None:
        await self._storage.set(PINCODE_SETTING_KEY, pincode)
