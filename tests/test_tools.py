from __future__ import annotations

from typing import Any

import httpx

from montageai._client import MontageClient
from montageai.tools._base import base_generate_fn, montage_tool_spec
from montageai.tools import ag2, aws_bedrock, claude_sdk, crewai, google_adk, langgraph, llamaindex, openai_sdk, pydantic_ai, strands


def test_base_generate_fn_returns_html(mock_transport: Any, generate_response: dict[str, Any]) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, json=generate_response)),
    )
    fn = base_generate_fn(client)
    assert fn("Build") == generate_response["html"]


def test_json_tool_specs_are_available_without_optional_dependencies() -> None:
    spec = montage_tool_spec()
    assert spec["name"] == "montage_generate"
    assert openai_sdk.montage_tool("sk-test")["function"]["name"] == "montage_generate"
    assert claude_sdk.montage_tool("sk-test")["name"] == "montage_generate"


def test_optional_tool_modules_import_without_framework_packages() -> None:
    from montageai import tools

    assert set(tools.__all__) >= {
        "ag2",
        "aws_bedrock",
        "claude_sdk",
        "crewai",
        "google_adk",
        "langgraph",
        "llamaindex",
        "openai_sdk",
        "pydantic_ai",
        "strands",
    }
    assert callable(ag2.montage_tool)
    assert callable(aws_bedrock.montage_tool)
    assert callable(crewai.montage_tool)
    assert callable(google_adk.montage_tool)
    assert callable(langgraph.montage_tool)
    assert callable(llamaindex.montage_tool)
    assert callable(pydantic_ai.montage_tool)
    assert callable(strands.montage_tool)
