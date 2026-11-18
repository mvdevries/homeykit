from ..config.bridge_defaults import BRIDGE_DEFAULT_NAME
from ..domain.bridge_name import normalize_bridge_name
from ..domain.log_function import LogFunction
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from ..storage.bridge_name_store import BridgeNameStore


class BridgeNameService:
    def __init__(
        self,
        *,
        bridge_name_store: BridgeNameStore,
        devices_gateway: HomeyDevicesGateway,
        log: LogFunction,
    ) -> None:
        self._bridge_name_store = bridge_name_store
        self._devices_gateway = devices_gateway
        self._log = log
        self._default_bridge_name = BRIDGE_DEFAULT_NAME

    @property
    def default_bridge_name(self) -> str:
        return self._default_bridge_name

    async def load_default_name_from_homey(self) -> None:
        try:
            homey_name = await self._devices_gateway.fetch_homey_name()
        except Exception as error:
            self._log(f"Reading the name of Homey failed: {error}")
            return
        if homey_name:
            self._default_bridge_name = homey_name

    def read_custom_bridge_name(self) -> str | None:
        return self._bridge_name_store.read_custom_name()

    def resolve_bridge_name(self) -> str:
        return self.read_custom_bridge_name() or self._default_bridge_name

    async def set_custom_bridge_name(self, text: str | None) -> None:
        normalized_name = normalize_bridge_name(text)
        if normalized_name is None:
            await self._bridge_name_store.clear_custom_name()
        else:
            await self._bridge_name_store.save_custom_name(normalized_name)
