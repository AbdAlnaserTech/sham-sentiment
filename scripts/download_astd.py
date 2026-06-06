"""Download and process ASTD dataset."""

import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from data.astd import build_astd_dataset  # noqa: E402


def main() -> None:
    out = os.path.join(_ROOT, "data", "real", "astd_processed.csv")
    df = build_astd_dataset(out_csv=out, max_per_class=800)
    print(f"Saved {len(df)} rows to {out}")
    print(df["sentiment"].value_counts())


if __name__ == "__main__":
    main()
