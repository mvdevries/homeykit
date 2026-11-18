import pytest
from homeykit.domain import errors
from homeykit.domain.defaults import STARTUP_DELAY_MAX_SECONDS
from homeykit.domain.errors import SettingsValidationError
from homeykit.domain.startup_delay import StartupDelay, validate_startup_delay_seconds


class TestValidateStartupDelaySeconds:
    @pytest.mark.parametrize(
        "seconds",
        [0, -1, STARTUP_DELAY_MAX_SECONDS + 1],
        ids=["zero", "negative", "above the maximum"],
    )
    def test_given_seconds_out_of_range_when_validated_then_it_is_rejected(
        self, seconds
    ):
        with pytest.raises(SettingsValidationError) as error:
            validate_startup_delay_seconds(seconds)

        assert error.value.error_code == errors.STARTUP_DELAY_OUT_OF_RANGE

    @pytest.mark.parametrize(
        "seconds",
        [1, 10, STARTUP_DELAY_MAX_SECONDS],
        ids=["minimum", "default", "maximum"],
    )
    def test_given_seconds_in_range_when_validated_then_they_are_returned(
        self, seconds
    ):
        validated = validate_startup_delay_seconds(seconds)

        assert validated == seconds


class TestStartupDelay:
    def test_given_a_disabled_delay_when_asked_for_seconds_then_it_is_zero(self):
        delay = StartupDelay(enabled=False, seconds=30)

        effective_seconds = delay.effective_seconds

        assert effective_seconds == 0

    def test_given_an_enabled_delay_when_asked_for_seconds_then_it_is_the_chosen_value(
        self,
    ):
        delay = StartupDelay(enabled=True, seconds=30)

        effective_seconds = delay.effective_seconds

        assert effective_seconds == 30
