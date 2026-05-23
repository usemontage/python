from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest


@pytest.fixture()
def generate_response() -> dict[str, Any]:
    return {
        "id": "gen_test123",
        "html": "<html><body>Dashboard</body></html>",
        "creditsUsed": 3,
    }


@pytest.fixture()
def mock_transport() -> Callable[[Callable[[httpx.Request], httpx.Response]], httpx.MockTransport]:
    def build(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
        return httpx.MockTransport(handler)

    return build

