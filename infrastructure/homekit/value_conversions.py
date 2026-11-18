from collections.abc import Callable
from typing import Any

type Converter = Callable[[Any], Any]

MIRED_MIN = 140
MIRED_MAX = 500


def keep_value(value: Any) -> Any:
    return value


def to_bool(value: Any) -> bool:
    return bool(value)


def to_zero_or_one(value: Any) -> int:
    return int(bool(value))


def to_float(value: Any) -> float:
    return float(value or 0)


def fraction_to_percentage(fraction: Any) -> int:
    return round(float(fraction or 0) * 100)


def percentage_to_fraction(percentage: Any) -> float:
    return float(percentage) / 100


def fraction_to_mireds(fraction: Any) -> int:
    mired_range = MIRED_MAX - MIRED_MIN
    return round(MIRED_MIN + float(fraction or 0) * mired_range)


def mireds_to_fraction(mireds: Any) -> float:
    fraction = (float(mireds) - MIRED_MIN) / (MIRED_MAX - MIRED_MIN)
    return min(1.0, max(0.0, fraction))
