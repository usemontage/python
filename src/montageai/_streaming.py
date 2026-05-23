"""SSE stream parsing for Montage progressive rendering events."""

from __future__ import annotations

import json
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator

from montageai.types import StreamEvent


def iter_sse_events(lines: Iterable[str]) -> Iterator[StreamEvent]:
    data_lines: list[str] = []
    for line in lines:
        if line == "":
            yield from _flush_event(data_lines)
            data_lines = []
            continue
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    yield from _flush_event(data_lines)


async def aiter_sse_events(lines: AsyncIterable[str]) -> AsyncIterator[StreamEvent]:
    data_lines: list[str] = []
    async for line in lines:
        if line == "":
            for event in _flush_event(data_lines):
                yield event
            data_lines = []
            continue
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    for event in _flush_event(data_lines):
        yield event


def _flush_event(data_lines: list[str]) -> Iterator[StreamEvent]:
    if not data_lines:
        return
    payload = "\n".join(data_lines)
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return
    yield StreamEvent.model_validate(parsed)

