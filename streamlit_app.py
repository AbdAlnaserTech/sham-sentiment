"""
Streamlit Community Cloud entry point.

Deploy settings:
  Main file: streamlit_app.py  (or app/main.py)
"""

from __future__ import annotations

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT, "app")
SRC_DIR = os.path.join(ROOT, "src")

for path in (APP_DIR, SRC_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

_APP_MAIN = os.path.join(APP_DIR, "main.py")
runpy.run_path(_APP_MAIN, run_name="__main__")
