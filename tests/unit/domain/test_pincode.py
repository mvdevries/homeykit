import pytest
from homeykit.domain import errors
from homeykit.domain.errors import SettingsValidationError
from homeykit.domain.pincode import (
    format_pincode,
    generate_random_pincode,
    normalize_pincode_input,
)


class TestFormatPincode:
    def test_given_eight_digits_when_formatted_then_it_has_the_homekit_pattern(self):
        digits = "20481357"

        formatted = format_pincode(digits)

        assert formatted == "204-81-357"


class TestNormalizePincodeInput:
    @pytest.mark.parametrize(
        "text",
        ["204-81-357", "20481357", " 204 81 357 "],
        ids=["with dashes", "plain digits", "with spaces"],
    )
    def test_given_a_common_notation_when_normalised_then_it_is_formatted(self, text):
        normalised = normalize_pincode_input(text)

        assert normalised == "204-81-357"

    @pytest.mark.parametrize(
        "text",
        ["abc", "1234567", "123456789", "204-81-35x", ""],
        ids=["letters", "too short", "too long", "one letter", "empty"],
    )
    def test_given_the_wrong_format_when_normalised_then_it_is_rejected(self, text):
        with pytest.raises(SettingsValidationError) as error:
            normalize_pincode_input(text)

        assert error.value.error_code == errors.PINCODE_INVALID_FORMAT

    @pytest.mark.parametrize(
        "text",
        ["11111111", "00000000", "12345678", "87654321"],
        ids=["repeated one", "repeated zero", "ascending", "descending"],
    )
    def test_given_a_simple_code_when_normalised_then_it_is_rejected_as_too_simple(
        self, text
    ):
        with pytest.raises(SettingsValidationError) as error:
            normalize_pincode_input(text)

        assert error.value.error_code == errors.PINCODE_TOO_SIMPLE


class TestGenerateRandomPincode:
    def test_given_many_draws_when_generated_then_every_pincode_is_valid(self):
        draws = [generate_random_pincode() for _ in range(200)]

        assert all(normalize_pincode_input(pincode) == pincode for pincode in draws)
