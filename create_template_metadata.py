#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser(description="Create template metadata JSON and optional anchor preview.")
    parser.add_argument("--image", required=True, help="Template/mockup image path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--anchor-x", type=int, required=True)
    parser.add_argument("--anchor-y", type=int, required=True)
    parser.add_argument("--box-x", type=int, default=None)
    parser.add_argument("--box-y", type=int, default=None)
    parser.add_argument("--box-width", type=int, default=None)
    parser.add_argument("--box-height", type=int, default=None)
    parser.add_argument("--scale", type=float, default=0.42)
    parser.add_argument("--rotation", type=float, default=0)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    image_path = Path(args.image)
    out_path = Path(args.output)
    if not image_path.exists():
        raise SystemExit(f"Template image not found: {image_path}")

    img = Image.open(image_path)
    meta = {
        "template_type": "mockup",
        "template_image": str(image_path).replace("\", "/"),
        "overlay_image": "",
        "foreground_mask": "",
        "anchor": {"x": args.anchor_x, "y": args.anchor_y},
        "default_scale": args.scale,
        "scale_min": max(0.05, args.scale - 0.1),
        "scale_max": min(1.0, args.scale + 0.1),
        "rotation": args.rotation,
        "shadow_profile": "soft_default",
        "output_crop": {"x": 0, "y": 0, "width": img.width, "height": img.height},
    }
    if None not in (args.box_x, args.box_y, args.box_width, args.box_height):
        meta["anchor_box"] = {"x": args.box_x, "y": args.box_y, "width": args.box_width, "height": args.box_height}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Template metadata saved: {out_path}")

    if args.preview:
        preview = img.convert("RGBA")
        d = ImageDraw.Draw(preview)
        d.ellipse((args.anchor_x - 20, args.anchor_y - 20, args.anchor_x + 20, args.anchor_y + 20), outline=(255, 0, 0, 255), width=5)
        if "anchor_box" in meta:
            b = meta["anchor_box"]
            d.rectangle((b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"]), outline=(0, 255, 0, 255), width=5)
        preview_path = out_path.with_suffix(".preview.png")
        preview.save(preview_path)
        print(f"Preview saved: {preview_path}")


if __name__ == "__main__":
    main()
