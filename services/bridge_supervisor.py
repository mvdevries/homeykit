from ..config.bridge_defaults import BRIDGE_DEFAULT_NAME
from ..domain.log_function import LogFunction
from .bridge_service import BridgeService


class BridgeSupervisor:
    def __init__(self, *, bridge_service: BridgeService, log: LogFunction) -> None:
        self._bridge_service = bridge_service
        self._log = log

    async def start(self) -> None:
        await self._start_bridge()

    async def shutdown(self) -> None:
        await self._stop_bridge()

    async def _start_bridge(self) -> None:
        await self._bridge_service.create_bridge(name=BRIDGE_DEFAULT_NAME)
        await self._bridge_service.publish_bridge()

    async def _stop_bridge(self) -> None:
        await self._bridge_service.stop_bridge()
