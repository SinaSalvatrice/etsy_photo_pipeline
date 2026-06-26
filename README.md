# Etsy Photo Pipeline

A reproducible Etsy product photo pipeline that keeps the real product image as the source of truth.

## Windows / VS Code workflow

1. Open this folder in VS Code.
2. Create and activate a virtual environment in PowerShell.

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install the shared CLI requirements.

```powershell
pip install -r requirements.txt
```

4. Generate demo data.

```powershell
python -m src.demo_data
```

5. Run the pendant demo.

```powershell
python make_etsy_set.py --input demo/pendant_demo --preset jewelry_dark_pendant --no-rembg --debug
```

6. Install the Windows GUI requirements.

```powershell
pip install -r requirements_windows.txt
```

7. Launch the Windows GUI from the project root.

```powershell
python run_windows_gui.py
```

Alternative direct launch from the project root:

```powershell
python apps/windows/app_pyside.py
```

## CLI usage

The CLI is a thin wrapper around the shared core in `src/pipeline.py`.

```powershell
python make_etsy_set.py --input input/pendant_001 --preset jewelry_dark_pendant
python make_etsy_set.py --input input/pendant_001 --preset jewelry_dark_pendant --no-rembg
python make_etsy_set.py --input input/clock_001 --preset clock_wall_dark --debug
```

Optional flags:

- `--output output/custom_runs`
- `--background path\to\background.jpg`
- `--template path\to\template.json`
- `--canvas-size 2500`
- `--no-rembg`
- `--debug`
- `--overwrite`
- `--zip`
- `--no-zip`

Outputs are written under `output/` by default. Each run exports Etsy-ready JPGs and, unless disabled, an `*_etsy_set.zip` archive.

## Windows GUI

The GUI uses the same shared pipeline as the CLI and supports:

- input folder picker
- preset dropdown from `configs/*.json`
- output folder picker
- optional background and template overrides
- canvas size selection
- rembg, debug, overwrite, and ZIP toggles
- worker-thread processing so the window stays responsive

Run it from the project root:

```powershell
python run_windows_gui.py
```

The root launcher keeps the repository root on `sys.path`, so the shared `src` package is importable even if the current shell location is not ideal.

## Debug output

When `--debug` is enabled, the run creates `output/<product>/debug/` with:

- original source images
- cutout PNGs
- final composite previews
- template preview overlays when a mockup template is used
- `log.txt` with the main processing details

## Demo commands

```powershell
python -m src.demo_data
python make_etsy_set.py --input demo/pendant_demo --preset jewelry_dark_pendant --no-rembg --debug
python make_etsy_set.py --input demo/clock_demo --preset clock_wall_dark --no-rembg --debug
```

## Build Windows EXE

Use the batch script from PowerShell or Command Prompt:

```powershell
apps\windows\build_windows.bat
```

The script:

- creates `.venv` if needed
- installs `requirements_windows.txt`
- runs PyInstaller
- bundles `configs/`, `templates/`, `README.md`, and `README_ANDROID.md`
- writes the packaged app to `dist/`

## Project structure

```text
src/pipeline.py                shared reusable pipeline entry point
make_etsy_set.py               CLI wrapper
run_windows_gui.py             Windows GUI root launcher
apps/windows/app_pyside.py     Windows desktop GUI
apps/windows/build_windows.bat Windows EXE build script
apps/android_kivy/main.py      Android/Kivy skeleton
```

## Android note

The Android/Kivy app stays intentionally lightweight for now. Keep using transparent PNG inputs there and treat APK work as a later step.
