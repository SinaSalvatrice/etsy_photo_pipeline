from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageOps

from .composite import resize_product
from .shadows import make_shadow
from .utils import fallback_background


def load_template_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Template metadata not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_template_image(meta: dict[str, Any], meta_path: Path, canvas_size: int) -> tuple[Image.Image, float, float, tuple[int, int]]:
    raw = Path(meta.get("template_image", ""))
    if not raw.is_absolute():
        # First try relative to repo root, then relative to metadata file.
        img_path = raw if raw.exists() else (meta_path.parent / raw.name)
    else:
        img_path = raw
    if not img_path.exists():
        print(f"WARNING: Template image not found: {img_path}. Using fallback background.")
        return fallback_background(canvas_size, dark=True), 1.0, 1.0, (0, 0)
    img = Image.open(img_path).convert("RGBA")
    crop = meta.get("output_crop") or {"x": 0, "y": 0, "width": img.width, "height": img.height}
    x, y, w, h = int(crop["x"]), int(crop["y"]), int(crop["width"]), int(crop["height"])
    img = img.crop((x, y, x + w, y + h))
    img = img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
    return img, canvas_size / w, canvas_size / h, (x, y)


def render_mockup(template_json: Path, product: Image.Image, base_config: dict[str, Any], debug_preview_path: Path | None = None) -> Image.Image:
    meta = load_template_metadata(template_json)
    canvas_size = int(base_config.get("canvas_size", 3000))
    canvas, sx, sy, crop_origin = _load_template_image(meta, template_json, canvas_size)
    ox, oy = crop_origin

    rotation = float(meta.get("rotation", base_config.get("rotation_degrees", 0)))
    anchor_box = meta.get("anchor_box")
    if anchor_box:
        bx = int((anchor_box["x"] - ox) * sx)
        by = int((anchor_box["y"] - oy) * sy)
        bw = int(anchor_box["width"] * sx)
        bh = int(anchor_box["height"] * sy)
        scale_min = float(meta.get("scale_min", 0.1))
        scale_max = float(meta.get("scale_max", 1.0))
        scale = float(meta.get("default_scale", base_config.get("object_scale", 0.5)))
        # First fit to anchor box, then clamp to a canvas-relative scale range.
        fitted = resize_product(product, (bw, bh), rotation=rotation)
        max_dim = int(canvas_size * min(scale_max, max(scale_min, scale)))
        if max(fitted.size) > max_dim:
            fitted = resize_product(fitted, (max_dim, max_dim), rotation=0)
        px = bx + bw // 2 - fitted.width // 2
        py = by + bh // 2 - fitted.height // 2
    else:
        anchor = meta.get("anchor", {"x": canvas_size // 2, "y": canvas_size // 2})
        ax = int((anchor["x"] - ox) * sx)
        ay = int((anchor["y"] - oy) * sy)
        scale = float(meta.get("default_scale", base_config.get("object_scale", 0.5)))
        target = int(canvas_size * scale)
        fitted = resize_product(product, (target, target), rotation=rotation)
        px = ax - fitted.width // 2
        py = ay - fitted.height // 2

    shadow = make_shadow(
        fitted,
        opacity=float(base_config.get("shadow_opacity", 0.38)),
        blur=int(base_config.get("shadow_blur", 45)),
        offset_x=int(base_config.get("shadow_offset_x", 30)),
        offset_y=int(base_config.get("shadow_offset_y", 55)),
    )
    sxpos = px - (shadow.width - fitted.width) // 2
    sypos = py - (shadow.height - fitted.height) // 2
    canvas.alpha_composite(shadow, (sxpos, sypos))
    canvas.alpha_composite(fitted, (px, py))

    overlay_path = meta.get("overlay_image")
    if overlay_path:
        overlay = Path(overlay_path)
        if overlay.exists():
            over = ImageOps.fit(Image.open(overlay).convert("RGBA"), (canvas_size, canvas_size), method=Image.Resampling.LANCZOS)
            canvas.alpha_composite(over, (0, 0))

    if debug_preview_path:
        preview = canvas.copy()
        d = ImageDraw.Draw(preview)
        if anchor_box:
            d.rectangle((bx, by, bx + bw, by + bh), outline=(255, 0, 0, 255), width=6)
        d.rectangle((px, py, px + fitted.width, py + fitted.height), outline=(0, 255, 0, 255), width=6)
        preview.save(debug_preview_path)

    return canvas
