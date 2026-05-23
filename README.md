# montageai

Python SDK for Montage production UI generation.

## Install

```bash
pip install montageai
```

## Sync generation

```python
from montageai import Montage

montage = Montage(api_key="mtg_sk_...")
result = montage.generate(
    prompt="Interactive fundraising pipeline for a startup CFO. Start empty.",
    data_info='{"investors":[]}',
    interactive=True,
    zeroed=True,
)
print(result.html)
```

## Async generation

```python
from montageai import MontageAsync

montage = MontageAsync(api_key="mtg_sk_...")
result = await montage.generate(prompt="Q4 revenue dashboard", data_info="{}")
```

## Streaming

```python
from montageai import MontageAsync

montage = MontageAsync(api_key="mtg_sk_...")
async for event in montage.stream(prompt="Build an ops dashboard", data_info="{}"):
    print(event.type, event.text or event.slot)
```

## Namespaces

```python
artifact = montage.artifacts.get("art_123")
versions = montage.artifacts.versions("art_123")
components = montage.components.list()
adapters = montage.adapters.list()
montage.adapters.configure("supabase", url="https://x.supabase.co", serviceRoleKey="...")
```

## Framework tools

All framework packages are optional extras and imported lazily:

```python
from montageai.tools.openai_sdk import montage_tool

tool = montage_tool(api_key="mtg_sk_...")
```

Available wrappers:

- `montageai.tools.langgraph`
- `montageai.tools.crewai`
- `montageai.tools.pydantic_ai`
- `montageai.tools.google_adk`
- `montageai.tools.llamaindex`
- `montageai.tools.aws_bedrock`
- `montageai.tools.ag2`
- `montageai.tools.claude_sdk`
- `montageai.tools.openai_sdk`
- `montageai.tools.strands`

## Save HTML

```python
from montageai.embed import save_artifact

save_artifact(result.html, "artifact.html")
```

