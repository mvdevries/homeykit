from ..domain.errors import SettingsValidationError
from ..domain.pincode import generate_random_pincode, normalize_pincode_input
from ..storage.pincode_store import PincodeStore


class PincodeService:
    def __init__(self, pincode_store: PincodeStore) -> None:
        self._pincode_store = pincode_store

    async def get_or_create_pincode(self) -> str:
        existing_pincode = self.read_valid_stored_pincode()
        if existing_pincode is not None:
            return existing_pincode
        return await self._create_and_save_random_pincode()

    def read_valid_stored_pincode(self) -> str | None:
        stored_pincode = self._pincode_store.read_pincode()
        if stored_pincode is None:
            return None
        return self._normalize_or_none(stored_pincode)

    async def _create_and_save_random_pincode(self) -> str:
        new_pincode = generate_random_pincode()
        await self._pincode_store.save_pincode(new_pincode)
        return new_pincode

    @staticmethod
    def _normalize_or_none(pincode: str) -> str | None:
        try:
            return normalize_pincode_input(pincode)
        except SettingsValidationError:
            return None
