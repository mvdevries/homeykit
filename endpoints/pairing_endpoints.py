from typing import Any

from homey.homey import Homey

from .endpoint_types import EmptyBody, EndpointParams, EndpointQuery
from .service_lookup import get_service_container


async def get_pairing(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: EmptyBody
) -> Any:
    pairing_service = get_service_container(homey).pairing_service
    return pairing_service.build_pairing_info()
