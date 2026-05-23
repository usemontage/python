"""Save Montage artifacts locally."""

from __future__ import annotations

from pathlib import Path


def save_artifact(html: str, path: str | Path) -> Path:
    out = Path(path)
    out.write_text(html, encoding="utf-8")
    return out

