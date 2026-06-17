from __future__ import annotations

import json
from argparse import Namespace
from typing import Any

from .app_config import CONFIG_DIR, resolve_user_path


def load_config(preset_name: str) -> dict[str, Any]:
    path = CONFIG_DIR / f"{preset_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Preset not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def apply_cli_overrides(config: dict[str, Any], args: Namespace) -> dict[str, Any]:
    cfg = dict(config)
    if args.background:
        cfg["background_template"] = str(resolve_user_path(args.background))
    if args.template:
        cfg["mockup_templates"] = [str(resolve_user_path(args.template))]
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
