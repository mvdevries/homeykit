from typing import Any

from ..container import ServiceContainer
from .endpoint import endpoint
from .endpoint_types import JsonBody


def read_optional_text(body: JsonBody, key: str) -> str | None:
    value = body.get(key)
    return value if isinstance(value, str) else None


@endpoint
async def get_settings(services: ServiceContainer, body: JsonBody) -> Any:
    return await services.settings_service.build_settings_overview()


@endpoint
async def set_bridge_name(services: ServiceContainer, body: JsonBody) -> Any:
    return await services.settings_service.set_bridge_name(
        read_optional_text(body, "bridge_name")
    )


@endpoint
async def set_pincode(services: ServiceContainer, body: JsonBody) -> Any:
    return await services.settings_service.set_pincode(
        read_optional_text(body, "pincode")
    )


@endpoint
async def set_startup_delay(services: ServiceContainer, body: JsonBody) -> Any:
    return await services.settings_service.set_startup_delay(
        enabled=bool(body.get("enabled")), seconds=int(body.get("seconds", 0))
    )
