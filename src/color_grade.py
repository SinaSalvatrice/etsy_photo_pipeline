from __future__ import annotations

from PIL import Image, ImageEnhance


def grade_product(img: Image.Image, contrast: float = 1.0, brightness: float = 1.0, sharpness: float = 1.0, saturation: float = 1.0) -> Image.Image:
    out = img.convert("RGBA")
    if brightness != 1.0:
        out = ImageEnhance.Brightness(out).enhance(brightness)
    if contrast != 1.0:
        out = ImageEnhance.Contrast(out).enhance(contrast)
    if saturation != 1.0:
        out = ImageEnhance.Color(out).enhance(saturation)
    if sharpness != 1.0:
        out = ImageEnhance.Sharpness(out).enhance(sharpness)
    return out
