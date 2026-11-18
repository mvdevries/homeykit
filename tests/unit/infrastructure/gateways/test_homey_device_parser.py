import pytest
from homeykit.infrastructure.gateways.homey_device_parser import parse_homey_device

from tests.support.sample_devices import build_sample_device_payloads


@pytest.fixture(scope="module")
def devices():
    payloads = build_sample_device_payloads()
    return {key: parse_homey_device(payload) for key, payload in payloads.items()}


class TestParseHomeyDevice:
    def test_given_a_lamp_payload_when_parsed_then_the_basic_fields_are_read(
        self, devices
    ):
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

    def test_given_capabilities_when_parsed_then_type_settable_and_value_are_read(
        self, devices
    ):
        dim = devices["dimmable-lamp"].capabilities["dim"]

        assert (dim.value_type, dim.is_settable, dim.value) == ("number", True, 0.5)

    def test_given_a_virtual_class_when_parsed_then_it_takes_precedence(self, devices):
        switch = devices["wall-switch"]

        assert switch.device_class == "other"
        assert switch.effective_class == "switch"

    def test_given_a_bare_payload_when_parsed_then_defaults_are_applied(self):
        device = parse_homey_device({"id": "bare"})

        assert device.name == "bare"
        assert device.device_class == "other"
        assert device.capabilities == {}
        assert device.icon_id is None
        assert device.is_available is True

    def test_given_a_device_when_asked_for_a_capability_then_presence_is_reported(
        self, devices
    ):
        assert devices["dimmable-lamp"].has_capability("dim")
        assert not devices["plain-lamp"].has_capability("dim")
