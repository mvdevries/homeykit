from typing import Any

from ..homekit.setup_uri import build_qr_code_svg, build_setup_uri
from .bridge_service import BridgeService, RunningBridge


class PairingService:
    def __init__(self, *, bridge_service: BridgeService) -> None:
        self._bridge_service = bridge_service

    def build_pairing_info(self) -> dict[str, Any]:
        running_bridge = self._bridge_service.running_bridge
        if running_bridge is None:
            return {"available": False}
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
