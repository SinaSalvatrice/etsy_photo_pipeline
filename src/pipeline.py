from __future__ import annotations

from pathlib import Path
from typing import Optional

from .app_config import OUTPUT_DIR, resolve_resource_path, resolve_user_path
from .config import load_config
from .export_set import run_pipeline as run_export_pipeline


def run_pipeline(
    input_dir: Path,
    preset_name: str,
    output_dir: Optional[Path] = None,
    background_override: Optional[Path] = None,
    template_override: Optional[Path] = None,
    canvas_size: Optional[int] = None,
    use_rembg: bool = True,
    debug: bool = False,
    overwrite: bool = False,
    export_zip: bool = True,
) -> Path:
    """Reusable pipeline entry point for CLI, Windows GUI, and Android/Kivy GUI."""
    input_dir = resolve_user_path(input_dir)
    output_base = resolve_user_path(output_dir) if output_dir else OUTPUT_DIR

    cfg = dict(load_config(preset_name))
    background_template = resolve_resource_path(cfg.get("background_template"))
    if background_template:
        cfg["background_template"] = str(background_template)
    mockup_templates = [
        str(resolved)
        for template in cfg.get("mockup_templates", []) or []
        if (resolved := resolve_resource_path(template)) is not None
    ]
    if mockup_templates:
        cfg["mockup_templates"] = mockup_templates

    if background_override:
        cfg["background_template"] = str(resolve_user_path(background_override))
    if template_override:
        cfg["mockup_templates"] = [str(resolve_user_path(template_override))]
    if canvas_size:
        cfg["canvas_size"] = int(canvas_size)
    cfg["export_zip"] = bool(export_zip)

    return run_export_pipeline(
        input_dir=input_dir,
        output_base=output_base,
        config=cfg,
        preset_name=preset_name,
        no_rembg=not use_rembg,
        debug=debug,
        overwrite=overwrite,
    )
