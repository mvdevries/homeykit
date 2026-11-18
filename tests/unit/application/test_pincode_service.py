import pytest
from homeykit.application.pincode_service import PincodeService
from homeykit.domain.errors import SettingsValidationError
from homeykit.infrastructure.repositories.pincode_repository import PincodeRepository
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


@pytest.fixture
def service(settings):
    return PincodeService(PincodeRepository(SettingsAccess(settings)))


class TestGetOrCreatePincode:
    async def test_given_no_pincode_when_asked_twice_then_the_same_one_is_kept(
        self, service
    ):
        first = await service.get_or_create_pincode()

        second = await service.get_or_create_pincode()

        assert second == first

    async def test_given_an_invalid_stored_pincode_when_asked_then_it_is_replaced(
        self, settings, service
    ):
        settings.values["bridge_pincode"] = "11111111"

        pincode = await service.get_or_create_pincode()

        assert pincode != "11111111"


class TestSetCustomOrRandomPincode:
    async def test_given_a_custom_code_when_set_then_it_is_formatted_and_stored(
        self, settings, service
    ):
        pincode = await service.set_custom_or_random_pincode("20481357")

        assert pincode == "204-81-357"
        assert settings.values["bridge_pincode"] == "204-81-357"

    async def test_given_an_invalid_code_when_set_then_it_is_rejected(self, service):
        with pytest.raises(SettingsValidationError):
            await service.set_custom_or_random_pincode("1")

    @pytest.mark.parametrize("text", [None, "", "  "], ids=["none", "empty", "blank"])
    async def test_given_no_code_when_set_then_a_different_random_one_is_chosen(
        self, service, text
    ):
        current = await service.get_or_create_pincode()

        new_pincode = await service.set_custom_or_random_pincode(text)

        assert new_pincode != current
