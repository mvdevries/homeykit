from ..config.setting_keys import ACCESSORY_IDS_SETTING_KEY
from .settings_storage import JsonSettingsAccess

FIRST_ASSIGNABLE_ACCESSORY_ID = 2
RESERVED_ACCESSORY_IDS = frozenset({1, 7})


class AccessoryIdRegistry:
    def __init__(self, settings_access: JsonSettingsAccess) -> None:
        self._settings_access = settings_access

    async def get_or_assign_accessory_id(self, device_id: str) -> int:
        accessory_ids = self._read_accessory_ids()
        if device_id in accessory_ids:
            return accessory_ids[device_id]
        new_accessory_id = self._find_next_free_accessory_id(accessory_ids)
        accessory_ids[device_id] = new_accessory_id
        await self._settings_access.write_json(ACCESSORY_IDS_SETTING_KEY, accessory_ids)
        return new_accessory_id

    def _read_accessory_ids(self) -> dict[str, int]:
        return self._settings_access.read_json(ACCESSORY_IDS_SETTING_KEY, {})

    @staticmethod
    def _find_next_free_accessory_id(accessory_ids: dict[str, int]) -> int:
        used_ids = set(accessory_ids.values()) | RESERVED_ACCESSORY_IDS
        candidate_id = FIRST_ASSIGNABLE_ACCESSORY_ID
        while candidate_id in used_ids:
            candidate_id += 1
        return candidate_id
