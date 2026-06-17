from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any


def load_config(preset_name: str) -> dict[str, Any]:
    path = Path("configs") / f"{preset_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Preset not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def apply_cli_overrides(config: dict[str, Any], args: Namespace) -> dict[str, Any]:
    cfg = dict(config)
    if args.background:
        cfg["background_template"] = args.background
    if args.template:
        cfg["mockup_templates"] = args.template
    if args.scale is not None:
        cfg["object_scale"] = args.scale
    if args.rotation is not None:
        cfg["rotation_degrees"] = args.rotation
    if args.canvas_size is not None:
        cfg["canvas_size"] = args.canvas_size
    if args.force_zip:
        cfg["export_zip"] = True
    if args.no_zip:
        cfg["export_zip"] = False
    return cfg
