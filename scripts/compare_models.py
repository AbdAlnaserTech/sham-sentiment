"""Compare TF-IDF vs BERT on validation and ASTD datasets."""

import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

import pandas as pd  # noqa: E402
from sklearn.metrics import classification_report  # noqa: E402

from data.loader import load_labeled_csv  # noqa: E402
from logging_utils import logger, save_json  # noqa: E402
from models.registry import load_predictor  # noqa: E402
from paths import ProjectPaths  # noqa: E402


def evaluate_model(predictor, df: pd.DataFrame) -> dict:
    preds = predictor.predict_dataframe(df, text_col="text", language_col="language")
    labels = ["negative", "neutral", "positive"]
    report = classification_report(
        df["sentiment"],
        preds["sentiment"],
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    return {
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "accuracy": float(report["accuracy"]),
        "report": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare TF-IDF and BERT models")
    parser.add_argument("--validation", type=str, default="data/real/validation_comments.csv")
    parser.add_argument("--astd", type=str, default="data/real/astd_processed.csv")
    parser.add_argument(
        "--astd-sample",
        type=int,
        default=300,
        help="Use random sample of ASTD for faster BERT evaluation (0 = full set)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Validation set only (fastest)",
    )
    args = parser.parse_args()

    paths = ProjectPaths.from_project_root(_ROOT)
    datasets = {}

    val_path = args.validation if os.path.isabs(args.validation) else os.path.join(_ROOT, args.validation)
    if os.path.exists(val_path):
        datasets["validation"] = load_labeled_csv(val_path)

    if not args.quick:
        astd_path = args.astd if os.path.isabs(args.astd) else os.path.join(_ROOT, args.astd)
        if os.path.exists(astd_path):
            astd_df = load_labeled_csv(astd_path)
            if args.astd_sample and len(astd_df) > args.astd_sample:
                astd_df = astd_df.sample(n=args.astd_sample, random_state=42).reset_index(drop=True)
            datasets["astd"] = astd_df

    if not datasets:
        raise SystemExit("No datasets found. Run download_astd.py first.")

    comparison = {}
    for model_kind in ["tfidf", "bert"]:
        logger.info("Evaluating model: %s", model_kind)
        try:
            predictor = load_predictor(model_kind, root_dir=_ROOT)
        except Exception as exc:
            logger.error("Could not load %s: %s", model_kind, exc)
            comparison[model_kind] = {"error": str(exc)}
            continue

        comparison[model_kind] = {}
        for dataset_name, frame in datasets.items():
            logger.info("  on %s (%d samples)", dataset_name, len(frame))
            comparison[model_kind][dataset_name] = evaluate_model(predictor, frame)

    rows = []
    for model_kind, results in comparison.items():
        if "error" in results:
            continue
        for dataset_name, metrics in results.items():
            rows.append({
                "model": model_kind,
                "dataset": dataset_name,
                "macro_f1": metrics["macro_f1"],
                "accuracy": metrics["accuracy"],
            })

    summary_df = pd.DataFrame(rows)
    print(summary_df.to_string(index=False))

    out_path = os.path.join(paths.reports_dir, "model_comparison.json")
    os.makedirs(paths.reports_dir, exist_ok=True)
    save_json(out_path, {"comparison": comparison, "summary": rows})
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
