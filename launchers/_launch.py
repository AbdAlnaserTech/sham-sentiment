"""Shared launch helper for command wrappers in launchers/."""

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

if os.getcwd() != ROOT:
    os.chdir(ROOT)


def launch(script_name: str) -> None:
    script_path = os.path.join(ROOT, "scripts", script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(script_path)
    runpy.run_path(script_path, run_name="__main__")


def main_module(script_name: str) -> None:
    launch(script_name)
