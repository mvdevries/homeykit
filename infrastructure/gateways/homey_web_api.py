from typing import Any, Protocol

import httpx

from ...domain.defaults import HOMEY_API_TIMEOUT_SECONDS


class TokenSource(Protocol):
    async def get_local_url(self) -> str: ...

    async def get_owner_api_token(self) -> str: ...


class HomeyWebApiClient:
    def __init__(
        self,
        token_source: TokenSource,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token_source = token_source
        self._transport = transport
        self._client: httpx.AsyncClient | None = None

    async def get_json(self, path: str) -> Any:
        response = await self._send_request("GET", path)
        return self._parse_json_or_none(response)

    async def get_text(self, path: str) -> str:
        response = await self._send_request("GET", path)
        return response.text

    async def put_json(self, path: str, body: Any) -> Any:
        response = await self._send_request("PUT", path, body)
        return self._parse_json_or_none(response)

    async def close(self) -> None:
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None

    async def _send_request(
        self, method: str, path: str, body: Any = None
    ) -> httpx.Response:
        response = await self._send_once(method, path, body)
        if response.status_code == 401:
            await self.close()
            response = await self._send_once(method, path, body)
        response.raise_for_status()
        return response

    async def _send_once(self, method: str, path: str, body: Any) -> httpx.Response:
        client = await self._ensure_connected()
        return await client.request(method, path, json=body)

    async def _ensure_connected(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = await self._open_client()
        return self._client

    async def _open_client(self) -> httpx.AsyncClient:
        local_url = (await self._token_source.get_local_url()).rstrip("/")
        token = await self._token_source.get_owner_api_token()
        return httpx.AsyncClient(
            base_url=f"{local_url}/api",
            headers={"Authorization": f"Bearer {token}"},
            timeout=HOMEY_API_TIMEOUT_SECONDS,
            transport=self._transport,
        )

    @staticmethod
    def _parse_json_or_none(response: httpx.Response) -> Any:
        if not response.content:
            return None
        return response.json()
