from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable
from PIL import Image, ImageDraw

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def find_images(folder: Path) -> list[Path]:
    if not folder.exists():
        raise FileNotFoundError(f"Input folder not found: {folder}")
    images = sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS and p.is_file())
    return images


def has_alpha(img: Image.Image) -> bool:
    return img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def make_output_dir(output_base: Path, product_name: str, overwrite: bool = False) -> Path:
    output_base.mkdir(parents=True, exist_ok=True)
    out = output_base / product_name
    if overwrite or not out.exists():
        out.mkdir(parents=True, exist_ok=True)
        return out
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = output_base / f"{product_name}_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    return out


def fallback_background(canvas_size: int, dark: bool = True) -> Image.Image:
    base = (24, 24, 24) if dark else (238, 235, 230)
    img = Image.new("RGB", (canvas_size, canvas_size), base)
    draw = ImageDraw.Draw(img)
    # Subtle vignette / texture-like noise-free gradient.
    for i in range(canvas_size):
        if i % 10 == 0:
            shade = int((i / canvas_size) * (18 if dark else -10))
            color = tuple(max(0, min(255, c + shade)) for c in base)
            draw.line([(0, i), (canvas_size, i)], fill=color)
    return img.convert("RGBA")


def save_jpg(img: Image.Image, path: Path, quality: int = 95) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = img.convert("RGB")
    rgb.save(path, "JPEG", quality=quality, optimize=True)
