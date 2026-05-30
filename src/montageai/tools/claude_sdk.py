from __future__ import annotations

from typing import Any

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn, montage_tool_spec


def montage_tool(api_key: str, api_url: str | None = None, **defaults: Any) -> dict[str, Any]:
    client = MontageClient(api_key=api_key, api_url=api_url)
    spec = montage_tool_spec()
    return {
        **spec,
        "_handler": base_generate_fn(client, **defaults),
    }
