from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DeviceRow:
    id: str
    name: str
    zone: str | None
    device_class: str
    icon_id: str | None
    is_supported: bool
    is_exposed: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "zone": self.zone,
            "device_class": self.device_class,
            "icon_id": self.icon_id,
            "supported": self.is_supported,
            "exposed": self.is_exposed,
        }
