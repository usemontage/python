"""Shared generate wrapper used by framework integrations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from montageai._client import MontageClient


def base_generate_fn(client: MontageClient, **defaults: Any) -> Callable[..., str]:
    def generate(prompt: str, data_info: str = "", **kwargs: Any) -> str:
        merged = {**defaults, **kwargs}
        result = client.generate(prompt=prompt, data_info=data_info, **merged)
        return result.html

    return generate


def montage_tool_spec() -> dict[str, Any]:
    return {
        "name": "montage_generate",
        "description": "Generate a production UI artifact from a prompt and data context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What to build."},
                "data_info": {
                    "type": "string",
                    "description": "JSON data context.",
                    "default": "",
                },
            },
            "required": ["prompt"],
        },
    }

