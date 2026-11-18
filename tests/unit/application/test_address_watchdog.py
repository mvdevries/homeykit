import asyncio

import pytest
from homeykit.application.address_watchdog import AddressWatchdog


@pytest.fixture
def changes():
    return []


def build_watchdog(current, found, changes, log, interval=0.01):
    async def record(address):
        changes.append(address)

    return AddressWatchdog(
        read_current_address=lambda: current,
        on_address_changed=record,
        find_address=lambda: found,
        log=log,
        interval_seconds=interval,
    )


class TestCheckAddressOnce:
    async def test_given_a_new_address_when_checked_then_the_bridge_is_restarted(
        self, changes, log
    ):
        watchdog = build_watchdog("192.0.2.1", "192.0.2.2", changes, log)

        changed = await watchdog.check_address_once()

        assert changed is True
        assert changes == ["192.0.2.2"]
        assert log.contains("IP address changed")

    @pytest.mark.parametrize(
        ("current", "found"),
        [("192.0.2.1", "192.0.2.1"), ("192.0.2.1", None), (None, "192.0.2.1")],
        ids=["unchanged", "network gone", "not started yet"],
    )
    async def test_given_no_change_or_no_address_when_checked_then_nothing_happens(
        self, changes, log, current, found
    ):
        watchdog = build_watchdog(current, found, changes, log)

        changed = await watchdog.check_address_once()

        assert changed is False
        assert changes == []


class TestStartAndStop:
    async def test_given_a_changed_address_when_running_then_it_is_checked_repeatedly(
        self, changes, log
    ):
        watchdog = build_watchdog("192.0.2.1", "192.0.2.2", changes, log)

        watchdog.start()
        watchdog.start()
        await asyncio.sleep(0.05)
        await watchdog.stop()
        await watchdog.stop()

        assert changes

    async def test_given_a_failing_restart_when_running_then_the_failure_is_logged(
        self, log
    ):
        async def failing(address):
            raise RuntimeError("boom")

        watchdog = AddressWatchdog(
            read_current_address=lambda: "192.0.2.1",
            on_address_changed=failing,
            find_address=lambda: "192.0.2.2",
            log=log,
            interval_seconds=0.01,
        )

        watchdog.start()
        await asyncio.sleep(0.05)
        await watchdog.stop()

        assert log.contains("Checking the IP address failed")
