from typing import Any

ZONES = [
    {"id": "zone-living-room", "name": "Living room"},
    {"id": "zone-kitchen", "name": "Kitchen"},
    {"id": "zone-bedroom", "name": "Bedroom"},
]

ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    '<circle cx="5" cy="5" r="4"/></svg>'
)

SENSOR_CLASS = "sensor"


def capability(
    capability_type: str, value: Any, *, settable: bool = False
) -> dict[str, Any]:
    return {"type": capability_type, "setable": settable, "value": value}


def device_payload(
    device_id: str,
    name: str,
    device_class: str,
    zone_id: str,
    capabilities: dict[str, dict[str, Any]],
    *,
    available: bool = True,
    virtual_class: str | None = None,
) -> dict[str, Any]:
    return {
        "id": device_id,
        "name": name,
        "class": device_class,
        "virtualClass": virtual_class,
        "zone": zone_id,
        "available": available,
        "capabilitiesObj": capabilities,
        "iconObj": {"id": f"icon-{device_class}", "url": f"/api/icon/{device_class}"},
    }


def build_sample_device_payloads() -> dict[str, dict[str, Any]]:
    payloads = [
        device_payload(
            "dimmable-lamp",
            "Dimmable lamp",
            "light",
            "zone-living-room",
            {
                "onoff": capability("boolean", True, settable=True),
                "dim": capability("number", 0.5, settable=True),
            },
        ),
        device_payload(
            "plain-lamp",
            "Plain lamp",
            "light",
            "zone-kitchen",
            {"onoff": capability("boolean", False, settable=True)},
        ),
        device_payload(
            "tunable-lamp",
            "Tunable white lamp",
            "light",
            "zone-bedroom",
            {
                "onoff": capability("boolean", True, settable=True),
                "dim": capability("number", 1.0, settable=True),
                "light_temperature": capability("number", 0.25, settable=True),
                "light_mode": capability("enum", "temperature", settable=True),
            },
        ),
        device_payload(
            "wall-socket",
            "Wall socket",
            "socket",
            "zone-living-room",
            {"onoff": capability("boolean", True, settable=True)},
        ),
        device_payload(
            "wall-switch",
            "Wall switch",
            "other",
            "zone-kitchen",
            {"onoff": capability("boolean", False, settable=True)},
            virtual_class="switch",
        ),
        device_payload(
            "climate-sensor",
            "Climate sensor",
            SENSOR_CLASS,
            "zone-bedroom",
            {
                "measure_temperature": capability("number", 21.5),
                "measure_humidity": capability("number", 48.0),
            },
        ),
        device_payload(
            "motion-sensor",
            "Motion sensor",
            SENSOR_CLASS,
            "zone-living-room",
            {"alarm_motion": capability("boolean", False)},
        ),
        device_payload(
            "door-sensor",
            "Door sensor",
            SENSOR_CLASS,
            "zone-kitchen",
            {"alarm_contact": capability("boolean", True)},
        ),
        device_payload(
            "leak-sensor",
            "Leak sensor",
            SENSOR_CLASS,
            "zone-kitchen",
            {"alarm_water": capability("boolean", False)},
        ),
        device_payload(
            "radiator-thermostat",
            "Radiator thermostat",
            "thermostat",
            "zone-bedroom",
            {
                "measure_temperature": capability("number", 19.0),
                "target_temperature": capability("number", 20.0, settable=True),
            },
        ),
    ]
    return {payload["id"]: payload for payload in payloads}


SUPPORTED_DEVICE_IDS = frozenset(
    {
        "dimmable-lamp",
        "plain-lamp",
        "tunable-lamp",
        "wall-socket",
        "wall-switch",
        "climate-sensor",
        "motion-sensor",
        "door-sensor",
        "leak-sensor",
    }
)
UNSUPPORTED_DEVICE_IDS = frozenset({"radiator-thermostat"})
