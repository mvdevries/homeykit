import asyncio
import json
from pathlib import Path

from pytest_bdd import given, parsers, then, when

from tests.integration.steps.scenario_context import parse_device_ids, parse_value
from tests.support.sample_devices import SUPPORTED_DEVICE_IDS

SNAPSHOT_PATH = Path(__file__).parents[1] / "snapshots" / "accessories.json"
HOMEKIT_WRITE_SETTLE_SECONDS = 0.15
CLIENT_NAME = "test-client"


def expose(scenario, device_ids):
    scenario.call(
        scenario.device_sync_service.save_exposed_device_ids_and_synchronize(device_ids)
    )


def find_characteristic(scenario, device_id, name):
    accessory = scenario.hap_bridge()._accessories_by_device_id[device_id]
    for service in accessory.services:
        for characteristic in service.characteristics:
            if characteristic.display_name == name:
                return accessory, characteristic
    raise LookupError(name)


async def write_from_homekit(scenario, device_id, name, value):
    accessory, characteristic = find_characteristic(scenario, device_id, name)
    scenario.hap_bridge()._driver.set_characteristics(
        {
            "characteristics": [
                {
                    "aid": accessory.aid,
                    "iid": characteristic.to_HAP()["iid"],
                    "value": value,
                }
            ]
        },
        CLIENT_NAME,
    )
    await asyncio.sleep(HOMEKIT_WRITE_SETTLE_SECONDS)


def describe_accessories(scenario):
    bridge = scenario.hap_bridge()._bridge
    accessories = [
        accessory.to_HAP()
        for accessory in sorted(bridge.accessories.values(), key=lambda a: a.aid)
        if accessory is not bridge
    ]
    for accessory in accessories:
        for service in accessory["services"]:
            service.pop("linked", None)
    return json.loads(json.dumps(accessories, sort_keys=True))


def writes_for(scenario, device_id):
    return [
        write
        for write in scenario.fake_homey_api.capability_writes
        if write[0] == device_id
    ]


@given(parsers.parse('the devices "{devices}" are exposed'))
@when(parsers.parse('the devices "{devices}" are exposed'))
def the_devices_are_exposed(scenario, devices):
    expose(scenario, parse_device_ids(devices))


@when("all supported devices are exposed")
def all_supported_devices_are_exposed(scenario):
    expose(scenario, sorted(SUPPORTED_DEVICE_IDS))


@when(parsers.parse('"{device_id}" is deleted in Homey'))
def a_device_is_deleted(scenario, device_id):
    scenario.fake_homey_api.remove_device(device_id)


@when(parsers.parse('"{device_id}" is switched off in Homey'))
def a_device_is_switched_off(scenario, device_id):
    scenario.fake_homey_api.set_capability_value(device_id, "onoff", False)


@when("the devices are synchronised")
def the_devices_are_synchronised(scenario):
    scenario.call(scenario.device_sync_service.synchronize_once())


@given("the accessory ids are remembered")
def the_accessory_ids_are_remembered(scenario):
    scenario.remembered["accessory_ids"] = json.loads(
        scenario.settings.values["accessory_ids"]
    )


@given(parsers.parse("Homey fails the next request with status {status:d}"))
def homey_fails_the_next_request(scenario, status):
    scenario.fake_homey_api.fail_next_requests_with.append(status)


@given(parsers.parse("Homey fails the first {count:d} requests with status {status:d}"))
def homey_fails_the_first_requests(scenario, count, status):
    scenario.fake_homey_api.fail_next_requests_with.extend([status] * count)


@given(parsers.parse('the characteristic "{name}" of "{device_id}" is {state}'))
@then(parsers.parse('the characteristic "{name}" of "{device_id}" is {state}'))
def the_characteristic_has_a_state(scenario, name, device_id, state):
    _, characteristic = find_characteristic(scenario, device_id, name)
    assert characteristic.value is (state == "on")


@when(parsers.parse('HomeKit sets "{name}" of "{device_id}" to {value}'))
def homekit_sets_a_characteristic(scenario, name, device_id, value):
    scenario.call(write_from_homekit(scenario, device_id, name, parse_value(value)))


@then(parsers.parse("{count:d} devices are exposed"))
@then(parsers.parse("{count:d} device is exposed"))
def devices_are_exposed(scenario, count):
    assert scenario.device_sync_service.exposed_accessory_count == count


@then("the accessory ids are the same as before")
def the_accessory_ids_are_the_same(scenario):
    current = json.loads(scenario.settings.values["accessory_ids"])
    assert current == scenario.remembered["accessory_ids"]


@then(
    parsers.parse(
        'Homey received the value {value} for "{capability}" of "{device_id}"'
    )
)
def homey_received_a_value(scenario, value, capability, device_id):
    assert (device_id, capability, parse_value(value)) in (
        scenario.fake_homey_api.capability_writes
    )


@then(
    parsers.parse(
        'Homey received for "{device_id}" first "{first}" with "{first_value}" '
        'and then "{second}" with {second_value}'
    )
)
def homey_received_two_writes_in_order(
    scenario, device_id, first, first_value, second, second_value
):
    writes = writes_for(scenario, device_id)
    assert writes[0] == (device_id, first, first_value)
    assert writes[1] == (device_id, second, parse_value(second_value))


@then("the HomeKit description equals the snapshot")
def the_description_equals_the_snapshot(scenario):
    actual = scenario.run(lambda: describe_accessories(scenario))
    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    assert actual == json.loads(SNAPSHOT_PATH.read_text())
