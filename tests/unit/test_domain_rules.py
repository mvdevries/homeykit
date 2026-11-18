import pytest
from homeykit.config.bridge_defaults import (
    BRIDGE_NAME_MAX_LENGTH,
    STARTUP_DELAY_MAX_SECONDS,
)
from homeykit.domain import errors
from homeykit.domain.bridge_name import collapse_whitespace, normalize_bridge_name
from homeykit.domain.device_row import DeviceRow
from homeykit.domain.errors import SettingsValidationError
from homeykit.domain.pincode import (
    format_pincode,
    generate_random_pincode,
    normalize_pincode_input,
)
from homeykit.domain.startup_delay import StartupDelay, validate_startup_delay_seconds


class TestPincode:
    def test_formats_digits_in_homekit_pattern(self):
        assert format_pincode("20481357") == "204-81-357"

    @pytest.mark.parametrize("text", ["204-81-357", "20481357", " 204 81 357 "])
    def test_accepts_common_notations(self, text):
        assert normalize_pincode_input(text) == "204-81-357"

    @pytest.mark.parametrize("text", ["abc", "1234567", "123456789", "204-81-35x", ""])
    def test_rejects_wrong_format(self, text):
        with pytest.raises(SettingsValidationError) as error:
            normalize_pincode_input(text)
        assert error.value.error_code == errors.PINCODE_INVALID_FORMAT

    @pytest.mark.parametrize("text", ["11111111", "00000000", "12345678", "87654321"])
    def test_rejects_simple_codes(self, text):
        with pytest.raises(SettingsValidationError) as error:
            normalize_pincode_input(text)
        assert error.value.error_code == errors.PINCODE_TOO_SIMPLE

    def test_random_pincodes_are_always_valid(self):
        for _ in range(200):
            pincode = generate_random_pincode()
            assert normalize_pincode_input(pincode) == pincode


class TestBridgeName:
    def test_collapses_whitespace(self):
        assert collapse_whitespace("  My   bridge ") == "My bridge"

    @pytest.mark.parametrize("text", [None, "", "   "])
    def test_empty_name_means_default(self, text):
        assert normalize_bridge_name(text) is None

    def test_returns_cleaned_name(self):
        assert normalize_bridge_name("  Living   room ") == "Living room"

    def test_rejects_too_long_name(self):
        with pytest.raises(SettingsValidationError) as error:
            normalize_bridge_name("x" * (BRIDGE_NAME_MAX_LENGTH + 1))
        assert error.value.error_code == errors.BRIDGE_NAME_TOO_LONG

    def test_accepts_name_of_maximum_length(self):
        name = "x" * BRIDGE_NAME_MAX_LENGTH
        assert normalize_bridge_name(name) == name


class TestStartupDelay:
    @pytest.mark.parametrize("seconds", [0, -1, STARTUP_DELAY_MAX_SECONDS + 1])
    def test_rejects_out_of_range(self, seconds):
        with pytest.raises(SettingsValidationError) as error:
            validate_startup_delay_seconds(seconds)
        assert error.value.error_code == errors.STARTUP_DELAY_OUT_OF_RANGE

    @pytest.mark.parametrize("seconds", [1, 10, STARTUP_DELAY_MAX_SECONDS])
    def test_accepts_range(self, seconds):
        assert validate_startup_delay_seconds(seconds) == seconds

    def test_disabled_delay_has_no_effective_seconds(self):
        assert StartupDelay(enabled=False, seconds=30).effective_seconds == 0

    def test_enabled_delay_uses_seconds(self):
        assert StartupDelay(enabled=True, seconds=30).effective_seconds == 30


def test_device_row_payload_uses_public_field_names():
    row = DeviceRow("id-1", "Lamp", "Kitchen", "light", "icon-1", True, False)
    assert row.to_payload() == {
        "id": "id-1",
        "name": "Lamp",
        "zone": "Kitchen",
        "device_class": "light",
        "icon_id": "icon-1",
        "supported": True,
        "exposed": False,
    }
