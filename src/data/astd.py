"""Download and normalize the ASTD Arabic Sentiment Tweets Dataset."""

import argparse
import os
import sys
import urllib.request

import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from language import detect_language  # noqa: E402
from paths import ensure_dirs  # noqa: E402

ASTD_TWEETS_URL = "https://raw.githubusercontent.com/mahmoudnabil/ASTD/master/data/Tweets.txt"

LABEL_MAP = {
    "POS": "positive",
    "NEG": "negative",
    "NEUTRAL": "neutral",
    "NEU": "neutral",
    "OBJ": "neutral",
    "MIX": "neutral",
}


def download_astd_tweets(out_path: str) -> str:
    ensure_dirs(os.path.dirname(out_path))
    urllib.request.urlretrieve(ASTD_TWEETS_URL, out_path)
    return out_path


def parse_astd_file(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            text, raw_label = line.rsplit("\t", 1)
            text = text.strip()
            raw_label = raw_label.strip().upper()
            if not text or raw_label not in LABEL_MAP:
                continue
            rows.append({
                "text": text,
                "sentiment": LABEL_MAP[raw_label],
                "language": detect_language(text),
            })

    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=["text"]).reset_index(drop=True)


def build_astd_dataset(
    tweets_path: str | None = None,
    out_csv: str | None = None,
    max_per_class: int | None = 800,
) -> pd.DataFrame:
    tweets_path = tweets_path or os.path.join(_ROOT, "data", "real", "astd_tweets.txt")
    out_csv = out_csv or os.path.join(_ROOT, "data", "real", "astd_processed.csv")

    if not os.path.exists(tweets_path):
        download_astd_tweets(tweets_path)

    df = parse_astd_file(tweets_path)

    if max_per_class:
        parts = []
        for sentiment in ["positive", "negative", "neutral"]:
            subset = df[df["sentiment"] == sentiment]
            parts.append(subset.sample(n=min(len(subset), max_per_class), random_state=42))
        df = pd.concat(parts, ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)

    ensure_dirs(os.path.dirname(out_csv))
    df.to_csv(out_csv, index=False, encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and process ASTD dataset")
    parser.add_argument("--max-per-class", type=int, default=800)
    parser.add_argument("--out", type=str, default="data/real/astd_processed.csv")
    args = parser.parse_args()

    out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    df = build_astd_dataset(out_csv=out_path, max_per_class=args.max_per_class)
    print(f"Saved {len(df)} rows to {out_path}")
    print(df.groupby(["sentiment", "language"]).size())


if __name__ == "__main__":
    main()
