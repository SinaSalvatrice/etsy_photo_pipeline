# Android / Pydroid workflow

This project has a lightweight Android mode.

## Install

In Pydroid 3, install only:

```text
Pillow
```

Or use:

```bash
pip install -r requirements_android.txt
```

## Important Android rule

Use transparent PNG cutouts.

Android mode does not require:

- rembg
- OpenCV
- numpy

Run with `--no-rembg`:

```bash
python make_etsy_set.py --input input/pendant_001 --preset jewelry_dark_pendant --no-rembg --canvas-size 2500
```

For clocks:

```bash
python make_etsy_set.py --input input/clock_001 --preset clock_wall_dark --no-rembg --canvas-size 2500
```

If a product image has no transparency, the script prints a warning. For clean output, remove the background first and save as PNG.

## Recommended Android folder workflow

```text
etsy-photo-pipeline/
  input/pendant_001/front.png
  templates/jewelry/dark_hero_01.jpg
  templates/jewelry/pendant_mockup_01.jpg
  templates/jewelry/pendant_mockup_01.json
  output/
```

## Canvas size

Start with:

```text
2500x2500
```

If your device struggles, use:

```text
2000x2000
```
