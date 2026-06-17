from __future__ import annotations

from pathlib import Path
from typing import Any
import zipfile
from PIL import Image

from .background_remove import remove_background
from .color_grade import grade_product
from .composite import composite_on_background, prepare_background
from .layout import render_group
from .template_engine import render_mockup
from .utils import find_images, make_output_dir, save_jpg


def _zip_outputs(out_dir: Path, zip_name: str) -> Path:
    zip_path = out_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for img in sorted(out_dir.glob("*.jpg")):
            zf.write(img, arcname=img.name)
    return zip_path


def run_pipeline(input_dir: Path, output_base: Path, config: dict[str, Any], preset_name: str,
                 no_rembg: bool = False, debug: bool = False, overwrite: bool = False) -> Path:
    images = find_images(input_dir)
    if not images:
        raise SystemExit(f"No product images found in {input_dir}. Add JPG/PNG/WEBP files first.")

    product_name = input_dir.name
    out_dir = make_output_dir(output_base, product_name, overwrite=overwrite)
    debug_dir = out_dir / "debug"
    if debug:
        debug_dir.mkdir(parents=True, exist_ok=True)

    canvas_size = int(config.get("canvas_size", 3000))
    quality = int(config.get("output_quality", 95))
    dark_fallback = "light" not in preset_name

    cutouts: list[Image.Image] = []
    for i, path in enumerate(images, start=1):
        cutout = remove_background(path, no_rembg=no_rembg)
        cutout = grade_product(
            cutout,
            contrast=float(config.get("contrast", 1.0)),
            brightness=float(config.get("brightness", 1.0)),
            sharpness=float(config.get("sharpness", 1.0)),
            saturation=float(config.get("saturation", 1.0)),
        )
        cutouts.append(cutout)
        if debug:
            cutout.save(debug_dir / f"{i:02d}_{path.stem}_cutout.png")

    bg = prepare_background(config.get("background_template"), canvas_size, dark_fallback=dark_fallback)
    outputs: list[Path] = []

    if config.get("group_mode"):
        group = render_group(bg, cutouts, config)
        p = out_dir / "01_group_shot.jpg"
        save_jpg(group, p, quality=quality)
        outputs.append(p)
    else:
        labels = ["hero_front", "angle_side", "detail_closeup", "secondary_view"]
        for idx, cutout in enumerate(cutouts[:4], start=1):
            rotation = float(config.get("rotation_degrees", 0)) if idx == 1 else 0
            comp = composite_on_background(bg, cutout, config, rotation=rotation)
            label = labels[idx - 1]
            p = out_dir / f"{idx:02d}_{label}.jpg"
            save_jpg(comp, p, quality=quality)
            outputs.append(p)

        next_idx = len(outputs) + 1
        for template in config.get("mockup_templates", []) or []:
            template_path = Path(template)
            try:
                preview_path = debug_dir / f"template_preview_{next_idx:02d}.png" if debug else None
                mockup = render_mockup(template_path, cutouts[0], config, debug_preview_path=preview_path)
                p = out_dir / f"{next_idx:02d}_mockup.jpg"
                save_jpg(mockup, p, quality=quality)
                outputs.append(p)
                next_idx += 1
            except FileNotFoundError as exc:
                print(f"WARNING: {exc}")

        if len(outputs) < 6:
            cover = composite_on_background(bg, cutouts[0], config, scale=float(config.get("object_scale", 0.62)) * 0.95)
            p = out_dir / f"{len(outputs)+1:02d}_square_cover.jpg"
            save_jpg(cover, p, quality=quality)
            outputs.append(p)

    if config.get("export_zip", True):
        zip_path = _zip_outputs(out_dir, f"{product_name}_etsy_set.zip")
        print(f"ZIP created: {zip_path}")

    print(f"Done. Exported {len(outputs)} image(s) to: {out_dir}")
    return out_dir
