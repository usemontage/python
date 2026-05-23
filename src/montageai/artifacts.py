"""Artifacts namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from montageai.types import Artifact, ArtifactVersion

if TYPE_CHECKING:
    from montageai._client import BaseMontageClient


class ArtifactsNamespace:
    def __init__(self, client: BaseMontageClient) -> None:
        self._client = client

    def get(self, artifact_id: str) -> Artifact:
        return Artifact.model_validate(self._client._request("GET", f"/v1/artifacts/{artifact_id}"))

    async def aget(self, artifact_id: str) -> Artifact:
        return Artifact.model_validate(await self._client._arequest("GET", f"/v1/artifacts/{artifact_id}"))

    def list(self, limit: int | None = None, offset: int | None = None) -> List[Artifact]:
        data = self._client._request("GET", "/v1/artifacts", params={"limit": limit, "offset": offset})
        return _parse_artifact_list(data)

    async def alist(self, limit: int | None = None, offset: int | None = None) -> List[Artifact]:
        data = await self._client._arequest("GET", "/v1/artifacts", params={"limit": limit, "offset": offset})
        return _parse_artifact_list(data)

    def versions(self, artifact_id: str, limit: int | None = None) -> List[ArtifactVersion]:
        data = self._client._request(
            "GET",
            f"/v1/artifacts/{artifact_id}/versions",
            params={"limit": limit},
        )
        return _parse_versions(data)

    async def aversions(self, artifact_id: str, limit: int | None = None) -> List[ArtifactVersion]:
        data = await self._client._arequest(
            "GET",
            f"/v1/artifacts/{artifact_id}/versions",
            params={"limit": limit},
        )
        return _parse_versions(data)


def _parse_artifact_list(data: Any) -> list[Artifact]:
    if isinstance(data, dict):
        items = data.get("artifacts") or data.get("data") or []
    else:
        items = data
    return [Artifact.model_validate(item) for item in items]


def _parse_versions(data: Any) -> list[ArtifactVersion]:
    if isinstance(data, dict):
        items = data.get("versions") or data.get("data") or []
    else:
        items = data
    return [ArtifactVersion.model_validate(item) for item in items]
