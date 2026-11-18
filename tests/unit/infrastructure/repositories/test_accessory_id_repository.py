from homeykit.infrastructure.repositories.accessory_id_repository import (
    AccessoryIdRepository,
)
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


class TestAccessoryIdRepository:
    async def test_given_new_devices_when_ids_are_assigned_then_reserved_are_skipped(
        self, settings
    ):
        repository = AccessoryIdRepository(SettingsAccess(settings))

        assigned = [
            await repository.get_or_assign_accessory_id(f"device-{index}")
            for index in range(7)
        ]

        assert assigned == [2, 3, 4, 5, 6, 8, 9]

    async def test_given_a_known_device_when_asked_again_then_the_same_id_is_returned(
        self, settings
    ):
        repository = AccessoryIdRepository(SettingsAccess(settings))
        first = await repository.get_or_assign_accessory_id("device")

        second = await repository.get_or_assign_accessory_id("device")

        assert second == first

    async def test_given_a_new_repository_instance_when_asked_then_earlier_ids_are_kept(
        self, settings
    ):
        await AccessoryIdRepository(
            SettingsAccess(settings)
        ).get_or_assign_accessory_id("a")
        repository = AccessoryIdRepository(SettingsAccess(settings))

        id_of_a = await repository.get_or_assign_accessory_id("a")
        id_of_b = await repository.get_or_assign_accessory_id("b")

        assert (id_of_a, id_of_b) == (2, 3)
