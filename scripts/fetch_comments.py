"""Fetch real comments from YouTube, Google Play, or Reddit and optionally analyze them."""

import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

from data.comment_fetcher import (  # noqa: E402
    FetchDependencyError,
    FetchError,
    comments_to_texts,
    fetch_comments,
    save_fetched_csv,
)
from models.registry import load_predictor  # noqa: E402
from paths import ProjectPaths, ensure_dirs  # noqa: E402


def analyze_fetched(comments, model_kind: str, output: str | None) -> None:
    texts = comments_to_texts(comments)
    if not texts:
        print("No comment text to analyze.")
        return

    predictor = load_predictor(model_kind, root_dir=bootstrap.ROOT)
    results = predictor.predict_batch(texts, auto_language=True)

    import pandas as pd

    rows = []
    for item, meta in zip(results, comments):
        rows.append({
            "text": item.get("text", meta.text),
            "sentiment": item.get("sentiment", ""),
            "confidence": item.get("confidence", 0),
            "language": item.get("language", ""),
            "author": meta.author,
            "source": meta.source,
            "likes": meta.likes,
            "error": item.get("error", ""),
        })
    df = pd.DataFrame(rows)

    paths = ProjectPaths.from_project_root(bootstrap.ROOT)
    ensure_dirs(paths.data_dir)
    out_path = output or os.path.join(paths.data_dir, "fetched_sentiment_results.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Analyzed {len(df)} comments → {out_path}")

    valid = df[df["error"].astype(str) == ""]
    if not valid.empty:
        for label in ("positive", "neutral", "negative"):
            count = int((valid["sentiment"] == label).sum())
            print(f"  {label}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real comments/reviews for sentiment analysis")
    parser.add_argument("url", help="YouTube / Google Play / Reddit URL or app package id")
    parser.add_argument(
        "--source",
        choices=["auto", "youtube", "google_play", "reddit"],
        default="auto",
    )
    parser.add_argument("--max", type=int, default=200, help="Max comments/reviews to fetch")
    parser.add_argument("--play-lang", default="ar")
    parser.add_argument("--play-country", default="sa")
    parser.add_argument("--save", help="Save raw fetched comments CSV")
    parser.add_argument("--analyze", action="store_true", help="Run sentiment analysis after fetch")
    parser.add_argument("--model", choices=["tfidf", "bert"], default="bert")
    parser.add_argument("--output", help="Analysis output CSV path")
    args = parser.parse_args()

    try:
        comments, source = fetch_comments(
            args.url,
            source=args.source,
            max_items=args.max,
            play_lang=args.play_lang,
            play_country=args.play_country,
        )
    except FetchDependencyError as exc:
        print(f"Dependency error: {exc}")
        print("Run: pip install -r requirements_fetch.txt")
        raise SystemExit(1) from exc
    except FetchError as exc:
        print(f"Fetch error: {exc}")
        raise SystemExit(1) from exc

    print(f"Fetched {len(comments)} items from {source}")

    paths = ProjectPaths.from_project_root(bootstrap.ROOT)
    ensure_dirs(paths.data_dir)
    raw_path = args.save or os.path.join(paths.data_dir, f"fetched_{source}_comments.csv")
    save_fetched_csv(comments, raw_path)
    print(f"Saved raw comments → {raw_path}")

    if args.analyze:
        analyze_fetched(comments, args.model, args.output)


if __name__ == "__main__":
    main()
