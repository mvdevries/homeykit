import pytest
from homeykit.infrastructure.repositories.settings_access import SettingsAccess


class TestJsonValues:
    async def test_given_a_value_when_written_and_read_then_it_round_trips(
        self, settings
    ):
        access = SettingsAccess(settings)

        await access.write_json("key", {"b": 1, "a": [1, 2]})

        assert access.read_json("key", None) == {"a": [1, 2], "b": 1}

    def test_given_no_stored_value_when_read_then_the_default_is_returned(
        self, settings
    ):
        access = SettingsAccess(settings)

        value = access.read_json("missing", "fallback")

        assert value == "fallback"

    @pytest.mark.parametrize(
        "stored",
        ["{not json", 12, None],
        ids=["broken json", "a number", "nothing"],
    )
    def test_given_an_unusable_value_when_read_then_the_default_is_returned(
        self, settings, stored
    ):
        settings.values["key"] = stored
        access = SettingsAccess(settings)

        value = access.read_json("key", [])

        assert value == []


class TestTypedValues:
    def test_given_a_text_when_read_as_text_then_it_is_returned(self, settings):
        settings.values["key"] = "hello"

        assert SettingsAccess(settings).read_text("key") == "hello"

    def test_given_a_number_when_read_as_text_then_nothing_is_returned(self, settings):
        settings.values["key"] = 5

        assert SettingsAccess(settings).read_text("key") is None

    @pytest.mark.parametrize(
        ("stored", "expected"),
        [(30, 30), (30.9, 30)],
        ids=["integer", "float is truncated"],
    )
    def test_given_a_number_when_read_as_an_integer_then_it_is_returned(
        self, settings, stored, expected
    ):
        settings.values["key"] = stored

        assert SettingsAccess(settings).read_int("key") == expected

    @pytest.mark.parametrize(
        "stored", [True, "30", None], ids=["boolean", "text", "nothing"]
    )
    def test_given_no_number_when_read_as_an_integer_then_nothing_is_returned(
        self, settings, stored
    ):
        settings.values["key"] = stored

        assert SettingsAccess(settings).read_int("key") is None

    def test_given_stored_flags_when_read_as_booleans_then_they_are_truthy_or_not(
        self, settings
    ):
        settings.values.update({"on": True, "off": None})
        access = SettingsAccess(settings)

        assert (access.read_bool("on"), access.read_bool("off")) == (True, False)

    async def test_given_a_raw_value_when_written_and_removed_then_it_is_gone(
        self, settings
    ):
        access = SettingsAccess(settings)

        await access.write_raw("key", 1)
        assert access.read_raw("key") == 1
        await access.remove("key")

        assert access.read_raw("key") is None
