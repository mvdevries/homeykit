import pytest
from homeykit.infrastructure.repositories.bridge_name_repository import (
    BridgeNameRepository,
)
from homeykit.infrastructure.repositories.setting_keys import BRIDGE_NAME_SETTING_KEY
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


class TestBridgeNameRepository:
    async def test_given_a_saved_name_when_cleared_then_no_custom_name_remains(
        self, settings
    ):
        repository = BridgeNameRepository(SettingsAccess(settings))

        await repository.save_custom_name("Mine")
        saved = repository.read_custom_name()
        await repository.clear_custom_name()

        assert saved == "Mine"
        assert repository.read_custom_name() is None

    @pytest.mark.parametrize(
        "stored", ["", "   ", 5], ids=["empty", "blank", "a number"]
    )
    def test_given_a_blank_or_wrong_type_when_read_then_there_is_no_custom_name(
        self, settings, stored
    ):
        settings.values[BRIDGE_NAME_SETTING_KEY] = stored
        repository = BridgeNameRepository(SettingsAccess(settings))

        name = repository.read_custom_name()

        assert name is None
