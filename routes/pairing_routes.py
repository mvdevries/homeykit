from typing import Any

from homey.homey import Homey

from .route_types import EmptyBody, RouteParams, RouteQuery
from .service_lookup import get_service_container


async def get_pairing(
    *, homey: Homey, query: RouteQuery, params: RouteParams, body: EmptyBody
) -> Any:
    pairing_service = get_service_container(homey).pairing_service
    return pairing_service.build_pairing_info()
