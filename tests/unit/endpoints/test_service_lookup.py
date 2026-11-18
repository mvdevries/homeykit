import types

import pytest
from homeykit.endpoints.service_lookup import get_service_container


def test_given_no_services_when_looked_up_then_it_fails_as_not_ready():
    homey = types.SimpleNamespace(app=types.SimpleNamespace(services=None))

    with pytest.raises(RuntimeError):
        get_service_container(homey)
