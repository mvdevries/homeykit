from dataclasses import dataclass

from ..domain.log_function import LogFunction
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from ..gateways.homey_web_api import HomeyWebApiClient, TokenSource
from ..repositories.accessory_id_repository import AccessoryIdRepository
from ..repositories.bridge_name_repository import BridgeNameRepository
from ..repositories.exposed_devices_repository import ExposedDevicesRepository
from ..repositories.pincode_repository import PincodeRepository
from ..repositories.settings_storage import JsonSettingsAccess, SettingsStorage
from ..repositories.startup_delay_repository import StartupDelayRepository
from .address_watchdog import AddressWatchdog
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
    address_watchdog: AddressWatchdog
    web_api_client: HomeyWebApiClient

    async def close_connections(self) -> None:
        await self.web_api_client.close()


def build_service_container(
    *, settings: SettingsStorage, token_source: TokenSource, log: LogFunction
) -> ServiceContainer:
    settings_access = JsonSettingsAccess(settings)
    web_api_client = HomeyWebApiClient(token_source)
    devices_gateway = HomeyDevicesGateway(web_api_client)
    exposed_devices_repository = ExposedDevicesRepository(settings_access)
    pincode_service = PincodeService(PincodeRepository(settings))
    bridge_service = BridgeService(pincode_service=pincode_service, log=log)
    device_sync_service = DeviceSyncService(
        devices_gateway=devices_gateway,
        exposed_devices_repository=exposed_devices_repository,
        accessory_id_repository=AccessoryIdRepository(settings_access),
        log=log,
    )
    bridge_name_service = BridgeNameService(
        bridge_name_repository=BridgeNameRepository(settings),
        devices_gateway=devices_gateway,
        log=log,
    )
    startup_delay_service = StartupDelayService(StartupDelayRepository(settings))
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
            exposed_devices_repository=exposed_devices_repository,
        ),
        icon_service=IconService(devices_gateway=devices_gateway),
        settings_service=SettingsService(
            bridge_name_service=bridge_name_service,
            pincode_service=pincode_service,
            startup_delay_service=startup_delay_service,
            bridge_service=bridge_service,
            bridge_supervisor=bridge_supervisor,
        ),
        address_watchdog=AddressWatchdog(
            read_current_address=bridge_supervisor.current_address,
            on_address_changed=bridge_supervisor.restart_bridge_on_new_address,
            log=log,
        ),
        web_api_client=web_api_client,
    )
