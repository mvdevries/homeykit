import asyncio
import functools
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from homeykit.gateways.homey_web_api import HomeyWebApiClient
from homeykit.services import address_watchdog as address_watchdog_module
from homeykit.services import bridge_service as bridge_service_module
from homeykit.services import bridge_supervisor as bridge_supervisor_module
from homeykit.services import service_container as service_container_module
from homeykit.services.service_container import (
    ServiceContainer,
    build_service_container,
)

from tests.support.fake_homey_api import FakeHomeyApi, FakeTokenSource
from tests.support.fixtures import InMemorySettings, LogRecorder, find_free_tcp_port

LOOPBACK_ADDRESS = "127.0.0.1"


@dataclass
class RunningApp:
    container: ServiceContainer
    fake_homey_api: FakeHomeyApi
    settings: InMemorySettings
    log: LogRecorder
    port: int
    network_address: list[str | None]


@asynccontextmanager
async def running_app(
    state_directory: Path,
    *,
    settings: InMemorySettings | None = None,
    fake_homey_api: FakeHomeyApi | None = None,
    start_bridge: bool = True,
) -> AsyncIterator[RunningApp]:
    fake_api = fake_homey_api or FakeHomeyApi()
    app_settings = settings or InMemorySettings()
    log = LogRecorder()
    port = find_free_tcp_port()
    network_address: list[str | None] = [LOOPBACK_ADDRESS]
    client_with_fake_transport = functools.partial(
        HomeyWebApiClient, transport=fake_api.build_transport()
    )
    with (
        patch.object(bridge_service_module, "BRIDGE_PORT", port),
        patch.object(
            bridge_service_module,
            "BRIDGE_STATE_FILE_PATH",
            str(state_directory / "homeykit.state"),
        ),
        patch.object(
            bridge_supervisor_module,
            "find_local_ip_address",
            lambda: network_address[0],
        ),
        patch.object(
            address_watchdog_module, "find_local_ip_address", lambda: network_address[0]
        ),
        patch.object(
            service_container_module, "HomeyWebApiClient", client_with_fake_transport
        ),
    ):
        container = build_service_container(
            settings=app_settings, token_source=FakeTokenSource(), log=log
        )
        if start_bridge:
            await container.bridge_supervisor.start()
        try:
            yield RunningApp(
                container, fake_api, app_settings, log, port, network_address
            )
        finally:
            await container.bridge_supervisor.shutdown()
            await container.close_connections()
            await asyncio.sleep(0)
