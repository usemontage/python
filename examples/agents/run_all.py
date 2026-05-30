from __future__ import annotations

import asyncio
import json
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DEMO_HTML = (
    '<!doctype html><html><body><main data-demo="montage-agent" '
    'data-surface="python-sdk"><h1>Agent demo artifact</h1>'
    '<button data-action="refresh">Refresh</button></main></body></html>'
)
SHELL_HTML = (
    '<!doctype html><html><body><main data-demo="montage-agent-shell">'
    '<div data-mtg-stream-slots></div></main></body></html>'
)
SLOT_HTML = (
    '<section data-demo="montage-agent-slot"><h2>Pipeline insight</h2>'
    "<p>Streaming content mounted.</p></section>"
)


@dataclass
class MatrixRow:
    package: str
    surface: str
    result: str


class MockMontageApi:
    def __init__(self) -> None:
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def api_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "MockMontageApi":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    adapters: dict[str, dict[str, Any]] = {}

    def do_POST(self) -> None:
        if self.path != "/v1/generate":
            self._send_json({"error": {"code": "not_found", "message": self.path}}, status=404)
            return
        body = self._read_json()
        if body.get("streaming"):
            self._send_sse()
            return
        self._send_json(generate_payload())

    def do_GET(self) -> None:
        if self.path.startswith("/v1/artifacts/art_demo_1/versions"):
            self._send_json({"versions": [{"version": "v1", "html": DEMO_HTML}]})
            return
        if self.path.startswith("/v1/artifacts/art_demo_1"):
            self._send_json({"id": "art_demo_1", "html": DEMO_HTML, "version": "v1"})
            return
        if self.path.startswith("/v1/artifacts"):
            self._send_json({"artifacts": [{"id": "art_demo_1", "html": DEMO_HTML}]})
            return
        if self.path == "/v1/components":
            self._send_json({"data": [{"id": "table", "name": "Table", "type": "table"}]})
            return
        if self.path == "/v1/adapters":
            self._send_json({"data": list(self.adapters.values())})
            return
        self._send_json({"error": {"code": "not_found", "message": self.path}}, status=404)

    def do_PUT(self) -> None:
        if not self.path.startswith("/v1/adapters/"):
            self._send_json({"error": {"code": "not_found", "message": self.path}}, status=404)
            return
        provider = self.path.rsplit("/", 1)[-1]
        body = self._read_json()
        self.adapters[provider] = {
            "provider": provider,
            "configuredAt": "2026-05-23T00:00:00.000Z",
            "keys": list(body.keys()),
        }
        self._send_json({"success": True})

    def do_DELETE(self) -> None:
        if not self.path.startswith("/v1/adapters/"):
            self._send_json({"error": {"code": "not_found", "message": self.path}}, status=404)
            return
        provider = self.path.rsplit("/", 1)[-1]
        self.adapters.pop(provider, None)
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *_: object) -> None:
        return

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_sse(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        for event in [
            {"type": "status", "text": "Planning dashboard"},
            {"type": "shell", "html": SHELL_HTML},
            {"type": "slot", "slot": "main", "html": SLOT_HTML},
            {
                "type": "done",
                "id": "gen_demo_1",
                "artifactId": "art_demo_1",
                "version": "v1",
                "html": DEMO_HTML,
                "creditsUsed": 0,
            },
        ]:
            self.wfile.write(f"data: {json.dumps(event)}\n\n".encode("utf-8"))
            self.wfile.flush()
            time.sleep(0.01)
        self.close_connection = True


def generate_payload() -> dict[str, Any]:
    return {
        "id": "gen_demo_1",
        "artifactId": "art_demo_1",
        "version": "v1",
        "html": DEMO_HTML,
        "creditsUsed": 0,
    }


def install_framework_stubs() -> None:
    install_crewai_stub()
    install_langchain_stub()
    install_pydantic_ai_stub()
    install_google_adk_stub()
    install_llamaindex_stub()
    install_strands_stub()


def install_crewai_stub() -> None:
    crewai = ModuleType("crewai")
    tools = ModuleType("crewai.tools")

    def tool(name: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
        def decorate(fn: Callable[..., str]) -> Callable[..., str]:
            setattr(fn, "name", name)
            return fn

        return decorate

    tools.tool = tool  # type: ignore[attr-defined]
    sys.modules["crewai"] = crewai
    sys.modules["crewai.tools"] = tools


def install_langchain_stub() -> None:
    langchain_core = ModuleType("langchain_core")
    tools = ModuleType("langchain_core.tools")

    class StructuredTool:
        def __init__(self, func: Callable[..., str], name: str) -> None:
            self.func = func
            self.name = name

        @classmethod
        def from_function(
            cls,
            *,
            func: Callable[..., str],
            name: str,
            description: str,
            args_schema: Any,
        ) -> "StructuredTool":
            _ = (description, args_schema)
            return cls(func, name)

    tools.StructuredTool = StructuredTool  # type: ignore[attr-defined]
    sys.modules["langchain_core"] = langchain_core
    sys.modules["langchain_core.tools"] = tools


def install_pydantic_ai_stub() -> None:
    module = ModuleType("pydantic_ai")

    class Tool:
        def __init__(self, function: Callable[..., str], name: str) -> None:
            self.function = function
            self.name = name

    module.Tool = Tool  # type: ignore[attr-defined]
    sys.modules["pydantic_ai"] = module


def install_google_adk_stub() -> None:
    google = ModuleType("google")
    adk = ModuleType("google.adk")
    tools = ModuleType("google.adk.tools")

    class FunctionTool:
        def __init__(self, fn: Callable[..., str]) -> None:
            self.fn = fn
            self.name = "montage_generate"

    tools.FunctionTool = FunctionTool  # type: ignore[attr-defined]
    sys.modules["google"] = google
    sys.modules["google.adk"] = adk
    sys.modules["google.adk.tools"] = tools


def install_llamaindex_stub() -> None:
    llama_index = ModuleType("llama_index")
    core = ModuleType("llama_index.core")
    tools = ModuleType("llama_index.core.tools")

    class FunctionTool:
        def __init__(self, fn: Callable[..., str], name: str) -> None:
            self.fn = fn
            self.name = name

        @classmethod
        def from_defaults(
            cls,
            *,
            fn: Callable[..., str],
            name: str,
            description: str,
        ) -> "FunctionTool":
            _ = description
            return cls(fn, name)

    tools.FunctionTool = FunctionTool  # type: ignore[attr-defined]
    sys.modules["llama_index"] = llama_index
    sys.modules["llama_index.core"] = core
    sys.modules["llama_index.core.tools"] = tools


def install_strands_stub() -> None:
    strands = ModuleType("strands")
    tools = ModuleType("strands.tools")

    def tool(name: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
        def decorate(fn: Callable[..., str]) -> Callable[..., str]:
            setattr(fn, "name", name)
            return fn

        return decorate

    tools.tool = tool  # type: ignore[attr-defined]
    sys.modules["strands"] = strands
    sys.modules["strands.tools"] = tools


def assert_html(html: str) -> None:
    if 'data-demo="montage-agent"' not in html or "<button" not in html:
        raise AssertionError("HTML did not include the agent demo artifact")


async def record(rows: list[MatrixRow], surface: str, fn: Callable[[], Any]) -> None:
    try:
        result = fn()
        if asyncio.iscoroutine(result):
            result = await result
        rows.append(MatrixRow("montageai", surface, f"PASS {result}"))
    except Exception as exc:  # noqa: BLE001 - proof runner should keep the full matrix.
        rows.append(MatrixRow("montageai", surface, f"FAIL {exc}"))


def invoke_tool(tool: Any) -> str:
    kwargs = {
        "prompt": "Interactive startup pipeline agent workspace",
        "data_info": '{"deals":[]}',
    }
    if isinstance(tool, dict):
        return str(tool["_handler"](**kwargs))
    if callable(tool):
        return str(tool(**kwargs))
    if hasattr(tool, "func"):
        return str(tool.func(**kwargs))
    if hasattr(tool, "fn"):
        return str(tool.fn(**kwargs))
    if hasattr(tool, "function"):
        return str(tool.function(**kwargs))
    raise TypeError(f"Unsupported tool shape: {tool!r}")


def print_matrix(rows: list[MatrixRow]) -> None:
    package_width = max(len("Package"), *(len(row.package) for row in rows))
    surface_width = max(len("Surface"), *(len(row.surface) for row in rows))
    print(f"{'Package'.ljust(package_width)}  {'Surface'.ljust(surface_width)}  Result")
    print(f"{'-' * package_width}  {'-' * surface_width}  ------")
    for row in rows:
        print(f"{row.package.ljust(package_width)}  {row.surface.ljust(surface_width)}  {row.result}")


async def main() -> int:
    install_framework_stubs()

    from montageai import Montage, MontageAsync
    from montageai.tools import (
        ag2,
        aws_bedrock,
        claude_sdk,
        crewai,
        google_adk,
        langgraph,
        llamaindex,
        openai_sdk,
        pydantic_ai,
        strands,
    )

    rows: list[MatrixRow] = []

    with MockMontageApi() as api:
        sync_client = Montage(api_key="mtg_demo_key", api_url=api.api_url)
        async_client = MontageAsync(api_key="mtg_demo_key", api_url=api.api_url)

        await record(rows, "sync generate", lambda: sync_client.generate(prompt="Build", data_info="").id)

        async def async_generate_id() -> str:
            return (await async_client.generate(prompt="Build", data_info="")).id

        await record(rows, "async generate", async_generate_id)

        async def stream_proof() -> str:
            events = []
            async for event in async_client.stream(prompt="Build", data_info="", streaming=True):
                events.append(event.type)
            if events != ["status", "shell", "slot", "done"]:
                raise AssertionError(f"unexpected event order: {events}")
            return "status,shell,slot,done"

        await record(rows, "streaming", stream_proof)

        await record(rows, "artifacts.get", lambda: sync_client.artifacts.get("art_demo_1").id)
        await record(rows, "artifacts.list", lambda: sync_client.artifacts.list()[0].id)
        await record(rows, "artifacts.versions", lambda: sync_client.artifacts.versions("art_demo_1")[0].version)
        await record(rows, "components.list", lambda: sync_client.components.list()[0].id)
        await record(rows, "adapters.configure", lambda: sync_client.adapters.configure("openai", apiKey="sk_demo"))
        await record(rows, "adapters.list", lambda: sync_client.adapters.list()[0].provider)
        await record(rows, "adapters.remove", lambda: sync_client.adapters.remove("openai"))

        wrappers = [
            ("langgraph", langgraph.montage_tool),
            ("crewai", crewai.montage_tool),
            ("pydantic_ai", pydantic_ai.montage_tool),
            ("google_adk", google_adk.montage_tool),
            ("llamaindex", llamaindex.montage_tool),
            ("aws_bedrock", aws_bedrock.montage_tool),
            ("ag2", ag2.montage_tool),
            ("claude_sdk", claude_sdk.montage_tool),
            ("openai_sdk", openai_sdk.montage_tool),
            ("strands", strands.montage_tool),
        ]

        for surface, factory in wrappers:
            await record(
                rows,
                surface,
                lambda factory=factory: _invoke_and_validate(factory("mtg_demo_key", api_url=api.api_url)),
            )

    print_matrix(rows)
    return 1 if any(row.result.startswith("FAIL") for row in rows) else 0


def _invoke_and_validate(tool: Any) -> str:
    html = invoke_tool(tool)
    assert_html(html)
    return "gen_demo_1"


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
