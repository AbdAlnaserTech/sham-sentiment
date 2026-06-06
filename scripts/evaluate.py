import os
import sys
from typing import Dict

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from sklearn.metrics import classification_report  # noqa: E402

from data.loader import load_labeled_csv  # noqa: E402
from logging_utils import logger, save_json  # noqa: E402
from models.registry import load_predictor  # noqa: E402
from paths import ProjectPaths  # noqa: E402


def evaluate_on_labeled_csv(
    data_path: str,
    root_dir: str | None = None,
    model_kind: str = "tfidf",
    output_name: str | None = None,
) -> Dict:
    paths = ProjectPaths.from_project_root(root_dir or _ROOT)
    df = load_labeled_csv(data_path)
    predictor = load_predictor(model_kind, root_dir=paths.root_dir)

    predictions = predictor.predict_dataframe(df, text_col="text", language_col="language")
    y_true = df["sentiment"].tolist()
    y_pred = predictions["sentiment"].tolist()
    labels = ["negative", "neutral", "positive"]

    report = classification_report(
        y_true, y_pred, labels=labels, output_dict=True, zero_division=0
    )

    per_language = {}
    merged = df.copy()
    merged["y_pred"] = y_pred
    for lang in sorted(merged["language"].unique()):
        subset = merged[merged["language"] == lang]
        per_language[lang] = classification_report(
            subset["sentiment"],
            subset["y_pred"],
            labels=labels,
            output_dict=True,
            zero_division=0,
        )

    output = {
        "model": model_kind,
        "dataset": os.path.basename(data_path),
        "samples": len(df),
        "overall": report,
        "per_language": per_language,
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "accuracy": float(report["accuracy"]),
    }

    if output_name:
        out_file = os.path.join(paths.reports_dir, output_name)
    elif "manual" in os.path.basename(data_path):
        out_file = os.path.join(paths.reports_dir, f"validation_demo_{model_kind}.json")
    else:
        out_file = os.path.join(paths.reports_dir, f"validation_{model_kind}.json")

    os.makedirs(paths.reports_dir, exist_ok=True)

    save_json(out_file, output)
    logger.info(
        "%s macro F1=%.4f on %s (%d samples) -> %s",
        model_kind,
        output["macro_f1"],
        os.path.basename(data_path),
        len(df),
        os.path.basename(out_file),
    )
    return output


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate model on labeled CSV")
    parser.add_argument("--data", type=str, default="data/real/validation_comments.csv")
    parser.add_argument("--model", type=str, default="both", choices=["tfidf", "bert", "both"])
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    data_path = args.data if os.path.isabs(args.data) else os.path.join(_ROOT, args.data)
    models = ["tfidf", "bert"] if args.model == "both" else [args.model]

    for kind in models:
        try:
            result = evaluate_on_labeled_csv(
                data_path,
                model_kind=kind,
                output_name=args.output if len(models) == 1 else None,
            )
            print(f"{kind}: F1={result['macro_f1']:.4f} Acc={result['accuracy']:.4f} ({result['samples']} samples)")
        except Exception as exc:
            print(f"{kind}: skipped ({exc})")


if __name__ == "__main__":
    main()
