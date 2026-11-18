import pytest
from homeykit.infrastructure.homekit import value_conversions as conversions


@pytest.mark.parametrize(
    ("fraction", "percentage"), [(0, 0), (0.5, 50), (1, 100), (None, 0), (0.004, 0)]
)
def test_fraction_to_percentage(fraction, percentage):
    assert conversions.fraction_to_percentage(fraction) == percentage


@pytest.mark.parametrize(("percentage", "fraction"), [(0, 0.0), (50, 0.5), (100, 1.0)])
def test_percentage_to_fraction(percentage, fraction):
    assert conversions.percentage_to_fraction(percentage) == fraction


@pytest.mark.parametrize(
    ("fraction", "mireds"), [(0, 140), (1, 500), (0.5, 320), (None, 140)]
)
def test_fraction_to_mireds(fraction, mireds):
    assert conversions.fraction_to_mireds(fraction) == mireds


@pytest.mark.parametrize(
    ("mireds", "fraction"), [(140, 0.0), (500, 1.0), (320, 0.5), (50, 0.0), (900, 1.0)]
)
def test_mireds_to_fraction_is_clamped(mireds, fraction):
    assert conversions.mireds_to_fraction(mireds) == fraction


def test_boolean_conversions():
    assert conversions.to_bool(1) is True
    assert conversions.to_bool(0) is False
    assert conversions.to_zero_or_one(True) == 1
    assert conversions.to_zero_or_one(None) == 0


def test_to_float_treats_missing_value_as_zero():
    assert conversions.to_float(None) == 0.0
    assert conversions.to_float("21.5") == 21.5


def test_keep_value_returns_the_same_object():
    marker = object()
    assert conversions.keep_value(marker) is marker
