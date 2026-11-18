from typing import Any

from homey.homey import Homey

from .endpoint_types import EmptyBody, JsonBody, EndpointParams, EndpointQuery
from .service_lookup import get_service_container


def read_optional_text(body: JsonBody, key: str) -> str | None:
    value = body.get(key)
    return value if isinstance(value, str) else None


async def get_settings(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: EmptyBody
) -> Any:
    settings_service = get_service_container(homey).settings_service
    return await settings_service.build_settings_overview()


async def set_bridge_name(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: JsonBody
) -> Any:
    settings_service = get_service_container(homey).settings_service
    return await settings_service.set_bridge_name(read_optional_text(body, "bridge_name"))


async def set_pincode(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: JsonBody
) -> Any:
    settings_service = get_service_container(homey).settings_service
    return await settings_service.set_pincode(read_optional_text(body, "pincode"))


async def set_startup_delay(
    *, homey: Homey, query: EndpointQuery, params: EndpointParams, body: JsonBody
) -> Any:
    settings_service = get_service_container(homey).settings_service
    return await settings_service.set_startup_delay(
        enabled=bool(body.get("enabled")), seconds=int(body.get("seconds", 0))
    )
