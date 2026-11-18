import json
import socket
import time
import types
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from tests.support.app_harness import AppHarness, HomeyAppHarness
from tests.support.fake_homey_api import FakeHomeyApi
from tests.support.fixtures import InMemorySettings
from tests.support.running_app import LOOPBACK_ADDRESS

POLL_INTERVAL_SECONDS = 0.05
DEFAULT_WAIT_SECONDS = 8.0
NO_QUERY = {"query": {}, "params": {}}


def port_is_open(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((LOOPBACK_ADDRESS, port)) == 0


def wait_until(
    condition: Callable[[], bool], timeout: float = DEFAULT_WAIT_SECONDS
) -> None:
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError("The condition was not met in time")
        time.sleep(POLL_INTERVAL_SECONDS)


async def _call_function(function: Callable[[], Any]) -> Any:
    return function()


@dataclass
class ScenarioContext:
    state_directory: Path
    fake_homey_api: FakeHomeyApi = field(default_factory=FakeHomeyApi)
    settings: InMemorySettings = field(default_factory=InMemorySettings)
    harness: AppHarness | None = None
    homey_app_harness: HomeyAppHarness | None = None
    remembered: dict[str, Any] = field(default_factory=dict)
    api_result: Any = None
    api_error: Exception | None = None

    def install_app(self) -> None:
        self.harness = AppHarness(
            self.state_directory,
            settings=self.settings,
            fake_homey_api=self.fake_homey_api,
        )
        self.harness.start()

    def start_app(self) -> None:
        self.call(self.container.bridge_supervisor.start())

    def stop_app(self) -> None:
        self.call(self.container.bridge_supervisor.shutdown())

    def restart_app(self) -> None:
        assert self.harness is not None
        self.harness.stop()
        self.install_app()
        self.start_app()

    def install_homey_app(self) -> None:
        self.homey_app_harness = HomeyAppHarness(
            self.state_directory,
            settings=self.settings,
            fake_homey_api=self.fake_homey_api,
        )
        self.homey_app_harness.start()

    @property
    def running_app(self):
        assert self.harness is not None and self.harness.app is not None
        return self.harness.app

    @property
    def container(self):
        return self.running_app.container

    @property
    def port(self) -> int:
        return self.running_app.port

    @property
    def log(self):
        return self.running_app.log

    @property
    def device_sync_service(self):
        if self.homey_app_harness is not None:
            return self.homey_app_harness.app.services.device_sync_service
        return self.container.device_sync_service

    def call(self, coroutine: Any) -> Any:
        harness = self.harness or self.homey_app_harness
        assert harness is not None
        return harness.call(coroutine)

    def run(self, function: Callable[[], Any]) -> Any:
        return self.call(_call_function(function))

    def pairing_details(self) -> dict[str, Any]:
        return self.run(self.container.pairing_service.build_pairing_info)

    def call_endpoint(
        self, endpoint: Callable[..., Any], body: dict[str, Any] | None = None
    ) -> Any:
        homey = types.SimpleNamespace(
            app=types.SimpleNamespace(services=self.container)
        )
        return self.call(endpoint(homey=homey, body=body or {}, **NO_QUERY))

    def attempt_endpoint(
        self, endpoint: Callable[..., Any], body: dict[str, Any]
    ) -> None:
        self.api_error = None
        try:
            self.api_result = self.call_endpoint(endpoint, body)
        except Exception as error:
            self.api_error = error

    def hap_bridge(self):
        return self.container.pairing_service._bridge_service.running_bridge

    def stop_everything(self) -> None:
        if self.homey_app_harness is not None:
            app = self.homey_app_harness.app
            if app is not None and app.services is not None:
                self.homey_app_harness.call(app.on_uninit())
            self.homey_app_harness.stop()
        if self.harness is not None:
            self.harness.stop()


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "homeykit.application.bridge_supervisor.ADDRESS_RETRY_INTERVAL_SECONDS", 0.05
    )
    scenario_context = ScenarioContext(state_directory=tmp_path)
    yield scenario_context
    scenario_context.stop_everything()


def parse_device_ids(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def parse_value(text: str) -> Any:
    return json.loads(text)
