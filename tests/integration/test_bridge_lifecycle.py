import asyncio
import socket

import pytest

from tests.support.running_app import LOOPBACK_ADDRESS, running_app

pytestmark = pytest.mark.integration


def port_is_open(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((LOOPBACK_ADDRESS, port)) == 0


async def wait_until(condition, timeout=5.0):
    deadline = asyncio.get_running_loop().time() + timeout
    while not condition():
        if asyncio.get_running_loop().time() > deadline:
            raise AssertionError("condition was not met in time")
        await asyncio.sleep(0.02)


async def test_bridge_is_published_on_loopback(app):
    running_bridge = app.container.bridge_supervisor
    assert port_is_open(app.port)
    assert running_bridge.current_address() == LOOPBACK_ADDRESS
    assert app.log.contains("published on port")


async def test_bridge_uses_name_of_homey_by_default(app):
    pairing = app.container.pairing_service.build_pairing_info()
    assert pairing["available"] is True
    assert pairing["name"] == "Test Homey"
    assert pairing["paired"] is False


async def test_pairing_info_contains_pincode_and_qr_code(app):
    pairing = app.container.pairing_service.build_pairing_info()
    assert len(pairing["pincode"]) == 10
    assert pairing["qr_svg"].startswith("<svg")


async def test_shutdown_closes_the_port(tmp_path):
    async with running_app(tmp_path) as app:
        port = app.port
        assert port_is_open(port)
    assert not port_is_open(port)


async def test_pincode_survives_a_restart(tmp_path):
    async with running_app(tmp_path) as first:
        pincode = first.container.pairing_service.build_pairing_info()["pincode"]
        settings = first.settings
    async with running_app(tmp_path, settings=settings) as second:
        info = second.container.pairing_service.build_pairing_info()
        assert info["pincode"] == pincode


async def test_start_without_network_address_waits(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "homeykit.services.bridge_supervisor.ADDRESS_RETRY_INTERVAL_SECONDS", 0.05
    )
    async with running_app(tmp_path, start_bridge=False) as app:
        app.network_address[0] = None
        await app.container.bridge_supervisor.start()
        assert app.container.pairing_service.build_pairing_info()["available"] is False
        app.network_address[0] = LOOPBACK_ADDRESS
        await wait_until(lambda: port_is_open(app.port))


async def test_startup_delay_postpones_the_bridge(tmp_path):
    async with running_app(tmp_path, start_bridge=False) as app:
        await app.container.settings_service.set_startup_delay(True, 2)
        await app.container.bridge_supervisor.start()
        pairing = app.container.pairing_service.build_pairing_info()
        assert pairing["available"] is False
        assert 0 < pairing["seconds_until_start"] <= 2
        assert not port_is_open(app.port)
        await wait_until(lambda: port_is_open(app.port), timeout=6)


async def test_shutdown_during_the_delay_cancels_the_start(tmp_path):
    async with running_app(tmp_path, start_bridge=False) as app:
        await app.container.settings_service.set_startup_delay(True, 30)
        await app.container.bridge_supervisor.start()
        await app.container.bridge_supervisor.shutdown()
        assert not port_is_open(app.port)


async def test_address_change_restarts_the_bridge(app):
    watchdog = app.container.address_watchdog
    assert await watchdog.check_address_once() is False
    app.network_address[0] = "0.0.0.0"
    assert await watchdog.check_address_once() is True
    assert app.container.bridge_supervisor.current_address() == "0.0.0.0"
    assert app.log.contains("IP address changed")


async def test_pincode_change_applies_to_the_running_bridge(app):
    await app.container.settings_service.set_pincode("20481357")
    info = app.container.pairing_service.build_pairing_info()
    assert info["pincode"] == "204-81-357"


async def test_bridge_name_change_restarts_the_bridge(app):
    await app.container.settings_service.set_bridge_name("Custom name")
    info = app.container.pairing_service.build_pairing_info()
    assert info["name"] == "Custom name"
    assert port_is_open(app.port)
