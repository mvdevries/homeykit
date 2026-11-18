from collections.abc import Callable
from typing import Any

from .bridge_service import BridgeService
from .ports import HomeKitBridge


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
        bridge = self._bridge_service.running_bridge
        if bridge is None:
            return {
                "available": False,
                "seconds_until_start": self._seconds_until_start_provider(),
            }
        return self._build_info_for_bridge(bridge)

    @staticmethod
    def _build_info_for_bridge(bridge: HomeKitBridge) -> dict[str, Any]:
        return {
            "available": True,
            "name": bridge.name,
            "paired": bridge.is_paired,
            "pincode": bridge.pincode,
            "qr_svg": bridge.qr_code_svg(),
        }
