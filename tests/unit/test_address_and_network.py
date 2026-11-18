import asyncio
import socket

import pytest
from homeykit.application.address_watchdog import AddressWatchdog
from homeykit.infrastructure import local_address


class FakeSocket:
    def __init__(self, address=None, fail=False):
        self.address = address
        self.fail = fail
        self.closed = False

    def connect(self, target):
        if self.fail:
            raise OSError("unreachable")

    def getsockname(self):
        return (self.address, 12345)

    def close(self):
        self.closed = True


class TestFindLocalIpAddress:
    def test_returns_address_of_the_outgoing_interface(self, monkeypatch):
        fake = FakeSocket("192.0.2.10")
        monkeypatch.setattr(socket, "socket", lambda *args: fake)
        assert local_address.find_local_ip_address() == "192.0.2.10"
        assert fake.closed

    def test_returns_none_without_network(self, monkeypatch):
        fake = FakeSocket(fail=True)
        monkeypatch.setattr(socket, "socket", lambda *args: fake)
        assert local_address.find_local_ip_address() is None
        assert fake.closed


class TestAddressWatchdog:
    @pytest.fixture
    def changes(self):
        return []

    def build(self, current, found, changes, log, interval=0.01):
        async def record(address):
            changes.append(address)

        return AddressWatchdog(
            read_current_address=lambda: current,
            on_address_changed=record,
            log=log,
            interval_seconds=interval,
            find_address=lambda: found,
        )

    async def test_restarts_on_new_address(self, changes, log):
        watchdog = self.build("192.0.2.1", "192.0.2.2", changes, log)
        assert await watchdog.check_address_once() is True
        assert changes == ["192.0.2.2"]
        assert log.contains("IP address changed")

    @pytest.mark.parametrize(
        ("current", "found"),
        [("192.0.2.1", "192.0.2.1"), ("192.0.2.1", None), (None, "192.0.2.1")],
    )
    async def test_does_nothing_when_unchanged_or_unknown(
        self, changes, log, current, found
    ):
        watchdog = self.build(current, found, changes, log)
        assert await watchdog.check_address_once() is False
        assert changes == []

    async def test_loop_checks_periodically_and_stops(self, changes, log):
        watchdog = self.build("192.0.2.1", "192.0.2.2", changes, log)
        watchdog.start()
        watchdog.start()
        await asyncio.sleep(0.05)
        await watchdog.stop()
        await watchdog.stop()
        assert changes

    async def test_loop_survives_errors(self, log):
        async def failing(address):
            raise RuntimeError("boom")

        watchdog = AddressWatchdog(
            read_current_address=lambda: "192.0.2.1",
            on_address_changed=failing,
            log=log,
            interval_seconds=0.01,
            find_address=lambda: "192.0.2.2",
        )
        watchdog.start()
        await asyncio.sleep(0.05)
        await watchdog.stop()
        assert log.contains("Checking the IP address failed")
