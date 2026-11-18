from ..domain.bridge_name import normalize_bridge_name
from ..domain.defaults import BRIDGE_DEFAULT_NAME
from .error_logging import run_logging_errors
from .log_function import LogFunction
from .ports import BridgeNameRepository, DevicesGateway


class BridgeNameService:
    def __init__(
        self,
        *,
        bridge_name_repository: BridgeNameRepository,
        devices_gateway: DevicesGateway,
        log: LogFunction,
    ) -> None:
        self._bridge_name_repository = bridge_name_repository
        self._devices_gateway = devices_gateway
        self._log = log
        self._default_bridge_name = BRIDGE_DEFAULT_NAME

    @property
    def default_bridge_name(self) -> str:
        return self._default_bridge_name

    async def load_default_name_from_homey(self) -> None:
        homey_name = await run_logging_errors(
            self._log,
            "Reading the name of Homey failed",
            self._devices_gateway.fetch_homey_name,
        )
        if homey_name:
            self._default_bridge_name = homey_name

    def read_custom_bridge_name(self) -> str | None:
        return self._bridge_name_repository.read_custom_name()

    def resolve_bridge_name(self) -> str:
        return self.read_custom_bridge_name() or self._default_bridge_name

    async def set_custom_bridge_name(self, text: str | None) -> None:
        normalized_name = normalize_bridge_name(text)
        if normalized_name is None:
            await self._bridge_name_repository.clear_custom_name()
        else:
            await self._bridge_name_repository.save_custom_name(normalized_name)
