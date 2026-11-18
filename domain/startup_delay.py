from dataclasses import dataclass

from .defaults import STARTUP_DELAY_MAX_SECONDS
from .errors import STARTUP_DELAY_OUT_OF_RANGE, SettingsValidationError


@dataclass(frozen=True, slots=True)
class StartupDelay:
    enabled: bool
    seconds: int

    @property
    def effective_seconds(self) -> int:
        return self.seconds if self.enabled else 0


def validate_startup_delay_seconds(seconds: int) -> int:
    if not 1 <= seconds <= STARTUP_DELAY_MAX_SECONDS:
        raise SettingsValidationError(STARTUP_DELAY_OUT_OF_RANGE)
    return seconds
