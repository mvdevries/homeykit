import pytest
from homeykit.infrastructure.gateways.homey_devices_gateway import HomeyDevicesGateway
from homeykit.infrastructure.gateways.homey_web_api import HomeyWebApiClient


@pytest.fixture
def client(fake_homey_api, token_source):
    return HomeyWebApiClient(token_source, transport=fake_homey_api.build_transport())


@pytest.fixture
def gateway(client):
    return HomeyDevicesGateway(client)
