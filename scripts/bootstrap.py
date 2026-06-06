"""Shared path setup for CLI scripts in scripts/."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

if os.getcwd() != ROOT:
    os.chdir(ROOT)
