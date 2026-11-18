import types
from pathlib import Path
from unittest.mock import patch

import pytest
from homeykit import api
from homeykit.app import App
from homeykit.domain import errors
from homeykit.domain.errors import SettingsValidationError
from homeykit.endpoints.service_lookup import get_service_container
from homeykit.gateways.homey_web_api import HomeyWebApiClient
from homeykit.services import service_container as service_container_module

from tests.support.fake_homey_api import FakeTokenSource
from tests.support.fixtures import InMemorySettings
from tests.support.running_app import LOOPBACK_ADDRESS, running_app

pytestmark = pytest.mark.integration

NO_QUERY = {"query": {}, "params": {}}


def fake_homey_for(app):
    return types.SimpleNamespace(app=types.SimpleNamespace(services=app.container))


async def call(endpoint, homey, body=None):
    return await endpoint(homey=homey, body=body or {}, **NO_QUERY)


async def test_get_devices_returns_ten_rows(app):
    payload = await call(api.get_devices, fake_homey_for(app))
    assert len(payload["devices"]) == 10
    assert {"id", "name", "zone", "supported", "exposed"} <= set(payload["devices"][0])


async def test_set_exposed_devices_updates_rows_and_bridge(app):
    homey = fake_homey_for(app)
    payload = await call(
        api.set_exposed_devices, homey, {"exposed_device_ids": ["wall-socket"]}
    )
    exposed = [row["id"] for row in payload["devices"] if row["exposed"]]
    assert exposed == ["wall-socket"]
    assert app.container.device_sync_service.exposed_accessory_count == 1


async def test_get_icons(app):
    payload = await call(api.get_icons, fake_homey_for(app))
    assert payload["missing_count"] == 0
    assert payload["icons"]


async def test_get_pairing(app):
    payload = await call(api.get_pairing, fake_homey_for(app))
    assert payload["available"] is True


async def test_settings_round_trip(app):
    homey = fake_homey_for(app)
    await call(api.set_bridge_name, homey, {"bridge_name": "Hall"})
    await call(api.set_pincode, homey, {"pincode": "20481357"})
    overview = await call(
        api.set_startup_delay, homey, {"enabled": True, "seconds": 15}
    )
    assert overview["bridge_name"] == "Hall"
    assert overview["custom_bridge_name"] == "Hall"
    assert overview["pincode"] == "204-81-357"
    assert overview["startup_delay_enabled"] is True
    assert overview["startup_delay_seconds"] == 15
    assert overview["bridge_running"] is True
    assert (await call(api.get_settings, homey)) == overview


async def test_invalid_settings_raise_codes(app):
    homey = fake_homey_for(app)
    with pytest.raises(SettingsValidationError) as error:
        await call(api.set_pincode, homey, {"pincode": "11111111"})
    assert error.value.error_code == errors.PINCODE_TOO_SIMPLE
    with pytest.raises(SettingsValidationError):
        await call(api.set_startup_delay, homey, {"enabled": True, "seconds": 0})
    with pytest.raises(SettingsValidationError):
        await call(api.set_bridge_name, homey, {"bridge_name": "x" * 65})


def test_service_lookup_fails_before_the_app_is_ready():
    homey = types.SimpleNamespace(app=types.SimpleNamespace(services=None))
    with pytest.raises(RuntimeError):
        get_service_container(homey)


async def test_app_lifecycle_migrates_legacy_settings(
    tmp_path: Path, fake_homey_api, monkeypatch
):
    legacy_settings = InMemorySettings(
        {"aangeboden": '["wall-socket"]', "bridge_naam": "Old name"}
    )

    def network():
        return LOOPBACK_ADDRESS

    async with running_app(
        tmp_path, settings=InMemorySettings(), start_bridge=False
    ) as scope:
        port, state = scope.port, tmp_path / "homeykit.state"
    with (
        patch("homeykit.services.bridge_service.BRIDGE_PORT", port),
        patch("homeykit.services.bridge_service.BRIDGE_STATE_FILE_PATH", str(state)),
        patch("homeykit.services.bridge_supervisor.find_local_ip_address", network),
        patch("homeykit.services.address_watchdog.find_local_ip_address", network),
        patch.object(
            service_container_module,
            "HomeyWebApiClient",
            lambda token_source: HomeyWebApiClient(
                token_source, transport=fake_homey_api.build_transport()
            ),
        ),
    ):
        app = App()
        app.homey = types.SimpleNamespace(
            settings=legacy_settings, api=FakeTokenSource()
        )
        app.log = lambda *args: None
        await app.on_init()
        assert "aangeboden" not in legacy_settings.values
        assert legacy_settings.values["bridge_name"] == "Old name"
        assert app.services.device_sync_service.exposed_accessory_count == 1
        await app.on_uninit()
        assert app.services is None
        await app.on_uninit()
