import re

from homeykit import api
from pytest_bdd import parsers, then, when

from tests.integration.steps.scenario_context import parse_device_ids

LISTED_DEVICE_FIELDS = {"id", "name", "zone", "supported", "exposed"}
CHANGE_PATTERNS = (
    (r'a pincode of "(.*)"', lambda value: (api.set_pincode, {"pincode": value})),
    (
        r"a startup delay of (\d+) seconds",
        lambda value: (
            api.set_startup_delay,
            {"enabled": True, "seconds": int(value)},
        ),
    ),
    (
        r"a bridge name of (\d+) characters",
        lambda value: (api.set_bridge_name, {"bridge_name": "x" * int(value)}),
    ),
)


def endpoint_and_body_for(change):
    for pattern, build in CHANGE_PATTERNS:
        match = re.fullmatch(pattern, change)
        if match:
            return build(match.group(1))
    raise LookupError(change)


@when("the device list is requested")
def the_device_list_is_requested(scenario):
    scenario.api_result = scenario.call_endpoint(api.get_devices)


@when(parsers.parse('the devices "{devices}" are chosen through the API'))
def the_devices_are_chosen_through_the_api(scenario, devices):
    scenario.api_result = scenario.call_endpoint(
        api.set_exposed_devices, {"exposed_device_ids": parse_device_ids(devices)}
    )


@when("the icons are requested")
def the_icons_are_requested(scenario):
    scenario.api_result = scenario.call_endpoint(api.get_icons)


@when("the pairing details are requested")
def the_pairing_details_are_requested(scenario):
    scenario.api_result = scenario.call_endpoint(api.get_pairing)


@when(parsers.parse('the bridge name is changed to "{name}" through the API'))
def the_bridge_name_is_changed(scenario, name):
    scenario.api_result = scenario.call_endpoint(
        api.set_bridge_name, {"bridge_name": name}
    )


@when(parsers.parse('the pincode is changed to "{pincode}" through the API'))
def the_pincode_is_changed(scenario, pincode):
    scenario.api_result = scenario.call_endpoint(api.set_pincode, {"pincode": pincode})


@when(
    parsers.parse("the startup delay is changed to {seconds:d} seconds through the API")
)
def the_startup_delay_is_changed(scenario, seconds):
    scenario.api_result = scenario.call_endpoint(
        api.set_startup_delay, {"enabled": True, "seconds": seconds}
    )


@when(parsers.parse("{change} is attempted through the API"))
def a_change_is_attempted(scenario, change):
    endpoint, body = endpoint_and_body_for(change)
    scenario.attempt_endpoint(endpoint, body)


@then(parsers.parse("{count:d} devices are listed"))
def devices_are_listed(scenario, count):
    assert len(scenario.api_result["devices"]) == count


@then("every listed device has an id, a name, a zone and its support and exposure")
def every_device_has_the_fields(scenario):
    for device in scenario.api_result["devices"]:
        assert set(device) >= LISTED_DEVICE_FIELDS


@then(parsers.parse('only "{device_id}" is marked as exposed in the list'))
def only_one_device_is_marked_as_exposed(scenario, device_id):
    exposed = [row["id"] for row in scenario.api_result["devices"] if row["exposed"]]
    assert exposed == [device_id]


@then("no icons are missing")
def no_icons_are_missing(scenario):
    assert scenario.api_result["missing_count"] == 0


@then("icons are returned")
def icons_are_returned(scenario):
    assert scenario.api_result["icons"]


@then(parsers.parse('the settings overview shows the bridge name "{name}"'))
def the_overview_shows_the_name(scenario, name):
    assert scenario.api_result["bridge_name"] == name
    assert scenario.api_result["custom_bridge_name"] == name


@then(parsers.parse('the settings overview shows the pincode "{pincode}"'))
def the_overview_shows_the_pincode(scenario, pincode):
    assert scenario.api_result["pincode"] == pincode


@then(
    parsers.parse("the settings overview shows a startup delay of {seconds:d} seconds")
)
def the_overview_shows_the_delay(scenario, seconds):
    assert scenario.api_result["startup_delay_enabled"] is True
    assert scenario.api_result["startup_delay_seconds"] == seconds


@then("the settings overview says the bridge is running")
def the_overview_says_the_bridge_is_running(scenario):
    assert scenario.api_result["bridge_running"] is True


@then("requesting the settings gives the same overview")
def requesting_the_settings_gives_the_same_overview(scenario):
    assert scenario.call_endpoint(api.get_settings) == scenario.api_result


@then(parsers.parse('the API answers with the error code "{code}"'))
def the_api_answers_with_an_error_code(scenario, code):
    assert scenario.api_error is not None
    assert scenario.api_error.error_code == code
