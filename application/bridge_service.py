from .pincode_service import PincodeService
from .ports import HomeKitBridge, HomeKitBridgeFactory


class BridgeService:
    def __init__(
        self,
        *,
        bridge_factory: HomeKitBridgeFactory,
        pincode_service: PincodeService,
    ) -> None:
        self._bridge_factory = bridge_factory
        self._pincode_service = pincode_service
        self._running_bridge: HomeKitBridge | None = None

    @property
    def running_bridge(self) -> HomeKitBridge | None:
        return self._running_bridge

    async def create_bridge(self, name: str, address: str) -> HomeKitBridge:
        pincode = await self._pincode_service.get_or_create_pincode()
        self._running_bridge = self._bridge_factory.create(
            name=name, address=address, pincode=pincode
        )
        return self._running_bridge

    async def publish_bridge(self) -> None:
        await self._require_running_bridge().publish()

    def apply_pincode_to_running_bridge(self, pincode: str) -> None:
        if self._running_bridge is None:
            return
        self._running_bridge.apply_pincode(pincode)

    async def stop_bridge(self) -> None:
        if self._running_bridge is None:
            return
        await self._running_bridge.stop()
        self._running_bridge = None

    def _require_running_bridge(self) -> HomeKitBridge:
        if self._running_bridge is None:
            raise RuntimeError("The bridge has not been created yet")
        return self._running_bridge
