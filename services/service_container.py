from dataclasses import dataclass

from ..domain.log_function import LogFunction
from ..storage.pincode_store import PincodeStore
from ..storage.settings_storage import SettingsStorage
from .bridge_service import BridgeService
from .bridge_supervisor import BridgeSupervisor
from .pairing_service import PairingService
from .pincode_service import PincodeService


@dataclass(frozen=True, slots=True)
class ServiceContainer:
    bridge_supervisor: BridgeSupervisor
    pairing_service: PairingService


def build_service_container(
    *, settings: SettingsStorage, log: LogFunction
) -> ServiceContainer:
    pincode_service = PincodeService(PincodeStore(settings))
    bridge_service = BridgeService(pincode_service=pincode_service, log=log)
    return ServiceContainer(
        bridge_supervisor=BridgeSupervisor(bridge_service=bridge_service, log=log),
        pairing_service=PairingService(bridge_service=bridge_service),
    )
