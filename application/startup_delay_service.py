from ..domain.defaults import STARTUP_DELAY_DEFAULT_SECONDS
from ..domain.startup_delay import StartupDelay, validate_startup_delay_seconds
from .ports import StartupDelayRepository


class StartupDelayService:
    def __init__(self, startup_delay_repository: StartupDelayRepository) -> None:
        self._startup_delay_repository = startup_delay_repository

    def read_startup_delay(self) -> StartupDelay:
        stored_seconds = self._startup_delay_repository.read_seconds()
        return StartupDelay(
            enabled=self._startup_delay_repository.read_enabled(),
            seconds=STARTUP_DELAY_DEFAULT_SECONDS
            if stored_seconds is None
            else stored_seconds,
        )

    async def save_startup_delay(self, enabled: bool, seconds: int) -> StartupDelay:
        valid_seconds = validate_startup_delay_seconds(seconds)
        await self._startup_delay_repository.save(enabled, valid_seconds)
        return StartupDelay(enabled=bool(enabled), seconds=valid_seconds)
