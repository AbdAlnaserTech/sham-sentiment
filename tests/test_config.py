"""اختبارات مسارات المشروع — ProjectPaths و get_project_root."""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from paths import ProjectPaths, get_project_root


def test_project_root_points_to_repo():
    """جذر المشروع يحتوي على مجلدات data و configs."""
    root = get_project_root()
    assert os.path.isdir(os.path.join(root, "data"))
    assert os.path.isdir(os.path.join(root, "configs"))


def test_paths_properties():
    """خصائص ProjectPaths — models و db."""
    paths = ProjectPaths.from_project_root()
    assert paths.models_dir.endswith("models")
    assert paths.db_path.endswith("sentiment_platform.db")
    assert paths.bert_finetuned_dir.endswith("bert_finetuned")
