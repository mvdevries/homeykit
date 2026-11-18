import pytest
from homeykit.gateways.homey_device_parser import parse_homey_device
from homeykit.homekit.service_profiles import (
    build_service_profiles,
    is_device_supported,
)

from tests.support.sample_devices import (
    SUPPORTED_DEVICE_IDS,
    UNSUPPORTED_DEVICE_IDS,
    build_sample_device_payloads,
)

EXPECTED_SERVICES = {
    "dimmable-lamp": ["Lightbulb"],
    "plain-lamp": ["Lightbulb"],
    "tunable-lamp": ["Lightbulb"],
    "wall-socket": ["Outlet"],
    "wall-switch": ["Switch"],
    "climate-sensor": ["TemperatureSensor", "HumiditySensor"],
    "motion-sensor": ["MotionSensor"],
    "door-sensor": ["ContactSensor"],
    "leak-sensor": ["LeakSensor"],
    "radiator-thermostat": [],
}


@pytest.fixture(scope="module")
def devices():
    payloads = build_sample_device_payloads()
    return {key: parse_homey_device(payload) for key, payload in payloads.items()}


class TestParser:
    def test_parses_basic_fields(self, devices):
        lamp = devices["dimmable-lamp"]
        assert (lamp.id, lamp.name, lamp.device_class) == (
            "dimmable-lamp",
            "Dimmable lamp",
            "light",
        )
        assert lamp.zone_id == "zone-living-room"
        assert lamp.is_available is True
        assert lamp.icon_id == "icon-light"
        assert lamp.icon_path == "/api/icon/light"

    def test_parses_capabilities(self, devices):
        dim = devices["dimmable-lamp"].capabilities["dim"]
        assert (dim.value_type, dim.is_settable, dim.value) == ("number", True, 0.5)

    def test_virtual_class_takes_precedence(self, devices):
        switch = devices["wall-switch"]
        assert switch.device_class == "other"
        assert switch.effective_class == "switch"

    def test_applies_defaults_for_missing_fields(self):
        device = parse_homey_device({"id": "bare"})
        assert device.name == "bare"
        assert device.device_class == "other"
        assert device.capabilities == {}
        assert device.icon_id is None
        assert device.is_available is True

    def test_has_capability(self, devices):
        assert devices["dimmable-lamp"].has_capability("dim")
        assert not devices["plain-lamp"].has_capability("dim")


class TestProfiles:
    @pytest.mark.parametrize(("device_id", "services"), EXPECTED_SERVICES.items())
    def test_chooses_services(self, devices, device_id, services):
        profiles = build_service_profiles(devices[device_id])
        assert [profile.service_name for profile in profiles] == services

    def test_supported_devices(self, devices):
        supported = {
            key for key, device in devices.items() if is_device_supported(device)
        }
        assert supported == SUPPORTED_DEVICE_IDS
        assert UNSUPPORTED_DEVICE_IDS.isdisjoint(supported)

    def test_tunable_lamp_has_brightness_and_color_temperature(self, devices):
        profile = build_service_profiles(devices["tunable-lamp"])[0]
        assert profile.optional_characteristics == ("Brightness", "ColorTemperature")
        capability_ids = [binding.capability_id for binding in profile.bindings]
        assert capability_ids == ["onoff", "dim", "light_temperature"]

    def test_color_temperature_sets_light_mode_first(self, devices):
        profile = build_service_profiles(devices["tunable-lamp"])[0]
        binding = profile.bindings[-1]
        assert binding.capabilities_to_set_first == (("light_mode", "temperature"),)

    def test_sensors_are_read_only(self, devices):
        for profile in build_service_profiles(devices["climate-sensor"]):
            assert all(binding.to_homey is None for binding in profile.bindings)

    def test_device_without_onoff_is_no_light(self):
        device = parse_homey_device(
            {"id": "x", "class": "light", "capabilitiesObj": {"dim": {"value": 1}}}
        )
        assert build_service_profiles(device) == ()
