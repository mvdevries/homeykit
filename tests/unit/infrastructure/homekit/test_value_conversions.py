import pytest
from homeykit.infrastructure.homekit import value_conversions as conversions


class TestFractionToPercentage:
    @pytest.mark.parametrize(
        ("fraction", "percentage"),
        [(0, 0), (0.5, 50), (1, 100), (None, 0), (0.004, 0)],
        ids=["zero", "half", "full", "missing", "rounds down"],
    )
    def test_given_a_homey_fraction_when_converted_then_it_is_a_percentage(
        self, fraction, percentage
    ):
        converted = conversions.fraction_to_percentage(fraction)

        assert converted == percentage


class TestPercentageToFraction:
    @pytest.mark.parametrize(
        ("percentage", "fraction"),
        [(0, 0.0), (50, 0.5), (100, 1.0)],
        ids=["zero", "half", "full"],
    )
    def test_given_a_homekit_percentage_when_converted_then_it_is_a_fraction(
        self, percentage, fraction
    ):
        converted = conversions.percentage_to_fraction(percentage)

        assert converted == fraction


class TestFractionToMireds:
    @pytest.mark.parametrize(
        ("fraction", "mireds"),
        [(0, 140), (1, 500), (0.5, 320), (None, 140)],
        ids=["coldest", "warmest", "middle", "missing"],
    )
    def test_given_a_homey_fraction_when_converted_then_it_is_in_the_mired_range(
        self, fraction, mireds
    ):
        converted = conversions.fraction_to_mireds(fraction)

        assert converted == mireds


class TestMiredsToFraction:
    @pytest.mark.parametrize(
        ("mireds", "fraction"),
        [(140, 0.0), (500, 1.0), (320, 0.5), (50, 0.0), (900, 1.0)],
        ids=["lowest", "highest", "middle", "below the range", "above the range"],
    )
    def test_given_a_mired_value_when_converted_then_it_is_clamped_to_zero_and_one(
        self, mireds, fraction
    ):
        converted = conversions.mireds_to_fraction(mireds)

        assert converted == fraction


class TestSimpleConversions:
    def test_given_numbers_when_converted_to_booleans_then_zero_is_false(self):
        results = (conversions.to_bool(1), conversions.to_bool(0))

        assert results == (True, False)

    def test_given_values_when_converted_to_zero_or_one_then_they_are_integers(self):
        results = (conversions.to_zero_or_one(True), conversions.to_zero_or_one(None))

        assert results == (1, 0)

    def test_given_a_missing_value_when_converted_to_a_float_then_it_is_zero(self):
        results = (conversions.to_float(None), conversions.to_float("21.5"))

        assert results == (0.0, 21.5)

    def test_given_any_object_when_kept_then_the_same_object_is_returned(self):
        marker = object()

        kept = conversions.keep_value(marker)

        assert kept is marker
