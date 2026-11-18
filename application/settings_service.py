from typing import Any

from .bridge_name_service import BridgeNameService
from .bridge_service import BridgeService
from .bridge_supervisor import BridgeSupervisor
from .pincode_service import PincodeService
from .startup_delay_service import StartupDelayService


class SettingsService:
    def __init__(
        self,
        *,
        bridge_name_service: BridgeNameService,
        pincode_service: PincodeService,
        startup_delay_service: StartupDelayService,
        bridge_service: BridgeService,
        bridge_supervisor: BridgeSupervisor,
    ) -> None:
        self._bridge_name_service = bridge_name_service
        self._pincode_service = pincode_service
        self._startup_delay_service = startup_delay_service
        self._bridge_service = bridge_service
        self._bridge_supervisor = bridge_supervisor

    async def build_settings_overview(self) -> dict[str, Any]:
        startup_delay = self._startup_delay_service.read_startup_delay()
        return {
            "bridge_name": self._bridge_name_service.resolve_bridge_name(),
            "default_bridge_name": self._bridge_name_service.default_bridge_name,
            "custom_bridge_name": self._bridge_name_service.read_custom_bridge_name(),
            "pincode": await self._pincode_service.get_or_create_pincode(),
            "startup_delay_enabled": startup_delay.enabled,
            "startup_delay_seconds": startup_delay.seconds,
            "bridge_running": self._bridge_service.running_bridge is not None,
            "seconds_until_start": self._bridge_supervisor.seconds_until_start(),
        }

    async def set_bridge_name(self, text: str | None) -> dict[str, Any]:
        await self._bridge_name_service.set_custom_bridge_name(text)
        if self._bridge_service.running_bridge is not None:
            await self._bridge_supervisor.restart_bridge()
        return await self.build_settings_overview()

    async def set_pincode(self, text: str | None) -> dict[str, Any]:
        new_pincode = await self._pincode_service.set_custom_or_random_pincode(text)
        self._bridge_service.apply_pincode_to_running_bridge(new_pincode)
        return await self.build_settings_overview()

    async def set_startup_delay(self, enabled: bool, seconds: int) -> dict[str, Any]:
        await self._startup_delay_service.save_startup_delay(enabled, seconds)
        return await self.build_settings_overview()
