from montageai.types import (
    Adapter,
    Artifact,
    ArtifactVersion,
    Component,
    DesignSystem,
    DesignSystemColors,
    GenerateRequest,
    GenerateResult,
    GenerationDiagnostic,
    StreamEvent,
)


def test_generate_request_minimal() -> None:
    req = GenerateRequest(prompt="Build a dashboard", data_info="")
    assert req.prompt == "Build a dashboard"
    assert req.backend_type == "fluxUI"
    assert req.cache is None


def test_generate_request_full() -> None:
    req = GenerateRequest(
        prompt="Revenue pipeline",
        data_info='{"deals": []}',
        design_system=DesignSystem(theme="dark"),
        backend_type="fluxAOT",
        cache="read-write",
        interactive=True,
        zeroed=True,
    )
    assert req.interactive is True
    assert isinstance(req.design_system, DesignSystem)
    assert req.design_system.theme == "dark"


def test_generate_result() -> None:
    result = GenerateResult(id="gen_abc", html="<html></html>", credits_used=3)
    assert result.id == "gen_abc"
    assert result.credits_used == 3
    assert result.artifact_id is None


def test_models_normalize_api_shapes() -> None:
    colors = DesignSystemColors(primary="#6161fd", background="#0a0a0a")
    assert colors.primary == "#6161fd"
    assert colors.surface is None
    assert Artifact(artifactId="art_1", currentVersion="v1").id == "art_1"
    assert ArtifactVersion(versionId="v1", createdAt="now").version == "v1"
    assert Adapter(provider="openai").configured is True
    assert Component(type="chart", description="Chart").id == "chart"


def test_stream_event_done() -> None:
    event = StreamEvent(type="done", html="<html></html>", id="gen_abc", credits_used=3)
    assert event.type == "done"
    assert event.html is not None


def test_stream_event_status() -> None:
    event = StreamEvent(type="status", text="Generating...")
    assert event.text == "Generating..."


def test_generation_diagnostic() -> None:
    diag = GenerationDiagnostic(
        code="missing-handler",
        severity="warning",
        phase="interactive-validation",
        message="Handler 'onClick' has no target state",
    )
    assert diag.severity == "warning"

