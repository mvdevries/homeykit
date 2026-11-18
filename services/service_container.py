from dataclasses import dataclass

from ..domain.log_function import LogFunction
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from ..gateways.homey_web_api import HomeyWebApiClient, TokenSource
from ..storage.accessory_id_registry import AccessoryIdRegistry
from ..storage.exposed_devices_store import ExposedDevicesStore
from ..storage.pincode_store import PincodeStore
from ..storage.settings_storage import JsonSettingsAccess, SettingsStorage
from .bridge_service import BridgeService
from .bridge_supervisor import BridgeSupervisor
from .device_overview_service import DeviceOverviewService
from .device_sync_service import DeviceSyncService
from .icon_service import IconService
from .pairing_service import PairingService
from .pincode_service import PincodeService


@dataclass(frozen=True, slots=True)
class ServiceContainer:
    bridge_supervisor: BridgeSupervisor
    pairing_service: PairingService
    device_sync_service: DeviceSyncService
    device_overview_service: DeviceOverviewService
    icon_service: IconService
    web_api_client: HomeyWebApiClient

    async def close_connections(self) -> None:
        await self.web_api_client.close()


def build_service_container(
    *, settings: SettingsStorage, token_source: TokenSource, log: LogFunction
) -> ServiceContainer:
    settings_access = JsonSettingsAccess(settings)
    web_api_client = HomeyWebApiClient(token_source)
    devices_gateway = HomeyDevicesGateway(web_api_client)
    exposed_devices_store = ExposedDevicesStore(settings_access)
    pincode_service = PincodeService(PincodeStore(settings))
    bridge_service = BridgeService(pincode_service=pincode_service, log=log)
    device_sync_service = DeviceSyncService(
        devices_gateway=devices_gateway,
        exposed_devices_store=exposed_devices_store,
        accessory_id_registry=AccessoryIdRegistry(settings_access),
        log=log,
    )
    return ServiceContainer(
        bridge_supervisor=BridgeSupervisor(
            bridge_service=bridge_service,
            device_sync_service=device_sync_service,
            log=log,
        ),
        pairing_service=PairingService(bridge_service=bridge_service),
        device_sync_service=device_sync_service,
        device_overview_service=DeviceOverviewService(
            devices_gateway=devices_gateway,
            exposed_devices_store=exposed_devices_store,
        ),
        icon_service=IconService(devices_gateway=devices_gateway),
        web_api_client=web_api_client,
    )
