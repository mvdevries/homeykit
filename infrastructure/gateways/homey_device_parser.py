from collections.abc import Mapping
from typing import Any

from ...domain.homey_device import Capability, HomeyDevice


def parse_capability(capability_id: str, payload: Mapping[str, Any]) -> Capability:
    return Capability(
        id=capability_id,
        value_type=str(payload.get("type", "")),
        is_settable=bool(payload.get("setable")),
        value=payload.get("value"),
    )


def parse_capabilities(device_payload: Mapping[str, Any]) -> dict[str, Capability]:
    capability_payloads = device_payload.get("capabilitiesObj") or {}
    return {
        capability_id: parse_capability(capability_id, capability_payload)
        for capability_id, capability_payload in capability_payloads.items()
    }


def read_icon_field(device_payload: Mapping[str, Any], field_name: str) -> str | None:
    icon_payload = device_payload.get("iconObj") or {}
    return icon_payload.get(field_name)


def parse_homey_device(payload: Mapping[str, Any]) -> HomeyDevice:
    return HomeyDevice(
        id=payload["id"],
        name=payload.get("name") or payload["id"],
        device_class=payload.get("class") or "other",
        virtual_class=payload.get("virtualClass"),
        zone_id=payload.get("zone"),
        is_available=bool(payload.get("available", True)),
        capabilities=parse_capabilities(payload),
        icon_id=read_icon_field(payload, "id"),
        icon_path=read_icon_field(payload, "url"),
    )
