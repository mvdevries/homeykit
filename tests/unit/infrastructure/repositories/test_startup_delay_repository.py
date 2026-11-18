import pytest
from homeykit.infrastructure.repositories.setting_keys import (
    STARTUP_DELAY_SECONDS_SETTING_KEY,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess
from homeykit.infrastructure.repositories.startup_delay_repository import (
    StartupDelayRepository,
)


class TestStartupDelayRepository:
    async def test_given_a_saved_delay_when_read_then_enabled_and_seconds_are_returned(
        self, settings
    ):
        repository = StartupDelayRepository(SettingsAccess(settings))

        await repository.save(True, 30)

        assert repository.read_enabled() is True
        assert repository.read_seconds() == 30

    def test_given_nothing_saved_when_read_then_the_delay_is_disabled_without_seconds(
        self, settings
    ):
        repository = StartupDelayRepository(SettingsAccess(settings))

        assert repository.read_enabled() is False
        assert repository.read_seconds() is None

    @pytest.mark.parametrize(
        "stored", [True, "30", None], ids=["boolean", "text", "nothing"]
    )
    def test_given_seconds_that_are_no_number_when_read_then_nothing_is_returned(
        self, settings, stored
    ):
        settings.values[STARTUP_DELAY_SECONDS_SETTING_KEY] = stored
        repository = StartupDelayRepository(SettingsAccess(settings))

        seconds = repository.read_seconds()

        assert seconds is None
