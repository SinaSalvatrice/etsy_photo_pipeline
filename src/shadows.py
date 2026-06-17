from __future__ import annotations

from PIL import Image, ImageFilter


def make_shadow(product: Image.Image, opacity: float = 0.4, blur: int = 45, offset_x: int = 35, offset_y: int = 65) -> Image.Image:
    """Create a blurred shadow layer based on the product alpha channel."""
    if product.mode != "RGBA":
        product = product.convert("RGBA")
    alpha = product.getchannel("A")
    shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
    shadow_alpha = alpha.point(lambda p: int(p * max(0.0, min(1.0, opacity))))
    shadow.putalpha(shadow_alpha)
    canvas = Image.new("RGBA", (product.width + abs(offset_x) * 2 + blur * 2, product.height + abs(offset_y) * 2 + blur * 2), (0, 0, 0, 0))
    paste_x = abs(offset_x) + blur + offset_x
    paste_y = abs(offset_y) + blur + offset_y
    canvas.alpha_composite(shadow, (paste_x, paste_y))
    return canvas.filter(ImageFilter.GaussianBlur(blur))
