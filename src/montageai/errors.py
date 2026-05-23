"""Typed error classes for the Montage SDK."""

from __future__ import annotations

from typing import Any


class MontageApiError(Exception):
    def __init__(
        self,
        message: str = "Montage API error",
        status: int = 500,
        code: str = "unknown",
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details


class MontageAuthError(MontageApiError):
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message=message, status=401, code="unauthorized")


class MontageRateLimitError(MontageApiError):
    def __init__(self, retry_after: int | None = None) -> None:
        super().__init__(
            message="Rate limit exceeded",
            status=429,
            code="rate_limited",
        )
        self.retry_after = retry_after

