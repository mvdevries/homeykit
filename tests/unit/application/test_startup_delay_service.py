import pytest
from homeykit.application.startup_delay_service import StartupDelayService
from homeykit.domain.errors import SettingsValidationError
from homeykit.infrastructure.repositories.settings_access import SettingsAccess
from homeykit.infrastructure.repositories.startup_delay_repository import (
    StartupDelayRepository,
)


@pytest.fixture
def service(settings):
    return StartupDelayService(StartupDelayRepository(SettingsAccess(settings)))


class TestStartupDelayService:
    def test_given_nothing_saved_when_read_then_the_delay_is_disabled(self, service):
        delay = service.read_startup_delay()

        assert delay.enabled is False
        assert delay.effective_seconds == 0

    async def test_given_a_valid_delay_when_saved_then_it_is_read_back(self, service):
        await service.save_startup_delay(True, 45)

        delay = service.read_startup_delay()

        assert (delay.enabled, delay.seconds) == (True, 45)

    async def test_given_zero_seconds_when_saved_then_it_is_rejected(self, service):
        with pytest.raises(SettingsValidationError):
            await service.save_startup_delay(True, 0)
