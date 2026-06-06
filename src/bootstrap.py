import os
import sys


def setup_src_path() -> str:
    """Add src/ to sys.path and return project root directory."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    return project_root
