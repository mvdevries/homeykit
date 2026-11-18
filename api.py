from .routes.device_routes import get_devices, get_icons, set_exposed_devices
from .routes.pairing_routes import get_pairing
from .routes.settings_routes import (
    get_settings,
    set_bridge_name,
    set_pincode,
    set_startup_delay,
)

__all__ = [
    "get_pairing",
    "get_devices",
    "set_exposed_devices",
    "get_icons",
    "get_settings",
    "set_bridge_name",
    "set_pincode",
    "set_startup_delay",
]
