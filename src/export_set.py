from __future__ import annotations

from pathlib import Path
from typing import Any
import shutil
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
    log_lines = [
        f"preset={preset_name}",
        f"input_dir={input_dir}",
        f"output_dir={out_dir}",
        f"canvas_size={config.get('canvas_size', 3000)}",
        f"use_rembg={not no_rembg}",
        f"overwrite={overwrite}",
        f"export_zip={bool(config.get('export_zip', True))}",
    ]
    if debug:
        debug_dir.mkdir(parents=True, exist_ok=True)
        log_lines.append(f"debug_dir={debug_dir}")

    canvas_size = int(config.get("canvas_size", 3000))
    quality = int(config.get("output_quality", 95))
    dark_fallback = "light" not in preset_name

    cutouts: list[Image.Image] = []
    for i, path in enumerate(images, start=1):
        log_lines.append(f"source_{i:02d}={path}")
        if debug:
            shutil.copy2(path, debug_dir / f"{i:02d}_{path.stem}_original{path.suffix.lower()}")
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
            log_lines.append(f"cutout_{i:02d}={debug_dir / f'{i:02d}_{path.stem}_cutout.png'}")

    bg = prepare_background(config.get("background_template"), canvas_size, dark_fallback=dark_fallback)
    outputs: list[Path] = []

    if config.get("group_mode"):
        group = render_group(bg, cutouts, config)
        if debug:
            group.save(debug_dir / "01_group_final.png")
        p = out_dir / "01_group_shot.jpg"
        save_jpg(group, p, quality=quality)
        outputs.append(p)
        log_lines.append(f"final_01={p}")
    else:
        labels = ["hero_front", "angle_side", "detail_closeup", "secondary_view"]
        for idx, cutout in enumerate(cutouts[:4], start=1):
            rotation = float(config.get("rotation_degrees", 0)) if idx == 1 else 0
            comp = composite_on_background(bg, cutout, config, rotation=rotation)
            label = labels[idx - 1]
            if debug:
                comp.save(debug_dir / f"{idx:02d}_{label}_final.png")
            p = out_dir / f"{idx:02d}_{label}.jpg"
            save_jpg(comp, p, quality=quality)
            outputs.append(p)
            log_lines.append(f"final_{idx:02d}={p}")

        next_idx = len(outputs) + 1
        for template in config.get("mockup_templates", []) or []:
            template_path = Path(template)
            log_lines.append(f"template_{next_idx:02d}={template_path}")
            try:
                preview_path = debug_dir / f"template_preview_{next_idx:02d}.png" if debug else None
                mockup = render_mockup(template_path, cutouts[0], config, debug_preview_path=preview_path)
                if debug:
                    mockup.save(debug_dir / f"{next_idx:02d}_mockup_final.png")
                p = out_dir / f"{next_idx:02d}_mockup.jpg"
                save_jpg(mockup, p, quality=quality)
                outputs.append(p)
                log_lines.append(f"final_{next_idx:02d}={p}")
                if preview_path:
                    log_lines.append(f"template_preview_{next_idx:02d}={preview_path}")
                next_idx += 1
            except FileNotFoundError as exc:
                print(f"WARNING: {exc}")
                log_lines.append(f"warning={exc}")

        if len(outputs) < 6:
            cover = composite_on_background(bg, cutouts[0], config, scale=float(config.get("object_scale", 0.62)) * 0.95)
            if debug:
                cover.save(debug_dir / f"{len(outputs)+1:02d}_square_cover_final.png")
            p = out_dir / f"{len(outputs)+1:02d}_square_cover.jpg"
            save_jpg(cover, p, quality=quality)
            outputs.append(p)
            log_lines.append(f"final_{len(outputs):02d}={p}")

    if config.get("export_zip", True):
        zip_path = _zip_outputs(out_dir, f"{product_name}_etsy_set.zip")
        print(f"ZIP created: {zip_path}")
        log_lines.append(f"zip={zip_path}")

    if debug:
        (debug_dir / "log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Done. Exported {len(outputs)} image(s) to: {out_dir}")
    return out_dir
