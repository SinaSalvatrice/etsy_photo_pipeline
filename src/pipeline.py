from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import load_config
from .export_set import run_pipeline as run_export_pipeline


def run_pipeline(
    input_dir: Path,
    preset_name: str,
    output_dir: Optional[Path] = None,
    background_override: Optional[Path] = None,
    template_override: Optional[Path] = None,
    canvas_size: Optional[int] = None,
    object_scale: Optional[float] = None,
    rotation_degrees: Optional[float] = None,
    use_rembg: bool = True,
    debug: bool = False,
    overwrite: bool = False,
    export_zip: bool = True,
) -> Path:
    """Reusable pipeline entry point for CLI, Windows GUI, and Android/Kivy GUI."""
    input_dir = Path(input_dir)
    output_base = Path(output_dir) if output_dir else Path("output")

    cfg = dict(load_config(preset_name))

    if background_override:
        cfg["background_template"] = str(Path(background_override))
    if template_override:
        cfg["mockup_templates"] = [str(Path(template_override))]
    if canvas_size:
        cfg["canvas_size"] = int(canvas_size)
    if object_scale is not None:
        cfg["object_scale"] = float(object_scale)
    if rotation_degrees is not None:
        cfg["rotation_degrees"] = float(rotation_degrees)
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
