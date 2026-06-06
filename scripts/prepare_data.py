import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from data.merge_datasets import merge_training_and_validation  # noqa: E402

if __name__ == "__main__":
    _, _, stats = merge_training_and_validation(_ROOT)
    print("Done.")
    for key, value in stats.items():
        print(f"  {key}: {value}")
