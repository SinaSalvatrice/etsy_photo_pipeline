#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create reproducible Etsy product photo sets from real product images and templates.")
    parser.add_argument("--input", required=True, help="Input product folder, e.g. input/pendant_001")
    parser.add_argument("--preset", required=True, help="Preset name without .json, e.g. jewelry_dark_pendant")
    parser.add_argument("--output", default="output", help="Base output folder")
    parser.add_argument("--background", default=None, help="Override background image path")
    parser.add_argument("--template", default=None, help="Override mockup template metadata JSON path")
    parser.add_argument("--scale", type=float, default=None, help="Override object scale")
    parser.add_argument("--rotation", type=float, default=None, help="Override rotation in degrees")
    parser.add_argument("--canvas-size", type=int, default=None, help="Override square canvas size, e.g. 2500")
    parser.add_argument("--zip", dest="force_zip", action="store_true", help="Force ZIP export")
    parser.add_argument("--no-zip", action="store_true", help="Disable ZIP export")
    parser.add_argument("--no-rembg", action="store_true", help="Disable rembg; use transparent PNGs or keep full rectangle")
    parser.add_argument("--debug", action="store_true", help="Export intermediate files and anchor previews")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output/product folder instead of timestamped folder")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_zip = True
    if args.force_zip:
        export_zip = True
    if args.no_zip:
        export_zip = False

    out_dir = run_pipeline(
        input_dir=Path(args.input),
        preset_name=args.preset,
        output_dir=Path(args.output),
        background_override=Path(args.background) if args.background else None,
        template_override=Path(args.template) if args.template else None,
        canvas_size=args.canvas_size,
        object_scale=args.scale,
        rotation_degrees=args.rotation,
        use_rembg=not args.no_rembg,
        debug=args.debug,
        overwrite=args.overwrite,
        export_zip=export_zip,
    )
    print(f"Output folder: {out_dir}")


if __name__ == "__main__":
    main()
