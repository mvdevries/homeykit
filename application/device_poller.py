from ..domain.defaults import DEVICE_SYNC_INTERVAL_SECONDS
from .background_tasks import PeriodicTask
from .device_sync_service import DeviceSyncService
from .log_function import LogFunction


class DevicePoller:
    def __init__(
        self,
        *,
        device_sync_service: DeviceSyncService,
        log: LogFunction,
        interval_seconds: float = DEVICE_SYNC_INTERVAL_SECONDS,
    ) -> None:
        self._periodic_task = PeriodicTask(
            interval_seconds=interval_seconds,
            action=device_sync_service.synchronize_once,
            log=log,
            failure_message="Device synchronization failed",
        )

    def start(self) -> None:
        self._periodic_task.start()

    async def stop(self) -> None:
        await self._periodic_task.stop()
