from typing import Any

from ..container import ServiceContainer
from .endpoint import endpoint
from .endpoint_types import JsonBody


@endpoint
async def get_pairing(services: ServiceContainer, body: JsonBody) -> Any:
    return services.pairing_service.build_pairing_info()
