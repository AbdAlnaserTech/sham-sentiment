"""Compare ML algorithms on validation set; pick best for production TF-IDF model."""

import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.calibration import CalibratedClassifierCV  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier, SGDClassifier  # noqa: E402
from sklearn.metrics import classification_report  # noqa: E402
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split  # noqa: E402
from sklearn.naive_bayes import ComplementNB, MultinomialNB  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.svm import LinearSVC  # noqa: E402

from config import load_config  # noqa: E402
from data.loader import load_labeled_csv  # noqa: E402
from logging_utils import logger, save_json  # noqa: E402
from models.trainer import build_text_column  # noqa: E402
from paths import ProjectPaths  # noqa: E402
from preprocessing import TextPreprocessor  # noqa: E402


def _algorithm_specs(grid_c: list[float]) -> dict:
    return {
        "logreg": {
            "estimator": LogisticRegression(max_iter=3000, class_weight="balanced", solver="lbfgs"),
            "param_grid": {"clf__C": grid_c},
            "label": "Logistic Regression",
        },
        "linear_svm": {
            "estimator": LinearSVC(class_weight="balanced"),
            "param_grid": {"clf__C": grid_c},
            "label": "Linear SVM",
        },
        "multinomial_nb": {
            "estimator": MultinomialNB(),
            "param_grid": {"clf__alpha": [0.05, 0.1, 0.5, 1.0]},
            "label": "Multinomial Naive Bayes",
        },
        "complement_nb": {
            "estimator": ComplementNB(),
            "param_grid": {"clf__alpha": [0.05, 0.1, 0.5, 1.0]},
            "label": "Complement Naive Bayes",
        },
        "passive_aggressive": {
            "estimator": PassiveAggressiveClassifier(class_weight="balanced", max_iter=2000),
            "param_grid": {"clf__C": [0.01, 0.1, 0.5, 1.0]},
            "label": "Passive Aggressive",
        },
        "sgd_log": {
            "estimator": SGDClassifier(
                loss="log_loss",
                class_weight="balanced",
                max_iter=2000,
                random_state=42,
            ),
            "param_grid": {"clf__alpha": [1e-5, 1e-4, 1e-3]},
            "label": "SGD (log loss)",
        },
    }


