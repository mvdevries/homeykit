from collections.abc import AsyncIterator

import pytest

from tests.support.running_app import RunningApp, running_app


@pytest.fixture
async def app(tmp_path) -> AsyncIterator[RunningApp]:
    async with running_app(tmp_path) as started_app:
        yield started_app
