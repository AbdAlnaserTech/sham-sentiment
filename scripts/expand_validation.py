import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from data.build_validation import build_expanded_validation  # noqa: E402


if __name__ == "__main__":
    path = build_expanded_validation(_ROOT)
    import pandas as pd

    df = pd.read_csv(path)
    print(f"Expanded validation saved: {path}")
    print(f"Total samples: {len(df)}")
    print(df.groupby(["language", "sentiment"]).size())
