from .setting_keys import PINCODE_SETTING_KEY
from .settings_access import SettingsAccess


class PincodeRepository:
    def __init__(self, settings_access: SettingsAccess) -> None:
        self._settings_access = settings_access

    def read_pincode(self) -> str | None:
        return self._settings_access.read_text(PINCODE_SETTING_KEY)

    async def save_pincode(self, pincode: str) -> None:
        await self._settings_access.write_raw(PINCODE_SETTING_KEY, pincode)
