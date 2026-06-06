"""Evaluate models — wrapper + re-exports for tests."""

import importlib.util
import os


def _load_script():
    path = os.path.join(os.path.dirname(__file__), "scripts", "evaluate.py")
    spec = importlib.util.spec_from_file_location("project_evaluate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_script()
evaluate_on_labeled_csv = _module.evaluate_on_labeled_csv


def main() -> None:
    _module.main()


if __name__ == "__main__":
    main()
