from __future__ import annotations

from typing import Any

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn


def montage_tool(api_key: str, **defaults: Any) -> Any:
    client = MontageClient(api_key=api_key)
    fn = base_generate_fn(client, **defaults)

    def montage_generate(prompt: str, data_info: str = "") -> str:
        """Generate a production UI artifact from a prompt and data context."""
        return fn(prompt=prompt, data_info=data_info)

    return montage_generate

