import json
from typing import Any, Protocol


class SettingsStorage(Protocol):
    def get(self, key: str) -> Any: ...

    async def set(self, key: str, value: Any) -> None: ...

    async def unset(self, key: str) -> None: ...


class JsonSettingsAccess:
    def __init__(self, storage: SettingsStorage) -> None:
        self._storage = storage

    def read_json(self, key: str, default: Any) -> Any:
        stored_text = self._storage.get(key)
        if not isinstance(stored_text, str):
            return default
        return self._parse_json_or_default(stored_text, default)

    async def write_json(self, key: str, value: Any) -> None:
        serialized_value = json.dumps(value, sort_keys=True)
        await self._storage.set(key, serialized_value)

    @staticmethod
    def _parse_json_or_default(text: str, default: Any) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return default
