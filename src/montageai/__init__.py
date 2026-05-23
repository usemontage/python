"""Montage Python SDK - production UI on demand at scale."""

from montageai._client import AsyncMontageClient, MontageClient

__version__ = "0.1.0"

Montage = MontageClient
MontageAsync = AsyncMontageClient

__all__ = [
    "AsyncMontageClient",
    "Montage",
    "MontageAsync",
    "MontageClient",
    "__version__",
]

