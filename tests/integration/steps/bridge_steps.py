from pytest_bdd import given, parsers, then, when

from tests.integration.steps.scenario_context import port_is_open, wait_until
from tests.support.running_app import LOOPBACK_ADDRESS

NEW_ADDRESS = "0.0.0.0"
STARTUP_DELAY_WAIT_SECONDS = 10


@given("the app is installed on a Homey")
def the_app_is_installed(scenario):
    scenario.install_app()


@given("the app is running")
def the_app_is_running(scenario):
    scenario.install_app()
    scenario.start_app()


@when("the app starts")
def the_app_starts(scenario):
    scenario.start_app()


@when("the app stops")
def the_app_stops(scenario):
    scenario.stop_app()


@when("the app is restarted")
def the_app_is_restarted(scenario):
    scenario.restart_app()


@given("the current pincode is remembered")
def the_pincode_is_remembered(scenario):
    scenario.remembered["pincode"] = scenario.pairing_details()["pincode"]


@then("the pincode is the same as before")
def the_pincode_is_the_same(scenario):
    assert scenario.pairing_details()["pincode"] == scenario.remembered["pincode"]


@given("the Homey has no network address yet")
def the_homey_has_no_address(scenario):
    scenario.running_app.network_address[0] = None


@when("the Homey gets a network address")
def the_homey_gets_an_address(scenario):
    scenario.running_app.network_address[0] = LOOPBACK_ADDRESS


@when("the Homey gets a new IP address")
def the_homey_gets_a_new_address(scenario):
    scenario.running_app.network_address[0] = NEW_ADDRESS


@when("the IP address is checked")
def the_address_is_checked(scenario):
    scenario.call(scenario.container.address_watchdog.check_address_once())


@given(parsers.parse("a startup delay of {seconds:d} seconds"))
def a_startup_delay(scenario, seconds):
    scenario.call(scenario.container.settings_service.set_startup_delay(True, seconds))


@when("the startup delay has passed")
def the_startup_delay_has_passed(scenario):
    wait_until(
        lambda: scenario.pairing_details()["available"], STARTUP_DELAY_WAIT_SECONDS
    )


@when(parsers.parse('the pincode is set to "{pincode}"'))
def the_pincode_is_set(scenario, pincode):
    scenario.call(scenario.container.settings_service.set_pincode(pincode))


@when(parsers.parse('the bridge name is set to "{name}"'))
def the_bridge_name_is_set(scenario, name):
    scenario.call(scenario.container.settings_service.set_bridge_name(name))


@then("the bridge is reachable on its port")
def the_bridge_is_reachable(scenario):
    wait_until(lambda: port_is_open(scenario.port))


@then("the bridge becomes reachable on its port")
def the_bridge_becomes_reachable(scenario):
    wait_until(lambda: port_is_open(scenario.port), STARTUP_DELAY_WAIT_SECONDS)


@then("the bridge is not reachable")
def the_bridge_is_not_reachable(scenario):
    assert not port_is_open(scenario.port)


@then("the bridge is no longer reachable")
def the_bridge_is_no_longer_reachable(scenario):
    assert not port_is_open(scenario.port)


@then("the bridge runs on the local address")
def the_bridge_runs_on_the_local_address(scenario):
    assert scenario.run(scenario.container.bridge_supervisor.current_address) == (
        LOOPBACK_ADDRESS
    )


@then("the bridge runs on the new address")
def the_bridge_runs_on_the_new_address(scenario):
    assert scenario.run(scenario.container.bridge_supervisor.current_address) == (
        NEW_ADDRESS
    )


@then("the log says the bridge is published")
def the_log_says_published(scenario):
    assert scenario.log.contains("published on port")


@then("the log says the IP address changed")
def the_log_says_the_address_changed(scenario):
    assert scenario.log.contains("IP address changed")


@then(parsers.parse('the log says "{text}"'))
def the_log_says(scenario, text):
    assert scenario.log.contains(text)


@then(parsers.parse('the pairing details show the bridge name "{name}"'))
def the_pairing_details_show_the_name(scenario, name):
    assert scenario.pairing_details()["name"] == name


@then(parsers.parse('the pairing details show the pincode "{pincode}"'))
def the_pairing_details_show_the_pincode(scenario, pincode):
    assert scenario.pairing_details()["pincode"] == pincode


@then("the bridge is not paired yet")
def the_bridge_is_not_paired(scenario):
    assert scenario.pairing_details()["paired"] is False


@then("the pairing details contain an eight digit pincode and a QR code")
def the_pairing_details_are_complete(scenario):
    details = scenario.pairing_details()
    assert len(details["pincode"].replace("-", "")) == 8
    assert details["qr_svg"].startswith("<svg")


@then("the pairing details are not available yet")
def the_pairing_details_are_not_available(scenario):
    assert scenario.pairing_details()["available"] is False


@then("the pairing details are available")
def the_pairing_details_are_available(scenario):
    assert scenario.pairing_details()["available"] is True


@then("the pairing details count down to the start")
def the_pairing_details_count_down(scenario):
    seconds = scenario.pairing_details()["seconds_until_start"]
    assert seconds is not None and 0 < seconds <= 2
