"""Montage Python SDK - production UI on demand at scale."""

from montageai._client import AsyncMontageClient, MontageClient
from montageai.types import (
    ArtifactParts,
    GenerateRequest,
    GenerateResult,
    GenerationDiagnostic,
    GenerationResolution,
    StreamEvent,
)

__version__ = "0.1.0"

Montage = MontageClient
MontageAsync = AsyncMontageClient

__all__ = [
    "ArtifactParts",
    "AsyncMontageClient",
    "GenerateRequest",
    "GenerateResult",
    "GenerationDiagnostic",
    "GenerationResolution",
    "Montage",
    "MontageAsync",
    "MontageClient",
    "StreamEvent",
    "__version__",
]

