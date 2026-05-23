from __future__ import annotations

from typing import Any

import httpx
import pytest

from montageai import MontageAsync
from montageai._client import MontageClient
from montageai.types import StreamEvent


SSE_BODY = (
    'data: {"type":"status","text":"Generating..."}\n\n'
    'data: {"type":"shell","html":"<html><div id=\\"s1\\"></div></html>"}\n\n'
    'data: {"type":"slot","slot":"s1","html":"<p>Hello</p>"}\n\n'
    'data: {"type":"done","html":"<html><p>Hello</p></html>","id":"gen_abc","creditsUsed":3}\n\n'
)


def test_stream_events_sync(mock_transport: Any) -> None:
    client = MontageClient(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, content=SSE_BODY.encode())),
    )
    events = list(client.stream(prompt="test", data_info=""))
    assert [event.type for event in events] == ["status", "shell", "slot", "done"]
    assert events[2].slot == "s1"
    assert events[3].credits_used == 3


@pytest.mark.asyncio
async def test_stream_events_async(mock_transport: Any) -> None:
    client = MontageAsync(
        api_key="mtg_test_sk_xxx",
        transport=mock_transport(lambda request: httpx.Response(200, content=SSE_BODY.encode())),
    )
    events: list[StreamEvent] = []
    async for event in client.stream(prompt="test", data_info=""):
        events.append(event)
    assert len(events) == 4
    assert events[0].text == "Generating..."
    assert events[-1].type == "done"

