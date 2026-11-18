import re
from dataclasses import dataclass, field
from typing import Any

import pytest
from playwright.sync_api import expect
from pytest_bdd import parsers, then, when

PINCODE_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{3}$")
FILTER_IDS = {
    "Active": "filter-active",
    "Inactive": "filter-inactive",
    "Not supported": "filter-unsupported",
}
PAGE_FRAGMENTS = {
    "settings": "",
    "devices": "#devices",
    "name": "#name",
    "pincode": "#pincode",
    "startup": "#startup",
}


@dataclass
class PageContext:
    page: Any
    backend: Any
    open_page: Any
    remembered: dict[str, str] = field(default_factory=dict)


@pytest.fixture
def pages(page, backend, settings_page):
    return PageContext(page=page, backend=backend, open_page=settings_page)


@when(parsers.parse("I open the {name} page"))
def i_open_a_page(pages, name):
    pages.open_page(fragment=PAGE_FRAGMENTS[name])


@when("I open the settings page in Dutch")
def i_open_the_settings_page_in_dutch(pages):
    pages.open_page("nl")


@then("I see the pairing section with a QR code")
def i_see_the_pairing_section(pages):
    expect(pages.page.locator("#pairing-section")).to_be_visible()
    expect(pages.page.locator("#qr-code svg")).to_be_visible()


@then("I see a pincode in the form 123-45-678")
def i_see_a_pincode(pages):
    expect(pages.page.locator("#pincode-display")).to_have_text(PINCODE_PATTERN)


@then(parsers.parse('the name menu item says "{text}"'))
def the_name_menu_item_says(pages, text):
    expect(pages.page.locator("#menu-name-subtitle")).to_have_text(text)


@then(parsers.parse('the startup menu item says "{text}"'))
def the_startup_menu_item_says(pages, text):
    expect(pages.page.locator("#menu-startup-subtitle")).to_have_text(text)


@then(parsers.parse('the first menu item is "{text}"'))
def the_first_menu_item_is(pages, text):
    expect(pages.page.locator(".menu-title").first).to_have_text(text)


@when(parsers.parse('I switch the "{name}" filter'))
def i_switch_a_filter(pages, name):
    pages.page.locator(f"#{FILTER_IDS[name]}").click()


@when(parsers.parse('I search for "{text}"'))
def i_search_for(pages, text):
    pages.page.locator("#device-search").fill(text)


@when(parsers.parse('I switch on "{device}"'))
def i_switch_on_a_device(pages, device):
    pages.page.get_by_role("switch", name=device).click()


@when(parsers.parse('I try to switch on "{device}"'))
def i_try_to_switch_on_a_device(pages, device):
    pages.page.get_by_role("switch", name=device).click(force=True)


@then(parsers.parse("I see {count:d} devices"))
@then(parsers.parse("I see {count:d} device"))
def i_see_devices(pages, count):
    expect(pages.page.locator(".device-row")).to_have_count(count)


@then(parsers.parse("I see {count:d} unsupported devices"))
@then(parsers.parse("I see {count:d} unsupported device"))
def i_see_unsupported_devices(pages, count):
    expect(pages.page.locator(".device-row.unsupported")).to_have_count(count)


@then("I am asked to choose a filter")
def i_am_asked_to_choose_a_filter(pages):
    expect(pages.page.locator(".empty-title")).to_have_text("No filter selected")


@then("I am told that no devices were found")
def i_am_told_no_devices_were_found(pages):
    expect(pages.page.locator(".empty-title")).to_have_text("No devices found")


@then(parsers.parse('the page confirms with "{text}"'))
def the_page_confirms_with(pages, text):
    expect(pages.page.locator("#toast")).to_have_text(text)


@then(parsers.parse('I see a message containing "{text}"'))
def i_see_a_message_containing(pages, text):
    expect(pages.page.locator("#toast")).to_contain_text(text)


@then(parsers.parse("the app exposes {count:d} device"))
def the_app_exposes_devices(pages, count):
    service = pages.backend.app.container.device_sync_service
    assert service.exposed_accessory_count == count


@then(parsers.parse('the summary mentions "{text}"'))
def the_summary_mentions(pages, text):
    expect(pages.page.locator("#device-summary")).to_contain_text(text)


@then(parsers.parse('the switch of "{device}" is disabled'))
def the_switch_is_disabled(pages, device):
    switch = pages.page.get_by_role("switch", name=device)
    expect(switch).to_have_attribute("aria-disabled", "true")


@then(parsers.parse('the switch of "{device}" stays off'))
def the_switch_stays_off(pages, device):
    switch = pages.page.get_by_role("switch", name=device)
    expect(switch).to_have_attribute("aria-checked", "false")


@when(parsers.parse('I enter the bridge name "{name}"'))
def i_enter_the_bridge_name(pages, name):
    pages.page.locator("#bridge-name-input").fill(name)


@when(parsers.parse("I enter a bridge name of {count:d} characters"))
def i_enter_a_long_bridge_name(pages, count):
    field_locator = pages.page.locator("#bridge-name-input")
    field_locator.evaluate("input => input.removeAttribute('maxlength')")
    field_locator.fill("x" * count)


@when("I save the name")
def i_save_the_name(pages):
    pages.page.locator("#bridge-name-save").click()


@when("I restore the default name")
def i_restore_the_default_name(pages):
    pages.page.locator("#bridge-name-restore").click()


@then(parsers.parse('the bridge is named "{name}"'))
def the_bridge_is_named(pages, name):
    pairing = pages.backend.app.container.pairing_service.build_pairing_info()
    assert pairing["name"] == name


@then(parsers.parse('the name field shows "{name}"'))
def the_name_field_shows(pages, name):
    expect(pages.page.locator("#bridge-name-input")).to_have_value(name)


@when(parsers.parse('I enter the pincode "{pincode}"'))
def i_enter_the_pincode(pages, pincode):
    pages.page.locator("#pincode-input").fill(pincode)


@when("I save the pincode")
def i_save_the_pincode(pages):
    pages.page.locator("#pincode-save").click()


@when("I remember the current pincode")
def i_remember_the_current_pincode(pages):
    pages.remembered["pincode"] = pages.page.locator("#pincode-current").inner_text()


@when("I ask for a new random pincode")
def i_ask_for_a_random_pincode(pages):
    pages.page.locator("#pincode-random").click()


@then(parsers.parse('the current pincode shows "{pincode}"'))
def the_current_pincode_shows(pages, pincode):
    expect(pages.page.locator("#pincode-current")).to_have_text(pincode)


@then("the current pincode is different")
def the_current_pincode_is_different(pages):
    expect(pages.page.locator("#pincode-current")).not_to_have_text(
        pages.remembered["pincode"]
    )


@then(parsers.parse('the bridge has the pincode "{pincode}"'))
def the_bridge_has_the_pincode(pages, pincode):
    pairing = pages.backend.app.container.pairing_service.build_pairing_info()
    assert pairing["pincode"] == pincode


@when("I switch on the startup delay")
def i_switch_on_the_startup_delay(pages):
    pages.page.get_by_role("switch").first.click()


@when(parsers.parse("I enter a delay of {seconds:d} seconds"))
def i_enter_a_delay(pages, seconds):
    seconds_field = pages.page.locator("#startup-delay-seconds")
    seconds_field.fill(str(seconds))
    seconds_field.blur()


@then(parsers.parse("the app stores a startup delay of {seconds:d} seconds"))
def the_app_stores_a_startup_delay(pages, seconds):
    stored = pages.backend.app.settings.values
    assert stored["startup_delay_enabled"] is True
    assert stored["startup_delay_seconds"] == seconds
