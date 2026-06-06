import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from paths import ProjectPaths, get_project_root


def test_project_root_points_to_repo():
    root = get_project_root()
    assert os.path.isdir(os.path.join(root, "data"))
    assert os.path.isdir(os.path.join(root, "configs"))


def test_paths_properties():
    paths = ProjectPaths.from_project_root()
    assert paths.model_path.endswith("sentiment_model.pkl")
    assert paths.metadata_path.endswith("model_metadata.json")
