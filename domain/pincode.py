import secrets
import string

from .errors import PINCODE_INVALID_FORMAT, PINCODE_TOO_SIMPLE, SettingsValidationError

PINCODE_DIGIT_COUNT = 8
ALLOWED_INPUT_CHARACTERS = frozenset(string.digits + "- ")
SAME_DIGIT_PINCODES = frozenset(digit * PINCODE_DIGIT_COUNT for digit in string.digits)
SEQUENTIAL_PINCODES = frozenset({"12345678", "87654321"})
REJECTED_PINCODES = SAME_DIGIT_PINCODES | SEQUENTIAL_PINCODES


def format_pincode(digits: str) -> str:
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


def contains_only_allowed_characters(text: str) -> bool:
    return all(character in ALLOWED_INPUT_CHARACTERS for character in text)


def extract_digits(text: str) -> str:
    return "".join(character for character in text if character in string.digits)


def normalize_pincode_input(text: str) -> str:
    if not contains_only_allowed_characters(text):
        raise SettingsValidationError(PINCODE_INVALID_FORMAT)
    digits = extract_digits(text)
    if len(digits) != PINCODE_DIGIT_COUNT:
        raise SettingsValidationError(PINCODE_INVALID_FORMAT)
    if digits in REJECTED_PINCODES:
        raise SettingsValidationError(PINCODE_TOO_SIMPLE)
    return format_pincode(digits)


def generate_random_digits() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(PINCODE_DIGIT_COUNT))


def generate_random_pincode() -> str:
    while True:
        digits = generate_random_digits()
        if digits not in REJECTED_PINCODES:
            return format_pincode(digits)
