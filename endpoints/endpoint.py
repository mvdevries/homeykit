from collections.abc import Awaitable, Callable
from typing import Any

from homey.homey import Homey

from ..container import ServiceContainer
from .endpoint_types import EndpointParams, EndpointQuery, JsonBody
from .service_lookup import get_service_container

type EndpointHandler = Callable[[ServiceContainer, JsonBody], Awaitable[Any]]
type HomeyEndpoint = Callable[..., Awaitable[Any]]


def endpoint(handler: EndpointHandler) -> HomeyEndpoint:
    async def homey_endpoint(
        *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: JsonBody
    ) -> Any:
        return await handler(get_service_container(homey), body)

    homey_endpoint.__name__ = handler.__name__
    return homey_endpoint
