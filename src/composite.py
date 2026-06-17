from __future__ import annotations

from pathlib import Path
from typing import Any
from PIL import Image, ImageOps

from .shadows import make_shadow
from .utils import fallback_background


def prepare_background(path: str | Path | None, canvas_size: int, dark_fallback: bool = True) -> Image.Image:
    if path:
        bg_path = Path(path)
        if bg_path.exists():
            img = Image.open(bg_path).convert("RGBA")
            return ImageOps.fit(img, (canvas_size, canvas_size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        print(f"WARNING: Background not found: {bg_path}. Using neutral fallback background.")
    return fallback_background(canvas_size, dark=dark_fallback)


def resize_product(product: Image.Image, target_box: tuple[int, int], rotation: float = 0) -> Image.Image:
    product = product.convert("RGBA")
    if rotation:
        product = product.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
    max_w, max_h = target_box
    ratio = min(max_w / product.width, max_h / product.height)
    new_size = (max(1, int(product.width * ratio)), max(1, int(product.height * ratio)))
    return product.resize(new_size, Image.Resampling.LANCZOS)


def composite_on_background(background: Image.Image, product: Image.Image, config: dict[str, Any], *,
                            scale: float | None = None, position_x: float | None = None,
                            position_y: float | None = None, rotation: float | None = None) -> Image.Image:
    canvas = background.convert("RGBA").copy()
    canvas_size = canvas.width
    scale = float(scale if scale is not None else config.get("object_scale", 0.62))
    position_x = float(position_x if position_x is not None else config.get("position_x", 0.5))
    position_y = float(position_y if position_y is not None else config.get("position_y", 0.5))
    rotation = float(rotation if rotation is not None else config.get("rotation_degrees", 0))

    target = int(canvas_size * scale)
    resized = resize_product(product, (target, target), rotation=rotation)

    x = int(canvas_size * position_x - resized.width / 2)
    y = int(canvas_size * position_y - resized.height / 2)

    shadow = make_shadow(
        resized,
        opacity=float(config.get("shadow_opacity", 0.4)),
        blur=int(config.get("shadow_blur", 45)),
        offset_x=int(config.get("shadow_offset_x", 35)),
        offset_y=int(config.get("shadow_offset_y", 65)),
    )
    sx = x - (shadow.width - resized.width) // 2
    sy = y - (shadow.height - resized.height) // 2
    canvas.alpha_composite(shadow, (sx, sy))
    canvas.alpha_composite(resized, (x, y))
    return canvas
