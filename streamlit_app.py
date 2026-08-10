"""
نقطة دخول Streamlit Cloud — يشغّل app/main.py.

في إعدادات Streamlit Cloud استخدم أحد:
  - streamlit_app.py   (موصى به)
  - app/main.py        (يعمل أيضاً بعد إصلاح bootstrap)
"""

from __future__ import annotations

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(ROOT, "app")
SRC = os.path.join(ROOT, "src")

for path in (ROOT, APP, SRC):
    if path not in sys.path:
        sys.path.insert(0, path)

_APP_MAIN = os.path.join(APP, "main.py")
runpy.run_path(_APP_MAIN, run_name="__main__")
