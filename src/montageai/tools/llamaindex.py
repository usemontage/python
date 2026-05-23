from __future__ import annotations

from typing import Any

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn


def montage_tool(api_key: str, **defaults: Any) -> Any:
    from llama_index.core.tools import FunctionTool

    client = MontageClient(api_key=api_key)
    return FunctionTool.from_defaults(
        fn=base_generate_fn(client, **defaults),
        name="montage_generate",
        description="Generate a production UI artifact from a prompt and data context.",
    )

