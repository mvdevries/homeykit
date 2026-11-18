import types

import pytest
from homeykit.endpoints.service_lookup import get_service_container


def test_service_lookup_fails_before_the_app_is_ready():
    homey = types.SimpleNamespace(app=types.SimpleNamespace(services=None))

    with pytest.raises(RuntimeError):
        get_service_container(homey)
