from typing import cast

from homey.homey import Homey

from ..app import App
from ..container import ServiceContainer


def get_service_container(homey: Homey) -> ServiceContainer:
    services = cast(App, homey.app).services
    if services is None:
        raise RuntimeError("The services are not ready yet")
    return services
