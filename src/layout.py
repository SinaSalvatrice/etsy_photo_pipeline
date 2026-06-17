from __future__ import annotations

from typing import Any
from PIL import Image
from .composite import resize_product
from .shadows import make_shadow


def render_group(background: Image.Image, products: list[Image.Image], config: dict[str, Any]) -> Image.Image:
    canvas = background.convert("RGBA").copy()
    if not products:
        return canvas
    canvas_size = canvas.width
    count = len(products)
    if count == 1:
        positions = [(0.5, 0.52)]
    elif count == 2:
        positions = [(0.37, 0.54), (0.63, 0.54)]
    elif count == 3:
        positions = [(0.31, 0.56), (0.5, 0.47), (0.69, 0.56)]
    else:
        positions = [(0.3, 0.4), (0.7, 0.4), (0.35, 0.68), (0.65, 0.68)]
    scale = float(config.get("object_scale", 0.35))
    target = int(canvas_size * scale)
    for product, (pxn, pyn) in zip(products[:4], positions):
        item = resize_product(product, (target, target), rotation=0)
        x = int(canvas_size * pxn - item.width / 2)
        y = int(canvas_size * pyn - item.height / 2)
        shadow = make_shadow(item, opacity=float(config.get("shadow_opacity", 0.4)), blur=int(config.get("shadow_blur", 45)), offset_x=25, offset_y=55)
        sx = x - (shadow.width - item.width) // 2
        sy = y - (shadow.height - item.height) // 2
        canvas.alpha_composite(shadow, (sx, sy))
        canvas.alpha_composite(item, (x, y))
    return canvas
