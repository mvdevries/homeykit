from dataclasses import dataclass

from ..domain.log_function import LogFunction
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from ..gateways.homey_web_api import HomeyWebApiClient, TokenSource
from ..storage.accessory_id_registry import AccessoryIdRegistry
from ..storage.bridge_name_store import BridgeNameStore
from ..storage.exposed_devices_store import ExposedDevicesStore
from ..storage.pincode_store import PincodeStore
from ..storage.settings_storage import JsonSettingsAccess, SettingsStorage
from ..storage.startup_delay_store import StartupDelayStore
from .bridge_name_service import BridgeNameService
from .bridge_service import BridgeService
from .bridge_supervisor import BridgeSupervisor
from .device_overview_service import DeviceOverviewService
from .device_sync_service import DeviceSyncService
from .icon_service import IconService
from .pairing_service import PairingService
from .pincode_service import PincodeService
from .settings_service import SettingsService
from .startup_delay_service import StartupDelayService


@dataclass(frozen=True, slots=True)
class ServiceContainer:
    bridge_supervisor: BridgeSupervisor
    pairing_service: PairingService
    device_sync_service: DeviceSyncService
    device_overview_service: DeviceOverviewService
    icon_service: IconService
    settings_service: SettingsService
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
    bridge_name_service = BridgeNameService(
        bridge_name_store=BridgeNameStore(settings),
        devices_gateway=devices_gateway,
        log=log,
    )
    startup_delay_service = StartupDelayService(StartupDelayStore(settings))
    bridge_supervisor = BridgeSupervisor(
        bridge_service=bridge_service,
        device_sync_service=device_sync_service,
        bridge_name_service=bridge_name_service,
        startup_delay_service=startup_delay_service,
        log=log,
    )
    return ServiceContainer(
        bridge_supervisor=bridge_supervisor,
        pairing_service=PairingService(
            bridge_service=bridge_service,
            seconds_until_start_provider=bridge_supervisor.seconds_until_start,
        ),
        device_sync_service=device_sync_service,
        device_overview_service=DeviceOverviewService(
            devices_gateway=devices_gateway,
            exposed_devices_store=exposed_devices_store,
        ),
        icon_service=IconService(devices_gateway=devices_gateway),
        settings_service=SettingsService(
            bridge_name_service=bridge_name_service,
            pincode_service=pincode_service,
            startup_delay_service=startup_delay_service,
            bridge_service=bridge_service,
            bridge_supervisor=bridge_supervisor,
        ),
        web_api_client=web_api_client,
    )
