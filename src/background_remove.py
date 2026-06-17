from __future__ import annotations

from pathlib import Path
from PIL import Image

from .utils import has_alpha


def remove_background(path: Path, no_rembg: bool = False) -> Image.Image:
    """Return RGBA product image. Uses alpha PNG directly; optionally tries rembg on desktop."""
    img = Image.open(path)
    if has_alpha(img):
        return img.convert("RGBA")

    if no_rembg:
        print(f"WARNING: {path.name} has no transparency. Please use a PNG cutout or run the desktop/rembg version.")
        return img.convert("RGBA")

    try:
        from rembg import remove  # type: ignore
    except Exception as exc:
        print(f"WARNING: rembg is not available ({exc}). Using full rectangular image for {path.name}.")
        print("Tip: install desktop requirements or provide transparent PNGs and use --no-rembg.")
        return img.convert("RGBA")

    try:
        result = remove(img.convert("RGBA"))
        return result.convert("RGBA")
    except Exception as exc:
        print(f"WARNING: rembg failed for {path.name}: {exc}")
        print("Using full rectangular image instead. For clean output, provide a transparent PNG cutout.")
        return img.convert("RGBA")
