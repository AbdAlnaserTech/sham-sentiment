"""Launch a script from scripts/ folder (project root helper)."""

import os
import runpy
import sys


def launch(script_name: str) -> None:
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(script_path)
    runpy.run_path(script_path, run_name="__main__")


def main_module(script_name: str) -> None:
    launch(script_name)
