# Android/Kivy App Skeleton

This is a lightweight Android app skeleton for the Etsy Photo Pipeline.

## Important limitations

- Android mode intentionally does **not** require `rembg`.
- Android mode intentionally does **not** require OpenCV.
- Use transparent PNG product cutouts.
- The same core pipeline is used with `use_rembg=False`.

## Run during development

From the project root:

```bash
pip install -r requirements_android_app.txt
python apps/android_kivy/main.py
```

## Build APK

Android builds are best done on Linux, WSL, or GitHub Actions.

```bash
cd apps/android_kivy
buildozer android debug
```

The included `buildozer.spec` is a starting point. Android file permissions and storage paths may need adjustment depending on your device and Android version.
