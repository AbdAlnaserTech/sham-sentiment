"""
Streamlit Community Cloud entry point.

In deploy settings use either:
  Main file: streamlit_app.py   (this file)
  or:        app/main.py
"""

import bootstrap  # noqa: F401

import runpy
import os

_APP_MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "main.py")
runpy.run_path(_APP_MAIN, run_name="__main__")
