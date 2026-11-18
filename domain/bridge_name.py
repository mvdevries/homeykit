from .defaults import BRIDGE_NAME_MAX_LENGTH
from .errors import BRIDGE_NAME_TOO_LONG, SettingsValidationError


def collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def normalize_bridge_name(text: str | None) -> str | None:
    cleaned_name = collapse_whitespace(text or "")
    if not cleaned_name:
        return None
    if len(cleaned_name) > BRIDGE_NAME_MAX_LENGTH:
        raise SettingsValidationError(BRIDGE_NAME_TOO_LONG)
    return cleaned_name
