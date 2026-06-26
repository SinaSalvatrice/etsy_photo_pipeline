from __future__ import annotations

import runpy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
APP_PATH = PROJECT_ROOT / "apps" / "windows" / "app_pyside.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    runpy.run_path(str(APP_PATH), run_name="__main__")
