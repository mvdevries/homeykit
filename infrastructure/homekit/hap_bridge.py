import asyncio
from collections.abc import Callable

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver

from ...application.log_function import LogFunction
from ...application.ports import DevicesGateway, HomeKitBridge
from ...domain.defaults import BRIDGE_PORT, BRIDGE_STATE_FILE_PATH
from ...domain.homey_device import HomeyDevice
from .homey_accessory import HomeyAccessory
from .service_profiles import build_service_profiles
from .setup_uri import build_qr_code_svg, build_setup_uri


class HapHomeKitBridge:
    def __init__(
        self,
        *,
        driver: AccessoryDriver,
        bridge: Bridge,
        name: str,
        address: str,
        devices_gateway: DevicesGateway,
        log: LogFunction,
    ) -> None:
        self._driver = driver
        self._bridge = bridge
        self._name = name
        self._address = address
        self._devices_gateway = devices_gateway
        self._log = log
        self._accessories_by_device_id: dict[str, HomeyAccessory] = {}
        self._is_published = False
        self._device_written_listener: Callable[[str], None] = _ignore_device_written

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @property
    def is_paired(self) -> bool:
        return self._driver.state.paired

    @property
    def pincode(self) -> str:
        return self._driver.state.pincode.decode()

    @property
    def exposed_device_ids(self) -> frozenset[str]:
        return frozenset(self._accessories_by_device_id)

    def qr_code_svg(self) -> str:
        return build_qr_code_svg(self._build_setup_uri())

    def set_device_written_listener(self, listener: Callable[[str], None]) -> None:
        self._device_written_listener = listener

    def add_device(self, device: HomeyDevice, accessory_id: int) -> None:
        accessory = HomeyAccessory(
            driver=self._driver,
            device=device,
            profiles=build_service_profiles(device),
            devices_gateway=self._devices_gateway,
            accessory_id=accessory_id,
            log=self._log,
            on_capability_written=self._notify_device_written,
        )
        self._bridge.add_accessory(accessory)
        self._accessories_by_device_id[device.id] = accessory
        self._log(f"'{device.name}' is now exposed")

    def remove_device(self, device_id: str) -> None:
        accessory = self._accessories_by_device_id.pop(device_id)
        self._bridge.accessories.pop(accessory.aid, None)
        self._log(f"'{accessory.homey_device.name}' is no longer exposed")

    def update_device(self, device: HomeyDevice) -> None:
        self._accessories_by_device_id[device.id].update_from_device(device)

    def announce_configuration_change(self) -> None:
        if self._is_published:
            self._driver.config_changed()

    def apply_pincode(self, pincode: str) -> None:
        self._driver.state.pincode = pincode.encode()

    async def publish(self) -> None:
        await self._driver.async_start()
        self._is_published = True
        self._log(
            f"Bridge '{self._name}' published on port {BRIDGE_PORT} "
            f"at address {self._address}"
        )

    async def stop(self) -> None:
        await self._cancel_pending_writes()
        self._accessories_by_device_id.clear()
        self._is_published = False
        await self._driver.async_stop()

    async def _cancel_pending_writes(self) -> None:
        for accessory in self._accessories_by_device_id.values():
            await accessory.cancel_pending_writes()

    def _notify_device_written(self, device_id: str) -> None:
        self._device_written_listener(device_id)

    def _build_setup_uri(self) -> str:
        return build_setup_uri(
            category=self._bridge.category,
            pincode=self._driver.state.pincode,
            setup_id=self._driver.state.setup_id,
        )


def _ignore_device_written(device_id: str) -> None:
    return None


class HapBridgeFactory:
    def __init__(self, *, devices_gateway: DevicesGateway, log: LogFunction) -> None:
        self._devices_gateway = devices_gateway
        self._log = log

    def create(self, *, name: str, address: str, pincode: str) -> HomeKitBridge:
        driver = self._build_driver(pincode, address)
        bridge = self._build_bridge(driver, name)
        return HapHomeKitBridge(
            driver=driver,
            bridge=bridge,
            name=name,
            address=address,
            devices_gateway=self._devices_gateway,
            log=self._log,
        )

    @staticmethod
    def _build_driver(pincode: str, address: str) -> AccessoryDriver:
        return AccessoryDriver(
            address=address,
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
