from pytest_bdd import given, parsers, then, when

DEFAULT_ROW_OFFSET = 1


@given("a Homey with the old settings:")
def a_homey_with_old_settings(scenario, datatable):
    rows = datatable[DEFAULT_ROW_OFFSET:]
    scenario.settings.values.update(dict(rows))
    scenario.install_homey_app()


@given("the Homey app has started")
@when("the Homey app starts")
def the_homey_app_starts(scenario):
    scenario.call(scenario.homey_app_harness.app.on_init())


@when("the Homey app stops")
@when("the Homey app stops again")
def the_homey_app_stops(scenario):
    scenario.call(scenario.homey_app_harness.app.on_uninit())


@then("the old keys are gone")
def the_old_keys_are_gone(scenario):
    assert "aangeboden" not in scenario.settings.values
    assert "bridge_naam" not in scenario.settings.values


@then(parsers.parse('the setting "{key}" is "{value}"'))
def a_setting_has_a_value(scenario, key, value):
    assert scenario.settings.values[key] == value


@then("the services are gone")
def the_services_are_gone(scenario):
    assert scenario.homey_app_harness.app.services is None
