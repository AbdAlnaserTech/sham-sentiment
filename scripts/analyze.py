"""Analyze one comment or a file/list of comments from the terminal."""

import argparse
import json
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

import pandas as pd  # noqa: E402

from language import SENTIMENT_LABEL_AR  # noqa: E402


def _print_result(result: dict, index: int | None = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    sentiment_ar = SENTIMENT_LABEL_AR.get(result["sentiment"], result["sentiment"])
    print(f"{prefix}{result['text']}")
    print(f"  -> {sentiment_ar} ({result['sentiment']}) | {result['confidence']:.1f}% | {result['language']}")
    if result.get("error"):
        print(f"  !! {result['error']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze comment sentiment")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Single comment text")
    group.add_argument("--file", type=str, help="CSV/TXT file (CSV needs text column; TXT one comment per line)")
    group.add_argument("--lines", nargs="+", help="Multiple comments from command line")
    parser.add_argument("--output", type=str, default=None, help="Save results to CSV")
    parser.add_argument("--model", type=str, default="tfidf", choices=["tfidf", "bert"])
    args = parser.parse_args()

    from models.registry import load_predictor  # noqa: E402

    predictor = load_predictor(args.model, root_dir=_ROOT)

    if args.text:
        result = predictor.predict_with_confidence(args.text)
        _print_result(result)
        results = [result]
    else:
        if args.file:
            path = args.file
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
                if "text" not in df.columns:
                    raise SystemExit("CSV must contain a `text` column.")
                texts = [str(v) for v in df["text"].tolist()]
                languages = (
                    [str(v) if pd.notna(v) else None for v in df["language"].tolist()]
                    if "language" in df.columns
                    else None
                )
            else:
                with open(path, "r", encoding="utf-8") as handle:
                    texts = [line.strip() for line in handle if line.strip()]
                languages = None
        else:
            texts = args.lines or []
            languages = None

        results = predictor.predict_batch(texts, languages=languages)
        for index, result in enumerate(results, start=1):
            _print_result(result, index=index)

    if args.output:
        out_df = pd.DataFrame(results)
        out_df.to_csv(args.output, index=False, encoding="utf-8-sig")
        print(f"\nSaved: {args.output}")

    summary = pd.DataFrame(results)
    if not summary.empty and "sentiment" in summary.columns:
        print("\nSummary:")
        print(summary["sentiment"].value_counts().to_string())


if __name__ == "__main__":
    main()
