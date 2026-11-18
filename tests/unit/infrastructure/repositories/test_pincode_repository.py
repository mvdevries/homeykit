from homeykit.infrastructure.repositories.pincode_repository import PincodeRepository
from homeykit.infrastructure.repositories.setting_keys import PINCODE_SETTING_KEY
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


class TestPincodeRepository:
    async def test_given_a_saved_pincode_when_read_then_it_is_returned(self, settings):
        repository = PincodeRepository(SettingsAccess(settings))
        before = repository.read_pincode()

        await repository.save_pincode("204-81-357")

        assert before is None
        assert repository.read_pincode() == "204-81-357"

    def test_given_a_stored_number_when_read_then_there_is_no_pincode(self, settings):
        settings.values[PINCODE_SETTING_KEY] = 20481357
        repository = PincodeRepository(SettingsAccess(settings))

        pincode = repository.read_pincode()

        assert pincode is None
