import asyncio
from dataclasses import dataclass

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver

from ..config.bridge_defaults import BRIDGE_PORT, BRIDGE_STATE_FILE_PATH
from ..domain.log_function import LogFunction
from .pincode_service import PincodeService


@dataclass(frozen=True, slots=True)
class RunningBridge:
    driver: AccessoryDriver
    bridge: Bridge
    name: str

    @property
    def is_paired(self) -> bool:
        return self.driver.state.paired

    @property
    def pincode(self) -> str:
        return self.driver.state.pincode.decode()

    @property
    def setup_id(self) -> str:
        return self.driver.state.setup_id


class BridgeService:
    def __init__(self, *, pincode_service: PincodeService, log: LogFunction) -> None:
        self._pincode_service = pincode_service
        self._log = log
        self._running_bridge: RunningBridge | None = None

    @property
    def running_bridge(self) -> RunningBridge | None:
        return self._running_bridge

    async def create_bridge(self, name: str) -> RunningBridge:
        pincode = await self._pincode_service.get_or_create_pincode()
        driver = self._build_driver(pincode)
        bridge = self._build_bridge(driver, name)
        self._running_bridge = RunningBridge(driver=driver, bridge=bridge, name=name)
        return self._running_bridge

    async def publish_bridge(self) -> None:
        running_bridge = self._require_running_bridge()
        await running_bridge.driver.async_start()
        self._log(f"Bridge '{running_bridge.name}' published on port {BRIDGE_PORT}")

    async def stop_bridge(self) -> None:
        if self._running_bridge is None:
            return
        await self._running_bridge.driver.async_stop()
        self._running_bridge = None

    @staticmethod
    def _build_driver(pincode: str) -> AccessoryDriver:
        return AccessoryDriver(
            port=BRIDGE_PORT,
            persist_file=BRIDGE_STATE_FILE_PATH,
            pincode=pincode.encode(),
            loop=asyncio.get_running_loop(),
        )

    @staticmethod
    def _build_bridge(driver: AccessoryDriver, name: str) -> Bridge:
        bridge = Bridge(driver, name)
        driver.add_accessory(accessory=bridge)
        return bridge

    def _require_running_bridge(self) -> RunningBridge:
        if self._running_bridge is None:
            raise RuntimeError("The bridge has not been created yet")
        return self._running_bridge
