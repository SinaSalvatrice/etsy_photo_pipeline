from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


def make_dirs() -> None:
    for p in [
        "demo/pendant_demo", "demo/clock_demo", "templates/jewelry", "templates/clocks", "templates/group"
    ]:
        Path(p).mkdir(parents=True, exist_ok=True)


def make_gradient(path: str, dark: bool = True) -> None:
    size = 3000
    base = (22, 22, 24) if dark else (235, 232, 226)
    img = Image.new("RGB", (size, size), base)
    d = ImageDraw.Draw(img)
    for y in range(size):
        if y % 5 == 0:
            shift = int((y / size) * (30 if dark else -18))
            color = tuple(max(0, min(255, c + shift)) for c in base)
            d.line((0, y, size, y), fill=color)
    img.save(path, quality=95)


def make_pendant(path: str) -> None:
    img = Image.new("RGBA", (900, 1500), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((390, 50, 510, 170), outline=(190, 190, 180, 255), width=22)
    pts = [(455, 160), (420, 420), (500, 730), (445, 1040), (500, 1350)]
    d.line(pts, fill=(185, 185, 175, 255), width=70, joint="curve")
    d.line(pts, fill=(110, 110, 105, 190), width=16)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=120))
    img.save(path)


def make_clock(path: str) -> None:
    img = Image.new("RGBA", (1600, 1600), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((120, 120, 1480, 1480), fill=(80, 82, 82, 255), outline=(190, 190, 180, 255), width=20)
    for a in range(12):
        import math
        ang = math.radians(a * 30 - 90)
        x1 = 800 + math.cos(ang) * 560
        y1 = 800 + math.sin(ang) * 560
        x2 = 800 + math.cos(ang) * 640
        y2 = 800 + math.sin(ang) * 640
        d.line((x1, y1, x2, y2), fill=(210, 205, 190, 255), width=16)
    d.line((800, 800, 800, 400), fill=(230, 220, 200, 255), width=18)
    d.line((800, 800, 1100, 800), fill=(230, 220, 200, 255), width=14)
    d.ellipse((760, 760, 840, 840), fill=(40, 40, 40, 255))
    img.save(path)


def make_templates() -> None:
    make_gradient("templates/jewelry/dark_hero_01.jpg", dark=True)
    make_gradient("templates/jewelry/light_ring_hero_01.jpg", dark=False)
    make_gradient("templates/clocks/wall_clock_dark_hero_01.jpg", dark=True)
    make_gradient("templates/clocks/wall_clock_light_hero_01.jpg", dark=False)
    make_gradient("templates/clocks/table_clock_dark_surface_01.jpg", dark=True)
    make_gradient("templates/group/dark_group_01.jpg", dark=True)

    make_gradient("templates/jewelry/pendant_mockup_01.jpg", dark=True)
    meta = {
        "template_type": "mockup", "template_image": "templates/jewelry/pendant_mockup_01.jpg",
        "overlay_image": "", "foreground_mask": "",
        "anchor": {"x": 1500, "y": 1500},
        "anchor_box": {"x": 1200, "y": 850, "width": 600, "height": 1200},
        "default_scale": 0.42, "scale_min": 0.32, "scale_max": 0.52, "rotation": 0,
        "shadow_profile": "soft_necklace", "output_crop": {"x": 0, "y": 0, "width": 3000, "height": 3000}
    }
    Path("templates/jewelry/pendant_mockup_01.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    make_gradient("templates/clocks/wall_clock_dark_room_01.jpg", dark=True)
    meta = {
        "template_type": "mockup", "template_image": "templates/clocks/wall_clock_dark_room_01.jpg",
        "overlay_image": "", "foreground_mask": "",
        "anchor": {"x": 1500, "y": 1350},
        "anchor_box": {"x": 750, "y": 600, "width": 1500, "height": 1500},
        "default_scale": 0.55, "scale_min": 0.45, "scale_max": 0.75, "rotation": 0,
        "shadow_profile": "soft_wall", "output_crop": {"x": 0, "y": 0, "width": 3000, "height": 3000}
    }
    Path("templates/clocks/wall_clock_dark_room_01.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> None:
    make_dirs()
    make_templates()
    make_pendant("demo/pendant_demo/front.png")
    make_clock("demo/clock_demo/front.png")
    print("Demo data created.")


if __name__ == "__main__":
    main()
