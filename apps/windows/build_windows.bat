@echo off
setlocal
cd /d "%~dp0\..\.."

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements_windows.txt
pip install pyinstaller

pyinstaller ^
  --noconfirm ^
  --name "Etsy Photo Pipeline" ^
  --windowed ^
  --add-data "configs;configs" ^
  --add-data "templates;templates" ^
  --add-data "README.md;." ^
  --add-data "README_ANDROID.md;." ^
  apps\windows\app_pyside.py

echo.
echo Build complete. Check dist\Etsy Photo Pipeline\
pause
