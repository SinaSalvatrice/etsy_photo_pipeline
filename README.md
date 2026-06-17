# Etsy Photo Pipeline

A reproducible, non-generative Etsy product photo pipeline.

It takes your real product images, cuts them out when possible, places them into reusable backgrounds/mockups, applies consistent shadows and grading, and exports an Etsy-ready image set plus ZIP.

## Core idea

Do **not** prompt an AI to recreate the product. The product is preserved as an image layer.

Use this workflow:

```text
real product image -> transparent cutout -> template/mockup -> shadow/grading -> Etsy export set
```

## Install desktop version

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run demo

```bash
python -m src.demo_data
python make_etsy_set.py --input demo/pendant_demo --preset jewelry_dark_pendant --no-rembg --debug
python make_etsy_set.py --input demo/clock_demo --preset clock_wall_dark --no-rembg --debug
```

## Normal workflow

Put reusable templates here:

```text
templates/jewelry/
templates/clocks/
templates/group/
```

Put current product photos here:

```text
input/pendant_001/front.png
input/pendant_001/side.png
input/pendant_001/detail.png
```

Run:

```bash
python make_etsy_set.py --input input/pendant_001 --preset jewelry_dark_pendant
```

For already transparent PNGs:

```bash
python make_etsy_set.py --input input/pendant_001 --preset jewelry_dark_pendant --no-rembg
```

## Presets

Available presets:

- `jewelry_dark_pendant`
- `jewelry_light_ring`
- `clock_wall_dark`
- `clock_wall_light`
- `clock_table_dark`
- `group_shot_dark`

Presets live in `configs/`.

## Add your own mockup template

1. Put the template image into `templates/jewelry/` or `templates/clocks/`.
2. Create metadata:

```bash
python create_template_metadata.py --image templates/jewelry/pendant_neck_mockup_01.jpg --output templates/jewelry/pendant_neck_mockup_01.json --anchor-x 1500 --anchor-y 1420 --box-x 1200 --box-y 1050 --box-width 600 --box-height 900 --preview
```

3. Add the JSON path to the matching config:

```json
"mockup_templates": [
  "templates/jewelry/pendant_neck_mockup_01.json"
]
```

## Folder policy

Commit permanent template files:

```text
templates/
configs/
src/
demo/
```

Do not commit normal working product photos or generated output:

```text
input/
output/
```

Those are ignored by `.gitignore` except `.gitkeep` files.

## Important limitations

- Pure compositing cannot create perfect body-contact realism by itself.
- For mockups, use fixed template images and tune anchor boxes.
- The more transparent and clean your product PNGs are, the better the output.
- On Android, use transparent PNGs and `--no-rembg`.

## Useful commands

```bash
python make_etsy_set.py --input input/clock_001 --preset clock_wall_dark --debug
python make_etsy_set.py --input input/ring_001 --preset jewelry_light_ring --no-rembg --canvas-size 2500
python make_etsy_set.py --input input/group_001 --preset group_shot_dark --no-rembg
```

---

# App Structure: Windows + Android

This repo now has a shared pipeline core plus app frontends.

```text
src/pipeline.py                shared reusable pipeline entry point
make_etsy_set.py               CLI wrapper
apps/windows/app_pyside.py     Windows desktop GUI
apps/windows/build_windows.bat Windows EXE build script
apps/android_kivy/main.py      Android/Kivy app skeleton
apps/android_kivy/buildozer.spec
.github/workflows/build-windows.yml
.github/workflows/build-android.yml
```

## Run Windows GUI from VS Code

```bash
pip install -r requirements_windows.txt
python apps/windows/app_pyside.py
```

In the GUI:

1. Select an input product folder, for example `input/pendant_001`.
2. Select a preset, for example `jewelry_dark_pendant`.
3. Keep `Use rembg` disabled if your product images are already transparent PNGs.
4. Click **Run**.
5. Open the output folder.

## Build Windows EXE

```bash
apps/windows/build_windows.bat
```

Output appears in:

```text
dist/Etsy Photo Pipeline/
```

## Android/Kivy skeleton

Android mode is intentionally lightweight:

- Pillow only
- no rembg
- no OpenCV
- transparent PNG product cutouts recommended

Run desktop preview of the Kivy app:

```bash
pip install -r requirements_android_app.txt
python apps/android_kivy/main.py
```

Build APK on Linux/WSL/GitHub Actions:

```bash
cd apps/android_kivy
buildozer android debug
```

## VS Code tasks

`.vscode/tasks.json` contains starter tasks:

- Run pendant demo
- Run clock demo
- Run Windows GUI

## Recommended workflow

Start with the Windows GUI. Get the pipeline stable there first. Android should stay as a lightweight companion app using transparent PNGs.
