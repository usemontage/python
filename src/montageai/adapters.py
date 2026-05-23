"""Adapter configuration namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from montageai.types import Adapter

if TYPE_CHECKING:
    from montageai._client import BaseMontageClient


class AdaptersNamespace:
    def __init__(self, client: BaseMontageClient) -> None:
        self._client = client

    def list(self) -> List[Adapter]:
        return _parse_adapters(self._client._request("GET", "/v1/adapters"))

    async def alist(self) -> List[Adapter]:
        return _parse_adapters(await self._client._arequest("GET", "/v1/adapters"))

    def configure(self, provider: str, **config: str) -> bool:
        data = self._client._request("PUT", f"/v1/adapters/{provider}", json=config)
        return _success(data)

    async def aconfigure(self, provider: str, **config: str) -> bool:
        data = await self._client._arequest("PUT", f"/v1/adapters/{provider}", json=config)
        return _success(data)

    def remove(self, provider: str) -> bool:
        data = self._client._request("DELETE", f"/v1/adapters/{provider}")
        return True if data is None else _success(data)

    async def aremove(self, provider: str) -> bool:
        data = await self._client._arequest("DELETE", f"/v1/adapters/{provider}")
        return True if data is None else _success(data)


def _parse_adapters(data: Any) -> list[Adapter]:
    if isinstance(data, dict):
        items = data.get("adapters") or data.get("data") or []
    else:
        items = data
    return [Adapter.model_validate(item) for item in items]


def _success(data: Any) -> bool:
    if data is None:
        return True
    return bool(data.get("success", False)) if isinstance(data, dict) else False