def compare_algorithms(
    train_path: str,
    validation_path: str,
    root_dir: str | None = None,
) -> dict:
    paths = ProjectPaths.from_project_root(root_dir or _ROOT)
    cfg = load_config()
    grid_c = [float(v) for v in cfg.model.get("grid_C", [0.5, 1.0, 2.0, 4.0])]

    train_df = pd.read_csv(train_path).dropna(subset=["text", "sentiment", "language"])
    val_df = load_labeled_csv(validation_path)

    preprocessor = TextPreprocessor(remove_stopwords=True)
    train_df = train_df.copy()
    train_df["text_clean"] = build_text_column(train_df, preprocessor)
    val_df = val_df.copy()
    val_df["text_clean"] = build_text_column(val_df, preprocessor)

    X_train = train_df["text_clean"].astype(str).values
    y_train = train_df["sentiment"].astype(str).values
    X_val = val_df["text_clean"].astype(str).values
    y_val = val_df["sentiment"].astype(str).values
    labels = cfg.labels

    vectorizer = TfidfVectorizer(
        ngram_range=cfg.ngram_range,
        max_features=cfg.max_features,
        sublinear_tf=bool(cfg.model.get("vectorizer", {}).get("sublinear_tf", True)),
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    stratify_key = (train_df["sentiment"].astype(str) + "__" + train_df["language"].astype(str)).values

    results = []
    best_name = None
    best_val_f1 = -1.0
    best_bundle = None

    for name, spec in _algorithm_specs(grid_c).items():
        logger.info("Testing algorithm: %s", name)
        pipe = Pipeline([("tfidf", vectorizer), ("clf", spec["estimator"])])
        grid = GridSearchCV(
            pipe,
            param_grid=spec["param_grid"],
            scoring="f1_macro",
            cv=cv,
            n_jobs=-1,
        )
        grid.fit(X_train, y_train)
        cv_score = float(grid.best_score_)

        calibrated = CalibratedClassifierCV(
            grid.best_estimator_,
            method="sigmoid",
            cv=3,
        )
        calibrated.fit(X_train, y_train)
        y_pred = calibrated.predict(X_val)
        val_report = classification_report(
            y_val, y_pred, labels=labels, output_dict=True, zero_division=0
        )
        val_f1 = float(val_report["macro avg"]["f1-score"])
        val_acc = float(val_report["accuracy"])

        row = {
            "algorithm": name,
            "label": spec["label"],
            "cv_f1_macro_synthetic": cv_score,
            "validation_macro_f1": val_f1,
            "validation_accuracy": val_acc,
            "best_params": grid.best_params_,
        }
        results.append(row)
        logger.info(
            "%s | CV F1=%.4f | Validation F1=%.4f | Acc=%.4f",
            name,
            cv_score,
            val_f1,
            val_acc,
        )

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_name = name
            best_bundle = {
                "model": calibrated,
                "best_params": grid.best_params_,
                "cv_f1": cv_score,
                "validation_f1": val_f1,
                "validation_accuracy": val_acc,
                "label": spec["label"],
            }

    if best_bundle is None or best_name is None:
        raise RuntimeError("No algorithm produced results")

    joblib.dump(best_bundle["model"], paths.model_path)

    output = {
        "selection_criterion": "validation_macro_f1",
        "validation_samples": len(val_df),
        "train_samples": len(train_df),
        "winner": {
            "algorithm": best_name,
            "label": best_bundle["label"],
            "validation_macro_f1": best_bundle["validation_f1"],
            "validation_accuracy": best_bundle["validation_accuracy"],
            "cv_f1_macro_synthetic": best_bundle["cv_f1"],
            "best_params": best_bundle["best_params"],
            "why_selected": (
                f"Highest macro F1 ({best_bundle['validation_f1']:.4f}) on real validation set "
                f"({len(val_df)} samples) among {len(results)} algorithms."
            ),
        },
        "ranking": sorted(results, key=lambda r: r["validation_macro_f1"], reverse=True),
    }

    meta_path = paths.metadata_path
    save_json(
        meta_path,
        {
            "model_name": best_name,
            "model_label": best_bundle["label"],
            "cv_f1_macro": best_bundle["cv_f1"],
            "validation_macro_f1": best_bundle["validation_f1"],
            "selection_note": "100% synthetic test F1 is not used for model selection",
            "best_params": best_bundle["best_params"],
            "overall": classification_report(
                y_val,
                best_bundle["model"].predict(X_val),
                labels=labels,
                output_dict=True,
                zero_division=0,
            ),
        },
    )

    out_file = os.path.join(paths.reports_dir, "algorithm_comparison.json")
    os.makedirs(paths.reports_dir, exist_ok=True)
    save_json(out_file, output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ML algorithms and save best model")
    parser.add_argument("--train", default="data/combined_training.csv")
    parser.add_argument("--validation", default="data/real/validation_manual.csv")
    args = parser.parse_args()

    train_path = args.train if os.path.isabs(args.train) else os.path.join(_ROOT, args.train)
    val_path = args.validation if os.path.isabs(args.validation) else os.path.join(_ROOT, args.validation)

    result = compare_algorithms(train_path, val_path)
    winner = result["winner"]
    print(f"Winner: {winner['algorithm']} ({winner['label']})")
    print(f"Validation F1: {winner['validation_macro_f1']:.4f}")
    print(f"Reason: {winner['why_selected']}")
    print("Saved: models/sentiment_model.pkl, models/reports/algorithm_comparison.json")


if __name__ == "__main__":
    main()
