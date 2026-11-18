import pytest
from homeykit.domain import errors
from homeykit.domain.bridge_name import collapse_whitespace, normalize_bridge_name
from homeykit.domain.defaults import BRIDGE_NAME_MAX_LENGTH
from homeykit.domain.errors import SettingsValidationError


class TestCollapseWhitespace:
    def test_given_extra_spaces_when_collapsed_then_single_spaces_remain(self):
        text = "  My   bridge "

        collapsed = collapse_whitespace(text)

        assert collapsed == "My bridge"


class TestNormalizeBridgeName:
    @pytest.mark.parametrize("text", [None, "", "   "], ids=["none", "empty", "blank"])
    def test_given_no_name_when_normalised_then_the_default_name_is_meant(self, text):
        normalised = normalize_bridge_name(text)

        assert normalised is None

    def test_given_a_messy_name_when_normalised_then_it_is_cleaned(self):
        name = "  Living   room "

        normalised = normalize_bridge_name(name)

        assert normalised == "Living room"

    def test_given_a_name_that_is_too_long_when_normalised_then_it_is_rejected(self):
        name = "x" * (BRIDGE_NAME_MAX_LENGTH + 1)

        with pytest.raises(SettingsValidationError) as error:
            normalize_bridge_name(name)

        assert error.value.error_code == errors.BRIDGE_NAME_TOO_LONG

    def test_given_a_name_of_the_maximum_length_when_normalised_then_it_is_kept(self):
        name = "x" * BRIDGE_NAME_MAX_LENGTH

        normalised = normalize_bridge_name(name)

        assert normalised == name
