from __future__ import annotations

import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT))
PROJECT_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else SOURCE_ROOT
CONFIG_DIR = RESOURCE_ROOT / "configs"
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATE_DIR = RESOURCE_ROOT / "templates"


def resolve_user_path(path: str | Path | None) -> Path | None:
    if path is None:
        return None

    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (PROJECT_ROOT / candidate).resolve()


def resolve_resource_path(path: str | Path | None) -> Path | None:
    if path is None:
        return None

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (RESOURCE_ROOT / candidate).resolve()


def list_presets() -> list[str]:
    if not CONFIG_DIR.exists():
        return []
    return sorted(p.stem for p in CONFIG_DIR.glob("*.json"))
