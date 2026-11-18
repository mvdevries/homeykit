import asyncio
import json
from pathlib import Path

import pytest

from tests.support.fake_homey_api import FakeHomeyApi
from tests.support.running_app import running_app
from tests.support.sample_devices import SUPPORTED_DEVICE_IDS

pytestmark = pytest.mark.integration

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "accessories.json"


def accessory_for(app, device_id):
    bridge = app.container.bridge_supervisor._bridge_service.running_bridge.bridge
    sync = app.container.device_sync_service
    return sync._accessories_by_device_id[device_id], bridge


def characteristic_of(accessory, name):
    for service in accessory.services:
        for characteristic in service.characteristics:
            if characteristic.display_name == name:
                return characteristic
    raise LookupError(name)


async def expose(app, device_ids):
    await app.container.device_sync_service.save_exposed_device_ids_and_synchronize(
        device_ids
    )


async def write_from_homekit(app, accessory, characteristic, value):
    app.container.bridge_supervisor._bridge_service.running_bridge.driver.set_characteristics(
        {
            "characteristics": [
                {
                    "aid": accessory.aid,
                    "iid": characteristic.to_HAP()["iid"],
                    "value": value,
                }
            ]
        },
        "test-client",
    )
    await asyncio.sleep(0.1)


async def test_nothing_is_exposed_by_default(app):
    assert app.container.device_sync_service.exposed_accessory_count == 0


async def test_exposes_all_supported_devices(app):
    await expose(app, list(SUPPORTED_DEVICE_IDS))
    assert app.container.device_sync_service.exposed_accessory_count == 9


async def test_unsupported_devices_are_not_exposed(app):
    await expose(app, ["radiator-thermostat", "wall-socket"])
    assert app.container.device_sync_service.exposed_accessory_count == 1


async def test_removing_a_device_removes_the_accessory(app):
    await expose(app, ["wall-socket", "plain-lamp"])
    await expose(app, ["wall-socket"])
    assert app.container.device_sync_service.exposed_accessory_count == 1
    assert app.log.contains("'Plain lamp' is no longer exposed")


async def test_device_deleted_in_homey_disappears(app):
    await expose(app, ["wall-socket", "plain-lamp"])
    app.fake_homey_api.remove_device("plain-lamp")
    await app.container.device_sync_service.synchronize_once()
    assert app.container.device_sync_service.exposed_accessory_count == 1


async def test_accessory_ids_are_stable_across_restarts(tmp_path):
    async with running_app(tmp_path) as first:
        await expose(first, ["wall-socket", "plain-lamp"])
        first_ids = json.loads(first.settings.values["accessory_ids"])
        settings = first.settings
    async with running_app(tmp_path, settings=settings) as second:
        await second.container.device_sync_service.synchronize_once()
        assert json.loads(second.settings.values["accessory_ids"]) == first_ids


async def test_exposed_devices_are_restored_on_start(tmp_path):
    async with running_app(tmp_path) as first:
        await expose(first, ["wall-socket"])
        settings = first.settings
    async with running_app(tmp_path, settings=settings) as second:
        assert second.container.device_sync_service.exposed_accessory_count == 1


async def test_homey_change_updates_the_characteristic(app):
    await expose(app, ["wall-socket"])
    accessory, _ = accessory_for(app, "wall-socket")
    assert characteristic_of(accessory, "On").value is True
    app.fake_homey_api.set_capability_value("wall-socket", "onoff", False)
    await app.container.device_sync_service.synchronize_once()
    assert characteristic_of(accessory, "On").value is False


async def test_homekit_write_reaches_homey(app):
    await expose(app, ["plain-lamp"])
    accessory, _ = accessory_for(app, "plain-lamp")
    await write_from_homekit(app, accessory, characteristic_of(accessory, "On"), True)
    assert ("plain-lamp", "onoff", True) in app.fake_homey_api.capability_writes


async def test_brightness_is_converted_to_a_fraction(app):
    await expose(app, ["dimmable-lamp"])
    accessory, _ = accessory_for(app, "dimmable-lamp")
    await write_from_homekit(
        app, accessory, characteristic_of(accessory, "Brightness"), 80
    )
    assert ("dimmable-lamp", "dim", 0.8) in app.fake_homey_api.capability_writes


async def test_color_temperature_switches_light_mode_first(app):
    await expose(app, ["tunable-lamp"])
    accessory, _ = accessory_for(app, "tunable-lamp")
    await write_from_homekit(
        app, accessory, characteristic_of(accessory, "ColorTemperature"), 320
    )
    writes = [w for w in app.fake_homey_api.capability_writes if w[0] == "tunable-lamp"]
    assert writes[0] == ("tunable-lamp", "light_mode", "temperature")
    assert writes[1] == ("tunable-lamp", "light_temperature", 0.5)


async def test_failed_write_is_logged(app):
    await expose(app, ["plain-lamp"])
    accessory, _ = accessory_for(app, "plain-lamp")
    app.fake_homey_api.fail_next_requests_with.append(500)
    await write_from_homekit(app, accessory, characteristic_of(accessory, "On"), True)
    assert app.log.contains("Writing to 'Plain lamp' failed")


async def test_first_sync_failure_does_not_stop_the_bridge(tmp_path):
    fake_api = FakeHomeyApi()
    fake_api.fail_next_requests_with.extend([500, 500])
    async with running_app(tmp_path, fake_homey_api=fake_api) as app:
        assert app.container.pairing_service.build_pairing_info()["available"]
        assert app.log.contains("First device synchronization failed")


def read_hap_description(app):
    bridge = app.container.bridge_supervisor._bridge_service.running_bridge.bridge
    return json.loads(json.dumps(_accessories(bridge)))


def _accessories(bridge):
    return [
        accessory.to_HAP()
        for accessory in sorted(bridge.accessories.values(), key=lambda a: a.aid)
        if accessory is not bridge
    ]


def strip_volatile_fields(accessories):
    for accessory in accessories:
        for service in accessory["services"]:
            service.pop("linked", None)
    return accessories


async def test_hap_description_matches_snapshot(app):
    await expose(app, sorted(SUPPORTED_DEVICE_IDS))
    actual = strip_volatile_fields(read_hap_description(app))
    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.parent.mkdir(exist_ok=True)
        SNAPSHOT_PATH.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    expected = json.loads(SNAPSHOT_PATH.read_text())
    assert json.loads(json.dumps(actual, sort_keys=True)) == expected
