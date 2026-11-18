from collections.abc import Callable
from typing import Any

from ..infrastructure.homekit.bridge_service import BridgeService, RunningBridge
from ..infrastructure.homekit.setup_uri import build_qr_code_svg, build_setup_uri


class PairingService:
    def __init__(
        self,
        *,
        bridge_service: BridgeService,
        seconds_until_start_provider: Callable[[], int | None],
    ) -> None:
        self._bridge_service = bridge_service
        self._seconds_until_start_provider = seconds_until_start_provider

    def build_pairing_info(self) -> dict[str, Any]:
        running_bridge = self._bridge_service.running_bridge
        if running_bridge is None:
            return {
                "available": False,
                "seconds_until_start": self._seconds_until_start_provider(),
            }
        return self._build_info_for_running_bridge(running_bridge)

    def _build_info_for_running_bridge(
        self, running_bridge: RunningBridge
    ) -> dict[str, Any]:
        setup_uri = self._build_setup_uri(running_bridge)
        return {
            "available": True,
            "name": running_bridge.name,
            "paired": running_bridge.is_paired,
            "pincode": running_bridge.pincode,
            "qr_svg": build_qr_code_svg(setup_uri),
        }

    @staticmethod
    def _build_setup_uri(running_bridge: RunningBridge) -> str:
        return build_setup_uri(
            category=running_bridge.bridge.category,
            pincode=running_bridge.driver.state.pincode,
            setup_id=running_bridge.setup_id,
        )
