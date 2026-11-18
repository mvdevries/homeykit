from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Capability:
    id: str
    value_type: str
    is_settable: bool
    value: Any


@dataclass(frozen=True, slots=True)
class HomeyDevice:
    id: str
    name: str
    device_class: str
    virtual_class: str | None
    zone_id: str | None
    is_available: bool
    capabilities: Mapping[str, Capability]
    icon_id: str | None = None
    icon_path: str | None = None

    @property
    def effective_class(self) -> str:
        return self.virtual_class or self.device_class

    def has_capability(self, capability_id: str) -> bool:
        return capability_id in self.capabilities
