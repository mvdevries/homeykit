from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pyhap.const import (
    CATEGORY_LIGHTBULB,
    CATEGORY_OUTLET,
    CATEGORY_SENSOR,
    CATEGORY_SWITCH,
)

from ...domain.homey_device import HomeyDevice
from .value_conversions import (
    MIRED_MAX,
    MIRED_MIN,
    Converter,
    fraction_to_mireds,
    fraction_to_percentage,
    keep_value,
    mireds_to_fraction,
    percentage_to_fraction,
    to_bool,
    to_float,
    to_zero_or_one,
)

ON_OFF = "onoff"
DIM = "dim"
LIGHT_TEMPERATURE = "light_temperature"
LIGHT_MODE = "light_mode"
LIGHT_MODE_TEMPERATURE = "temperature"
DEVICE_CLASSES_WITHOUT_SENSOR_SERVICES = frozenset({"thermostat"})


@dataclass(frozen=True, slots=True)
class CapabilityBinding:
    capability_id: str
    characteristic_name: str
    to_homekit: Converter = keep_value
    to_homey: Converter | None = None
    characteristic_properties: Mapping[str, Any] | None = None
    capabilities_to_set_first: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class ServiceProfile:
    service_name: str
    category: int
    bindings: tuple[CapabilityBinding, ...]
    optional_characteristics: tuple[str, ...] = ()


def build_on_off_binding() -> CapabilityBinding:
    return CapabilityBinding(ON_OFF, "On", to_bool, to_bool)


def build_brightness_binding() -> CapabilityBinding:
    return CapabilityBinding(
        DIM, "Brightness", fraction_to_percentage, percentage_to_fraction
    )


def build_color_temperature_binding() -> CapabilityBinding:
    return CapabilityBinding(
        LIGHT_TEMPERATURE,
        "ColorTemperature",
        fraction_to_mireds,
        mireds_to_fraction,
        characteristic_properties={"minValue": MIRED_MIN, "maxValue": MIRED_MAX},
        capabilities_to_set_first=((LIGHT_MODE, LIGHT_MODE_TEMPERATURE),),
    )


def build_light_profile(device: HomeyDevice) -> ServiceProfile:
    bindings = [build_on_off_binding()]
    optional_characteristics: list[str] = []
    if device.has_capability(DIM):
        bindings.append(build_brightness_binding())
        optional_characteristics.append("Brightness")
    if device.has_capability(LIGHT_TEMPERATURE):
        bindings.append(build_color_temperature_binding())
        optional_characteristics.append("ColorTemperature")
    return ServiceProfile(
        service_name="Lightbulb",
        category=CATEGORY_LIGHTBULB,
        bindings=tuple(bindings),
        optional_characteristics=tuple(optional_characteristics),
    )


def build_outlet_profile() -> ServiceProfile:
    return ServiceProfile("Outlet", CATEGORY_OUTLET, (build_on_off_binding(),))


def build_switch_profile() -> ServiceProfile:
    return ServiceProfile("Switch", CATEGORY_SWITCH, (build_on_off_binding(),))


def build_main_service_profile(device: HomeyDevice) -> ServiceProfile | None:
    if not device.has_capability(ON_OFF):
        return None
    match device.effective_class:
        case "light":
            return build_light_profile(device)
        case "socket":
            return build_outlet_profile()
        case "other" | "switch":
            return build_switch_profile()
        case _:
            return None


def build_sensor_profile(
    service_name: str,
    capability_id: str,
    characteristic_name: str,
    to_homekit: Converter,
    characteristic_properties: Mapping[str, Any] | None = None,
) -> ServiceProfile:
    binding = CapabilityBinding(
        capability_id,
        characteristic_name,
        to_homekit,
        characteristic_properties=characteristic_properties,
    )
    return ServiceProfile(service_name, CATEGORY_SENSOR, (binding,))


SENSOR_PROFILES: tuple[tuple[str, ServiceProfile], ...] = (
    (
        "measure_temperature",
        build_sensor_profile(
            "TemperatureSensor",
            "measure_temperature",
            "CurrentTemperature",
            to_float,
            {"minValue": -50, "maxValue": 100},
        ),
    ),
    (
        "measure_humidity",
        build_sensor_profile(
            "HumiditySensor", "measure_humidity", "CurrentRelativeHumidity", to_float
        ),
    ),
    (
        "alarm_motion",
        build_sensor_profile("MotionSensor", "alarm_motion", "MotionDetected", to_bool),
    ),
    (
        "alarm_contact",
        build_sensor_profile(
            "ContactSensor", "alarm_contact", "ContactSensorState", to_zero_or_one
        ),
    ),
    (
        "alarm_water",
        build_sensor_profile(
            "LeakSensor", "alarm_water", "LeakDetected", to_zero_or_one
        ),
    ),
)


def build_sensor_profiles(device: HomeyDevice) -> tuple[ServiceProfile, ...]:
    if device.effective_class in DEVICE_CLASSES_WITHOUT_SENSOR_SERVICES:
        return ()
    return tuple(
        profile
        for capability_id, profile in SENSOR_PROFILES
        if device.has_capability(capability_id)
    )


def build_service_profiles(device: HomeyDevice) -> tuple[ServiceProfile, ...]:
    main_profile = build_main_service_profile(device)
    main_profiles = (main_profile,) if main_profile is not None else ()
    return main_profiles + build_sensor_profiles(device)


def is_device_supported(device: HomeyDevice) -> bool:
    return bool(build_service_profiles(device))
