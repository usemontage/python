from __future__ import annotations

from typing import Any

import httpx
import pytest

from montageai import Montage, MontageAsync
from montageai._client import MontageClient
from montageai.errors import MontageAuthError, MontageRateLimitError
from montageai.types import GenerateResult


def test_generate_sync(mock_transport: Any, generate_response: dict[str, Any]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://api.usemontage.ai/v1/generate"
        assert request.headers["authorization"] == "Bearer mtg_test_sk_xxx"
        return httpx.Response(200, json=generate_response)

    client = MontageClient(api_key="mtg_test_sk_xxx", transport=mock_transport(handler))
    result = client.generate(prompt="Build a dashboard", data_info="")

    assert isinstance(result, GenerateResult)
    assert result.id == "gen_test123"
    assert result.credits_used == 3
    assert "<body>" in result.html


@pytest.mark.asyncio
async def test_generate_async(mock_transport: Any, generate_response: dict[str, Any]) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, json=generate_response)),
    )
    result = await client.agenerate(prompt="Build a dashboard", data_info="")
    assert result.id == "gen_test123"


@pytest.mark.asyncio
async def test_async_client_generate(mock_transport: Any, generate_response: dict[str, Any]) -> None:
    client = MontageAsync(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, json=generate_response)),
    )
    result = await client.generate(prompt="Build a dashboard", data_info="")
    assert result.id == "gen_test123"


def test_auth_error(mock_transport: Any) -> None:
    client = MontageClient(
        api_key="bad_key",
        transport=mock_transport(lambda request: httpx.Response(401, json={"error": "Unauthorized"})),
    )
    with pytest.raises(MontageAuthError):
        client.generate(prompt="test", data_info="")


def test_rate_limit_error(mock_transport: Any) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(
            lambda request: httpx.Response(
                429,
                json={"error": "Rate limited"},
                headers={"Retry-After": "30"},
            )
        ),
    )
    with pytest.raises(MontageRateLimitError) as exc_info:
        client.generate(prompt="test", data_info="")
    assert exc_info.value.retry_after == 30


def test_custom_api_url() -> None:
    client = MontageClient(api_key="mtg_test_sk_xxx", api_url="https://custom.api.example.com")
    assert client._base_url == "https://custom.api.example.com"


def test_default_design_system(mock_transport: Any, generate_response: dict[str, Any]) -> None:
    sent_body: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent_body.update(request.read() and __import__("json").loads(request.content))
        return httpx.Response(200, json=generate_response)

    client = Montage(
        api_key="mtg_test_sk_xxx",
        defaults={"design_system": {"theme": "dark"}},
        transport=mock_transport(handler),
    )
    result = client.generate(prompt="test", data_info="")
    assert result.id == "gen_test123"
    assert sent_body["designSystem"]["theme"] == "dark"

