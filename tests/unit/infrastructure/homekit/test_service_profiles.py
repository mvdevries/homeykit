import pytest
from homeykit.infrastructure.gateways.homey_device_parser import parse_homey_device
from homeykit.infrastructure.homekit.service_profiles import (
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


class TestBuildServiceProfiles:
    @pytest.mark.parametrize(("device_id", "services"), EXPECTED_SERVICES.items())
    def test_given_a_sample_device_when_profiles_are_built_then_it_gets_its_services(
        self, devices, device_id, services
    ):
        profiles = build_service_profiles(devices[device_id])

        assert [profile.service_name for profile in profiles] == services

    def test_given_a_tunable_lamp_when_built_then_brightness_and_temperature_are_added(
        self, devices
    ):
        profile = build_service_profiles(devices["tunable-lamp"])[0]

        capability_ids = [binding.capability_id for binding in profile.bindings]
        assert profile.optional_characteristics == ("Brightness", "ColorTemperature")
        assert capability_ids == ["onoff", "dim", "light_temperature"]

    def test_given_colour_temperature_when_built_then_the_light_mode_is_set_first(
        self, devices
    ):
        profile = build_service_profiles(devices["tunable-lamp"])[0]

        binding = profile.bindings[-1]

        assert binding.capabilities_to_set_first == (("light_mode", "temperature"),)

    def test_given_sensors_when_profiles_are_built_then_they_are_read_only(
        self, devices
    ):
        profiles = build_service_profiles(devices["climate-sensor"])

        assert all(
            binding.to_homey is None
            for profile in profiles
            for binding in profile.bindings
        )

    def test_given_a_light_without_onoff_when_profiles_are_built_then_there_are_none(
        self,
    ):
        device = parse_homey_device(
            {"id": "x", "class": "light", "capabilitiesObj": {"dim": {"value": 1}}}
        )

        profiles = build_service_profiles(device)

        assert profiles == ()


class TestIsDeviceSupported:
    def test_given_the_sample_devices_when_checked_then_only_the_expected_are_supported(
        self, devices
    ):
        supported = {
            key for key, device in devices.items() if is_device_supported(device)
        }

        assert supported == SUPPORTED_DEVICE_IDS
        assert UNSUPPORTED_DEVICE_IDS.isdisjoint(supported)
