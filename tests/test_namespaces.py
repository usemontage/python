from __future__ import annotations

from typing import Any

import httpx
import pytest

from montageai._client import MontageClient


def test_artifacts_namespace(mock_transport: Any) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/artifacts/art_1":
            return httpx.Response(200, json={"artifactId": "art_1", "currentVersion": "v1"})
        if request.url.path == "/v1/artifacts":
            return httpx.Response(200, json={"artifacts": [{"artifactId": "art_1"}]})
        return httpx.Response(200, json={"versions": [{"versionId": "v1", "createdAt": "now"}]})

    client = MontageClient(api_key="mtg_test_sk_xxx", transport=mock_transport(handler))
    assert client.artifacts.get("art_1").id == "art_1"
    assert client.artifacts.list(limit=10)[0].id == "art_1"
    assert client.artifacts.versions("art_1")[0].version == "v1"


@pytest.mark.asyncio
async def test_async_artifacts_namespace(mock_transport: Any) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, json={"artifacts": []})),
    )
    assert await client.artifacts.alist() == []


def test_adapters_namespace(mock_transport: Any) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"provider": "openai", "keys": ["apiKey"]}]})
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"success": True})

    client = MontageClient(api_key="mtg_test_sk_xxx", transport=mock_transport(handler))
    assert client.adapters.list()[0].provider == "openai"
    assert client.adapters.configure("openai", apiKey="sk-xxx") is True
    assert client.adapters.remove("openai") is True


def test_components_namespace(mock_transport: Any) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(
            lambda request: httpx.Response(
                200,
                json={"data": [{"type": "chart", "description": "Charts", "hasExample": True}]},
            )
        ),
    )
    components = client.components.list()
    assert components[0].id == "chart"
    assert components[0].has_example is True

