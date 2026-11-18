import json
from typing import Any

from ...application.ports import SettingsStorage


class SettingsAccess:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    def read_raw(self, key: str) -> Any:
        return self._storage.get(key)

    def read_text(self, key: str) -> str | None:
        stored_value = self._storage.get(key)
        return stored_value if isinstance(stored_value, str) else None

    def read_int(self, key: str) -> int | None:
        stored_value = self._storage.get(key)
        if isinstance(stored_value, bool) or not isinstance(stored_value, (int, float)):
            return None
        return int(stored_value)

    def read_bool(self, key: str) -> bool:
        return bool(self._storage.get(key))

    def read_json(self, key: str, default: Any) -> Any:
        stored_text = self.read_text(key)
        if stored_text is None:
            return default
        return self._parse_json_or_default(stored_text, default)

    async def write_raw(self, key: str, value: Any) -> None:
        await self._storage.set(key, value)

    async def write_json(self, key: str, value: Any) -> None:
        await self._storage.set(key, json.dumps(value, sort_keys=True))

    async def remove(self, key: str) -> None:
        await self._storage.unset(key)

    @staticmethod
    def _parse_json_or_default(text: str, default: Any) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return default
