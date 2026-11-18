import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e

PINCODE_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{3}$")


def test_start_page_shows_pairing_details(settings_page):
    page = settings_page()
    expect(page.locator("#pairing-section")).to_be_visible()
    expect(page.locator("#qr-code svg")).to_be_visible()
    expect(page.locator("#pincode-display")).to_have_text(PINCODE_PATTERN)


def test_start_page_menu_subtitles_are_filled(settings_page):
    page = settings_page()
    expect(page.locator("#menu-name-subtitle")).to_have_text("Test Homey")
    expect(page.locator("#menu-startup-subtitle")).to_have_text("Starts immediately")


def test_pages_are_translated_to_dutch(settings_page):
    page = settings_page("nl")
    expect(page.locator(".menu-title").first).to_have_text("Apparaten")
    expect(page.locator("#menu-startup-subtitle")).to_have_text("Direct starten")


def test_devices_page_shows_supported_devices_by_default(settings_page):
    page = settings_page(fragment="#devices")
    expect(page.locator("#page-devices")).to_be_visible()
    expect(page.locator(".device-row")).to_have_count(9)
    expect(page.locator(".device-row.unsupported")).to_have_count(0)


def test_devices_page_asks_for_a_filter_when_none_is_selected(settings_page):
    page = settings_page(fragment="#devices")
    page.locator("#filter-active").click()
    page.locator("#filter-inactive").click()
    expect(page.locator(".empty-title")).to_have_text("No filter selected")


def test_unsupported_filter_adds_the_thermostat(settings_page):
    page = settings_page(fragment="#devices")
    page.locator("#filter-unsupported").click()
    expect(page.locator(".device-row")).to_have_count(10)
    expect(page.locator(".device-row.unsupported")).to_have_count(1)


def test_search_narrows_the_list(settings_page):
    page = settings_page(fragment="#devices")
    page.locator("#device-search").fill("lamp")
    expect(page.locator(".device-row")).to_have_count(3)
    page.locator("#device-search").fill("nothing matches this")
    expect(page.locator(".empty-title")).to_have_text("No devices found")


def test_exposing_a_device_is_saved_in_the_backend(settings_page, backend):
    page = settings_page(fragment="#devices")
    page.get_by_role("switch", name="Wall socket").click()
    expect(page.locator("#toast")).to_have_text("Saved")
    sync = backend.app.container.device_sync_service
    assert sync.exposed_accessory_count == 1
    expect(page.locator("#device-summary")).to_contain_text("1 of")


def test_unsupported_devices_cannot_be_switched_on(settings_page):
    page = settings_page(fragment="#devices")
    page.locator("#filter-unsupported").click()
    switch = page.get_by_role("switch", name="Radiator thermostat")
    expect(switch).to_have_attribute("aria-disabled", "true")
    switch.click(force=True)
    expect(switch).to_have_attribute("aria-checked", "false")


def test_bridge_name_can_be_changed_and_restored(settings_page, backend):
    page = settings_page(fragment="#name")
    page.locator("#bridge-name-input").fill("Hall bridge")
    page.locator("#bridge-name-save").click()
    expect(page.locator("#toast")).to_have_text("Saved")
    assert (
        backend.app.container.pairing_service.build_pairing_info()["name"]
        == "Hall bridge"
    )
    page.locator("#bridge-name-restore").click()
    expect(page.locator("#bridge-name-input")).to_have_value("Test Homey")


def test_bridge_name_that_is_too_long_shows_an_error(settings_page):
    page = settings_page(fragment="#name")
    page.locator("#bridge-name-input").evaluate(
        "input => input.removeAttribute('maxlength')"
    )
    page.locator("#bridge-name-input").fill("x" * 70)
    page.locator("#bridge-name-save").click()
    expect(page.locator("#toast")).to_have_text("The name can be at most 64 characters")


def test_pincode_can_be_set(settings_page, backend):
    page = settings_page(fragment="#pincode")
    page.locator("#pincode-input").fill("20481357")
    page.locator("#pincode-save").click()
    expect(page.locator("#pincode-current")).to_have_text("204-81-357")
    assert (
        backend.app.container.pairing_service.build_pairing_info()["pincode"]
        == "204-81-357"
    )


def test_simple_pincode_is_rejected(settings_page):
    page = settings_page(fragment="#pincode")
    page.locator("#pincode-input").fill("11111111")
    page.locator("#pincode-save").click()
    expect(page.locator("#toast")).to_contain_text("does not accept this code")


def test_random_pincode_replaces_the_current_one(settings_page):
    page = settings_page(fragment="#pincode")
    before = page.locator("#pincode-current").inner_text()
    page.locator("#pincode-random").click()
    expect(page.locator("#pincode-current")).not_to_have_text(before)


def test_startup_delay_can_be_enabled(settings_page, backend):
    page = settings_page(fragment="#startup")
    page.get_by_role("switch").first.click()
    expect(page.locator("#menu-startup-subtitle")).to_have_text(
        "Waits 10 s after startup"
    )
    page.locator("#startup-delay-seconds").fill("25")
    page.locator("#startup-delay-seconds").blur()
    expect(page.locator("#menu-startup-subtitle")).to_have_text(
        "Waits 25 s after startup"
    )
    stored = backend.app.settings.values
    assert stored["startup_delay_enabled"] is True
    assert stored["startup_delay_seconds"] == 25
