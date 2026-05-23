"""Components listing namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from montageai.types import Component

if TYPE_CHECKING:
    from montageai._client import BaseMontageClient


class ComponentsNamespace:
    def __init__(self, client: BaseMontageClient) -> None:
        self._client = client

    def list(self) -> List[Component]:
        return _parse_components(self._client._request("GET", "/v1/components"))

    async def alist(self) -> List[Component]:
        return _parse_components(await self._client._arequest("GET", "/v1/components"))


def _parse_components(data: Any) -> list[Component]:
    if isinstance(data, dict):
        items = data.get("components") or data.get("data") or []
    else:
        items = data
    return [Component.model_validate(item) for item in items]
