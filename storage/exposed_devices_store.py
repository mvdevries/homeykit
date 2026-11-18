from collections.abc import Iterable

from ..config.setting_keys import EXPOSED_DEVICE_IDS_SETTING_KEY
from .settings_storage import JsonSettingsAccess


class ExposedDevicesStore:
    def __init__(self, settings_access: JsonSettingsAccess) -> None:
        self._settings_access = settings_access

    def read_exposed_device_ids(self) -> frozenset[str]:
        stored_ids = self._settings_access.read_json(EXPOSED_DEVICE_IDS_SETTING_KEY, [])
        return frozenset(stored_ids)

    async def save_exposed_device_ids(self, device_ids: Iterable[str]) -> None:
        sorted_unique_ids = sorted(set(device_ids))
        await self._settings_access.write_json(
            EXPOSED_DEVICE_IDS_SETTING_KEY, sorted_unique_ids
        )
