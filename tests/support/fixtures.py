import socket
from collections.abc import Iterator
from typing import Any

import pytest

from tests.support.fake_homey_api import FakeHomeyApi, FakeTokenSource


class InMemorySettings:
    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self.values: dict[str, Any] = dict(initial or {})

    def get(self, key: str) -> Any:
        return self.values.get(key)

    async def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    async def unset(self, key: str) -> None:
        self.values.pop(key, None)


class LogRecorder:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, message: str) -> None:
        self.messages.append(message)

    def contains(self, fragment: str) -> bool:
        return any(fragment in message for message in self.messages)


def find_free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
        probe_socket.bind(("127.0.0.1", 0))
        return int(probe_socket.getsockname()[1])


@pytest.fixture
def settings() -> InMemorySettings:
    return InMemorySettings()


@pytest.fixture
def log() -> LogRecorder:
    return LogRecorder()


@pytest.fixture
def fake_homey_api() -> FakeHomeyApi:
    return FakeHomeyApi()


@pytest.fixture
def token_source() -> FakeTokenSource:
    return FakeTokenSource()


@pytest.fixture
def free_port() -> Iterator[int]:
    yield find_free_tcp_port()
