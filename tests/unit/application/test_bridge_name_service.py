import pytest
from homeykit.application.bridge_name_service import BridgeNameService
from homeykit.domain.defaults import BRIDGE_DEFAULT_NAME
from homeykit.infrastructure.repositories.bridge_name_repository import (
    BridgeNameRepository,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


@pytest.fixture
def service(settings, gateway, log):
    return BridgeNameService(
        bridge_name_repository=BridgeNameRepository(SettingsAccess(settings)),
        devices_gateway=gateway,
        log=log,
    )


class TestResolveBridgeName:
    async def test_given_nothing_loaded_when_resolved_then_the_fallback_name_is_used(
        self, service
    ):
        name = service.resolve_bridge_name()

        assert name == BRIDGE_DEFAULT_NAME

    async def test_given_the_homey_name_loaded_when_resolved_then_it_is_the_default(
        self, service
    ):
        await service.load_default_name_from_homey()

        name = service.resolve_bridge_name()

        assert name == "Test Homey"

    async def test_given_a_custom_name_when_it_is_cleared_then_the_default_returns(
        self, service
    ):
        await service.load_default_name_from_homey()

        await service.set_custom_bridge_name("  My   bridge ")
        custom = service.resolve_bridge_name()
        await service.set_custom_bridge_name("")

        assert custom == "My bridge"
        assert service.resolve_bridge_name() == "Test Homey"


class TestLoadDefaultNameFromHomey:
    async def test_given_a_failing_homey_when_loaded_then_the_failure_is_logged(
        self, service, fake_homey_api, log
    ):
        fake_homey_api.fail_next_requests_with.append(500)

        await service.load_default_name_from_homey()

        assert service.resolve_bridge_name() == BRIDGE_DEFAULT_NAME
        assert log.contains("Reading the name of Homey failed")
