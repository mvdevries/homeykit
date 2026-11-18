import asyncio
import threading
import types
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path
from typing import Any
from unittest.mock import patch

from homeykit import container as service_container_module
from homeykit.app import App
from homeykit.infrastructure.gateways.homey_web_api import HomeyWebApiClient

from tests.support.fake_homey_api import FakeHomeyApi, FakeTokenSource
from tests.support.fixtures import InMemorySettings, find_free_tcp_port
from tests.support.running_app import LOOPBACK_ADDRESS, RunningApp, running_app

STARTUP_TIMEOUT_SECONDS = 20
CALL_TIMEOUT_SECONDS = 30


class BackgroundLoop:
    def __init__(self) -> None:
        self._ready = threading.Event()
        self._stop_event: asyncio.Event | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._error: BaseException | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()
        if not self._ready.wait(timeout=STARTUP_TIMEOUT_SECONDS):
            raise RuntimeError("The background loop did not start in time")
        if self._error is not None:
            raise self._error

    def stop(self) -> None:
        if self._loop is not None and self._stop_event is not None:
            self._loop.call_soon_threadsafe(self._stop_event.set)
        self._thread.join(timeout=STARTUP_TIMEOUT_SECONDS)

    def call(self, coroutine: Any) -> Any:
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result(timeout=CALL_TIMEOUT_SECONDS)

    def lifecycle(self) -> AbstractAsyncContextManager[None]:
        raise NotImplementedError

    def _run(self) -> None:
        asyncio.run(self._main())

    async def _main(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()
        try:
            async with self.lifecycle():
                self._ready.set()
                await self._stop_event.wait()
        except BaseException as error:
            self._error = error
            self._ready.set()


class AppHarness(BackgroundLoop):
    def __init__(
        self,
        state_directory: Path,
        *,
        settings: InMemorySettings,
        fake_homey_api: FakeHomeyApi,
    ) -> None:
        super().__init__()
        self._state_directory = state_directory
        self._settings = settings
        self._fake_homey_api = fake_homey_api
        self.app: RunningApp | None = None

    @asynccontextmanager
    async def lifecycle(self) -> AsyncIterator[None]:
        async with running_app(
            self._state_directory,
            settings=self._settings,
            fake_homey_api=self._fake_homey_api,
            start_bridge=False,
        ) as app:
            self.app = app
            yield


class HomeyAppHarness(BackgroundLoop):
    def __init__(
        self,
        state_directory: Path,
        *,
        settings: InMemorySettings,
        fake_homey_api: FakeHomeyApi,
    ) -> None:
        super().__init__()
        self._state_directory = state_directory
        self._settings = settings
        self._fake_homey_api = fake_homey_api
        self.app: App | None = None

    @asynccontextmanager
    async def lifecycle(self) -> AsyncIterator[None]:
        port = find_free_tcp_port()
        with (
            patch(
                "homeykit.infrastructure.homekit.hap_bridge.BRIDGE_PORT",
                port,
            ),
            patch(
                "homeykit.infrastructure.homekit.hap_bridge.BRIDGE_STATE_FILE_PATH",
                str(self._state_directory / "homeykit.state"),
            ),
            patch("homeykit.container.find_local_ip_address", lambda: LOOPBACK_ADDRESS),
            patch.object(
                service_container_module,
                "HomeyWebApiClient",
                lambda token_source: HomeyWebApiClient(
                    token_source, transport=self._fake_homey_api.build_transport()
                ),
            ),
        ):
            app = App()
            app.homey = types.SimpleNamespace(
                settings=self._settings, api=FakeTokenSource()
            )
            app.log = lambda *args: None
            self.app = app
            yield
