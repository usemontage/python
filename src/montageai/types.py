"""Public Pydantic models for the Montage API contract."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class MontageModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class DesignSystemColors(MontageModel):
    background: str | None = None
    background_subtle: str | None = Field(None, alias="backgroundSubtle")
    surface: str | None = None
    surface_hover: str | None = Field(None, alias="surfaceHover")
    surface_active: str | None = Field(None, alias="surfaceActive")
    primary: str | None = None
    primary_hover: str | None = Field(None, alias="primaryHover")
    primary_subtle: str | None = Field(None, alias="primarySubtle")
    secondary: str | None = None
    secondary_subtle: str | None = Field(None, alias="secondarySubtle")
    text: str | None = None
    text_secondary: str | None = Field(None, alias="textSecondary")
    text_muted: str | None = Field(None, alias="textMuted")
    border: str | None = None
    border_subtle: str | None = Field(None, alias="borderSubtle")
    focus: str | None = None
    success: str | None = None
    warning: str | None = None
    danger: str | None = None
    info: str | None = None


class DesignSystem(MontageModel):
    id: str | None = None
    label: str | None = None
    theme: Literal["light", "dark", "auto"] | None = None
    palette: str | None = None
    colors: DesignSystemColors | dict[str, Any] | None = None
    typography: str | None = None
    density: Literal["compact", "default", "relaxed"] | None = None
    mood: str | None = None


class RenderSurface(MontageModel):
    width: int | None = None
    height: int | None = None
    viewport_width: int | None = Field(None, alias="viewportWidth")
    viewport_height: int | None = Field(None, alias="viewportHeight")
    device_pixel_ratio: float | None = Field(None, alias="devicePixelRatio")


class GenerateRequest(MontageModel):
    prompt: str
    data_info: str = Field("", alias="dataInfo")
    data: Any | None = None
    title: str | None = None
    design_system: DesignSystem | dict[str, Any] | None = Field(None, alias="designSystem")
    render_surface: RenderSurface | dict[str, Any] | None = Field(None, alias="renderSurface")
    backend_type: Literal["fluxUI", "fluxAOT"] = Field("fluxUI", alias="backendType")
    cache: Literal["read-write", "read", "write", "skip", "read-through"] | None = None
    artifact_id: str | None = Field(None, alias="artifactId")
    hosted: bool | None = None
    strict_data: bool | None = Field(None, alias="strictData")
    required_fields: list[str] | None = Field(None, alias="requiredFields")
    required_capabilities: list[str] | None = Field(None, alias="requiredCapabilities")
    interactive: bool | None = None
    zeroed: bool | None = None
    streaming: bool | None = None
    output: Literal["html", "fragment"] | None = None
    request_id: str | None = Field(None, alias="requestId")
    include_html: bool | None = Field(None, alias="includeHtml")


class GenerationDiagnostic(MontageModel):
    code: str
    severity: Literal["error", "warning"]
    phase: str
    message: str
    path: str | None = None
    suggestion: str | None = None


class GenerationResolution(MontageModel):
    kind: str
    path: str | None = None
    duration_ms: int | None = Field(None, alias="durationMs")


class ArtifactParts(MontageModel):
    fragment: str
    styles: str | None = None
    stylesheets: list[str] | None = None
    scripts: list[str] | None = None
    external_scripts: list[str] | None = Field(None, alias="externalScripts")


class GenerateResult(MontageModel):
    id: str
    html: str
    credits_used: int = Field(alias="creditsUsed")
    artifact_id: str | None = Field(None, alias="artifactId")
    version: str | None = None
    html_bundle_ref: str | None = Field(None, alias="htmlBundleRef")
    hosted_url: str | None = Field(None, alias="hostedUrl")
    resolution: GenerationResolution | None = None
    diagnostics: list[GenerationDiagnostic] | None = None
    parts: ArtifactParts | None = None


class StreamEvent(MontageModel):
    type: Literal["shell", "slot", "status", "done", "artifact", "error", "debug"]
    html: str | None = None
    text: str | None = None
    slot: str | None = None
    styles: str | None = None
    style_key: str | None = Field(None, alias="styleKey")
    stylesheets: list[str] | None = None
    id: str | None = None
    credits_used: int | None = Field(None, alias="creditsUsed")
    cache_key: str | None = Field(None, alias="cacheKey")
    artifact_id: str | None = Field(None, alias="artifactId")
    version: str | None = None
    html_bundle_ref: str | None = Field(None, alias="htmlBundleRef")
    hosted_url: str | None = Field(None, alias="hostedUrl")
    resolution: GenerationResolution | None = None
    diagnostics: list[GenerationDiagnostic] | None = None
    parts: ArtifactParts | None = None


class Artifact(MontageModel):
    id: str = Field(validation_alias=AliasChoices("id", "artifactId"))
    html: str | None = None
    prompt: str | None = None
    user_id: str | None = Field(None, alias="userId")
    current_version: str | None = Field(None, alias="currentVersion")
    ir: Any | None = None
    created_at: str | None = Field(None, alias="createdAt")
    updated_at: str | None = Field(None, alias="updatedAt")
    version: str | None = None


class ArtifactVersion(MontageModel):
    version: str = Field(validation_alias=AliasChoices("version", "versionId"))
    artifact_id: str | None = Field(None, alias="artifactId")
    content_hash: str | None = Field(None, alias="contentHash")
    parent_id: str | None = Field(None, alias="parentId")
    created_at: str | None = Field(None, alias="createdAt")
    created_by_path: str | None = Field(None, alias="createdByPath")
    html: str | None = None
    ir: Any | None = None


class Adapter(MontageModel):
    provider: str
    configured: bool = True
    configured_at: str | None = Field(None, alias="configuredAt")
    keys: list[str] = Field(default_factory=list)


class Component(MontageModel):
    id: str
    name: str
    kind: str | None = None
    type: str | None = None
    description: str | None = None
    props: Any | None = None
    has_example: bool | None = Field(None, alias="hasExample")

    @model_validator(mode="before")
    @classmethod
    def normalize_component(cls, value: Any) -> Any:
        if isinstance(value, dict):
            data = dict(value)
            component_type = data.get("type")
            if "id" not in data and isinstance(component_type, str):
                data["id"] = component_type
            if "name" not in data and isinstance(component_type, str):
                data["name"] = component_type
            return data
        return value
