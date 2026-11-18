from collections.abc import Iterator

import pytest

from tests.e2e.backend import Backend


@pytest.fixture
def backend(tmp_path) -> Iterator[Backend]:
    running_backend = Backend(tmp_path)
    running_backend.start()
    yield running_backend
    running_backend.stop()


@pytest.fixture
def settings_page(page, backend):
    def open_page(language: str = "en", fragment: str = ""):
        page.goto(f"{backend.base_url}/index.html?lang={language}{fragment}")
        page.wait_for_function("window.homeyReady === true")
        return page

    return open_page
