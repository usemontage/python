from __future__ import annotations

from typing import Any

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn


def montage_tool(api_key: str, api_url: str | None = None, **defaults: Any) -> Any:
    from pydantic_ai import Tool

    client = MontageClient(api_key=api_key, api_url=api_url)
    return Tool(base_generate_fn(client, **defaults), name="montage_generate")
