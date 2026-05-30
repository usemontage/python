from __future__ import annotations

from typing import Any

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn


def montage_tool(api_key: str, api_url: str | None = None, **defaults: Any) -> Any:
    from crewai.tools import tool

    client = MontageClient(api_key=api_key, api_url=api_url)
    fn = base_generate_fn(client, **defaults)

    @tool("montage_generate")  # type: ignore[untyped-decorator]
    def generate_ui(prompt: str, data_info: str = "") -> str:
        """Generate a production UI artifact from a prompt and data context."""
        return fn(prompt=prompt, data_info=data_info)

    return generate_ui
