@echo off
setlocal
cd /d "%~dp0\..\.."

if not exist .venv (
  python -m venv .venv
)

set "PYTHON=.venv\Scripts\python.exe"

"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r requirements_windows.txt

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name "Etsy Photo Pipeline" ^
  --windowed ^
  --distpath dist ^
  --workpath build ^
  --add-data "configs;configs" ^
  --add-data "templates;templates" ^
  --add-data "README.md;." ^
  --add-data "README_ANDROID.md;." ^
  apps\windows\app_pyside.py

echo.
echo Build complete. Check dist\Etsy Photo Pipeline\
pause
