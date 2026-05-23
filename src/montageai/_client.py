"""Sync and async HTTP clients for the Montage API."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, cast

import httpx

from montageai._streaming import aiter_sse_events, iter_sse_events
from montageai.errors import MontageApiError, MontageAuthError, MontageRateLimitError
from montageai.types import GenerateRequest, GenerateResult, StreamEvent

DEFAULT_BASE_URL = "https://api.usemontage.ai"
DEFAULT_TIMEOUT = 120.0


class BaseMontageClient:
    def __init__(
        self,
        api_key: str,
        api_url: str | None = None,
        defaults: dict[str, Any] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = (api_url or DEFAULT_BASE_URL).rstrip("/")
        self._defaults = defaults or {}
        self._timeout = timeout
        self._transport = transport

        from montageai.adapters import AdaptersNamespace
        from montageai.artifacts import ArtifactsNamespace
        from montageai.components import ComponentsNamespace

        self.adapters = AdaptersNamespace(self)
        self.artifacts = ArtifactsNamespace(self)
        self.components = ComponentsNamespace(self)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _build_generate_body(self, **kwargs: Any) -> dict[str, Any]:
        merged = {**self._defaults, **{key: value for key, value in kwargs.items() if value is not None}}
        request = GenerateRequest.model_validate(merged)
        return request.model_dump(by_alias=True, exclude_none=True)

    def _handle_error(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return

        body: Any
        try:
            body = response.json()
        except ValueError:
            body = response.text

        message = _extract_error_message(body) or f"Montage API request failed with HTTP {response.status_code}"
        code = _extract_error_code(body)

        if response.status_code == 401:
            raise MontageAuthError(message=message)

        if response.status_code == 429:
            retry_after_raw = response.headers.get("Retry-After")
            retry_after = int(retry_after_raw) if retry_after_raw and retry_after_raw.isdigit() else None
            raise MontageRateLimitError(retry_after=retry_after)

        raise MontageApiError(
            message=message,
            status=response.status_code,
            code=code or "api_error",
            details=body,
        )

    def _sync_transport(self) -> httpx.BaseTransport | None:
        return cast(httpx.BaseTransport | None, self._transport)

    def _async_transport(self) -> httpx.AsyncBaseTransport | None:
        return cast(httpx.AsyncBaseTransport | None, self._transport)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        with httpx.Client(timeout=self._timeout, transport=self._sync_transport()) as http:
            response = http.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(),
                json=json,
                params=_clean_params(params),
            )
        self._handle_error(response)
        if response.status_code == 204:
            return None
        return response.json()

    async def _arequest(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._async_transport()) as http:
            response = await http.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(),
                json=json,
                params=_clean_params(params),
            )
        self._handle_error(response)
        if response.status_code == 204:
            return None
        return response.json()


class MontageClient(BaseMontageClient):
    def generate(self, **kwargs: Any) -> GenerateResult:
        body = self._build_generate_body(**kwargs)
        return GenerateResult.model_validate(self._request("POST", "/v1/generate", json=body))

    async def agenerate(self, **kwargs: Any) -> GenerateResult:
        body = self._build_generate_body(**kwargs)
        return GenerateResult.model_validate(await self._arequest("POST", "/v1/generate", json=body))

    def stream(self, **kwargs: Any) -> Iterator[StreamEvent]:
        body = self._build_generate_body(**kwargs)
        with httpx.Client(timeout=self._timeout, transport=self._sync_transport()) as http:
            with http.stream(
                "POST",
                f"{self._base_url}/v1/generate",
                headers=self._headers(),
                json=body,
            ) as response:
                self._handle_error(response)
                yield from iter_sse_events(response.iter_lines())

    async def astream(self, **kwargs: Any) -> AsyncIterator[StreamEvent]:
        body = self._build_generate_body(**kwargs)
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._async_transport()) as http:
            async with http.stream(
                "POST",
                f"{self._base_url}/v1/generate",
                headers=self._headers(),
                json=body,
            ) as response:
                self._handle_error(response)
                async for event in aiter_sse_events(response.aiter_lines()):
                    yield event


class AsyncMontageClient(BaseMontageClient):
    async def generate(self, **kwargs: Any) -> GenerateResult:
        body = self._build_generate_body(**kwargs)
        return GenerateResult.model_validate(await self._arequest("POST", "/v1/generate", json=body))

    def stream(self, **kwargs: Any) -> AsyncIterator[StreamEvent]:
        return self._stream(**kwargs)

    async def _stream(self, **kwargs: Any) -> AsyncIterator[StreamEvent]:
        body = self._build_generate_body(**kwargs)
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._async_transport()) as http:
            async with http.stream(
                "POST",
                f"{self._base_url}/v1/generate",
                headers=self._headers(),
                json=body,
            ) as response:
                self._handle_error(response)
                async for event in aiter_sse_events(response.aiter_lines()):
                    yield event


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if not params:
        return None
    return {key: value for key, value in params.items() if value is not None}


def _extract_error_message(body: Any) -> str | None:
    if isinstance(body, str):
        return body or None
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            return _string_or_none(error.get("message")) or _string_or_none(error.get("title"))
        return (
            _string_or_none(error)
            or _string_or_none(body.get("message"))
            or _string_or_none(body.get("title"))
        )
    return None


def _extract_error_code(body: Any) -> str | None:
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            return _string_or_none(error.get("code"))
        return _string_or_none(body.get("code"))
    return None


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
