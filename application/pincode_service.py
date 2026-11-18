from ..domain.errors import SettingsValidationError
from ..domain.pincode import generate_random_pincode, normalize_pincode_input
from ..infrastructure.repositories.pincode_repository import PincodeRepository


class PincodeService:
    def __init__(self, pincode_repository: PincodeRepository) -> None:
        self._pincode_repository = pincode_repository

    async def get_or_create_pincode(self) -> str:
        existing_pincode = self.read_valid_stored_pincode()
        if existing_pincode is not None:
            return existing_pincode
        return await self._create_and_save_random_pincode()

    async def set_custom_or_random_pincode(self, text: str | None) -> str:
        if text is None or not text.strip():
            new_pincode = self._generate_pincode_different_from_current()
        else:
            new_pincode = normalize_pincode_input(text)
        await self._pincode_repository.save_pincode(new_pincode)
        return new_pincode

    def read_valid_stored_pincode(self) -> str | None:
        stored_pincode = self._pincode_repository.read_pincode()
        if stored_pincode is None:
            return None
        return self._normalize_or_none(stored_pincode)

    def _generate_pincode_different_from_current(self) -> str:
        current_pincode = self.read_valid_stored_pincode()
        new_pincode = generate_random_pincode()
        while new_pincode == current_pincode:
            new_pincode = generate_random_pincode()
        return new_pincode

    async def _create_and_save_random_pincode(self) -> str:
        new_pincode = generate_random_pincode()
        await self._pincode_repository.save_pincode(new_pincode)
        return new_pincode

    @staticmethod
    def _normalize_or_none(pincode: str) -> str | None:
        try:
            return normalize_pincode_input(pincode)
        except SettingsValidationError:
            return None
