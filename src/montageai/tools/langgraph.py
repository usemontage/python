from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn


class MontageInput(BaseModel):
    prompt: str = Field(description="What to build.")
    data_info: str = Field("", description="JSON data context.")


def montage_tool(api_key: str, api_url: str | None = None, **defaults: Any) -> Any:
    from langchain_core.tools import StructuredTool

    client = MontageClient(api_key=api_key, api_url=api_url)
    fn = base_generate_fn(client, **defaults)
    return StructuredTool.from_function(
        func=fn,
        name="montage_generate",
        description="Generate a production UI artifact from a prompt and data context.",
        args_schema=MontageInput,
    )
