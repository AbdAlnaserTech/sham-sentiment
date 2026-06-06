import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from config import AppConfig, load_config
from evaluation.metrics import save_metrics_tables
from evaluation.plots import (
    plot_calibration,
    plot_confusion_matrix,
    plot_dataset_distribution,
    plot_f1_by_language,
    plot_roc_multiclass,
)
from logging_utils import logger, save_json
from paths import ProjectPaths, ensure_dirs
from preprocessing import TextPreprocessor


def build_text_column(df: pd.DataFrame, preprocessor: TextPreprocessor | None = None) -> pd.Series:
    pre = preprocessor or TextPreprocessor(remove_stopwords=True)
    return df.apply(
        lambda row: pre.preprocess(str(row["text"]), language=str(row["language"])).cleaned_text,
        axis=1,
    )


def train_and_evaluate(
    data_path: str,
    root_dir: str | None = None,
    config: AppConfig | None = None,
) -> Dict[str, Any]:
    paths = ProjectPaths.from_project_root(root_dir)
    cfg = config or load_config()
    ensure_dirs(paths.data_dir, paths.models_dir, paths.plots_dir)

    df = pd.read_csv(data_path)
    required_cols = {"text", "sentiment", "language"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"Dataset must contain columns: {required_cols}")

    df = df.dropna(subset=["text", "sentiment", "language"]).reset_index(drop=True)

    plot_dataset_distribution(
        df,
        out_path=os.path.join(paths.plots_dir, "dataset_distribution.png"),
    )

    preprocessor = TextPreprocessor(remove_stopwords=True)
    df["text_clean"] = build_text_column(df, preprocessor)

    X = df["text_clean"].astype(str).values
    y = df["sentiment"].astype(str).values
    stratify_key = (df["sentiment"].astype(str) + "__" + df["language"].astype(str)).values

    test_size = float(cfg.training.get("test_size", 0.2))
    random_state = int(cfg.training.get("random_state", 42))

    X_train, X_test, y_train, y_test, _, df_test = train_test_split(
        X,
        y,
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_key,
    )

    vectorizer = TfidfVectorizer(
        ngram_range=cfg.ngram_range,
        max_features=cfg.max_features,
        sublinear_tf=bool(cfg.model.get("vectorizer", {}).get("sublinear_tf", True)),
    )

    base_models = {
        "logreg": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            solver="lbfgs",
        ),
        "linear_svm": LinearSVC(class_weight="balanced"),
    }

    grid_values = cfg.model.get("grid_C", [0.5, 1.0, 2.0, 4.0])
    grids = {name: {"clf__C": grid_values} for name in base_models}

    cv_folds = int(cfg.training.get("cv_folds", 5))
    scoring = str(cfg.training.get("scoring", "f1_macro"))
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    best_name: Optional[str] = None
    best_score = -1.0
    best_est = None

    for name, model in base_models.items():
        pipe = Pipeline([("tfidf", vectorizer), ("clf", model)])
        grid = GridSearchCV(
            pipe,
            param_grid=grids[name],
            scoring=scoring,
            cv=cv,
            n_jobs=-1,
        )
        logger.info("Training %s with CV...", name)
        grid.fit(X_train, y_train)
        score = float(grid.best_score_)
        logger.info("%s best %s=%.4f params=%s", name, scoring, score, grid.best_params_)

        if score > best_score:
            best_score = score
            best_name = name
            best_est = grid.best_estimator_

    if best_est is None or best_name is None:
        raise RuntimeError("No model trained")

    logger.info("Best model: %s (cv %s=%.4f)", best_name, scoring, best_score)

    calib_cfg = cfg.model.get("calibration", {})
    calibrated = CalibratedClassifierCV(
        best_est,
        method=str(calib_cfg.get("method", "sigmoid")),
        cv=int(calib_cfg.get("cv", 5)),
    )
    calibrated.fit(X_train, y_train)
    final_model = calibrated
    y_pred = final_model.predict(X_test)
    probas = final_model.predict_proba(X_test)

    labels = cfg.labels
    report = classification_report(
        y_test, y_pred, labels=labels, output_dict=True, zero_division=0
    )

    plot_confusion_matrix(
        y_test,
        y_pred,
        labels=labels,
        title="Confusion Matrix (Overall)",
        out_path=os.path.join(paths.plots_dir, "confusion_overall.png"),
    )
    plot_calibration(
        probas,
        y_test,
        classes=labels,
        out_path=os.path.join(paths.plots_dir, "calibration_overall.png"),
    )
    plot_roc_multiclass(
        probas,
        y_test,
        classes=labels,
        out_path=os.path.join(paths.plots_dir, "roc_overall.png"),
    )

    per_language: Dict[str, Dict] = {}
    df_test_local = df_test.copy()
    df_test_local["y_true"] = y_test
    df_test_local["y_pred"] = y_pred

    for lang in sorted(df_test_local["language"].unique().tolist()):
        subset = df_test_local[df_test_local["language"] == lang]
        subset_probas = final_model.predict_proba(subset["text_clean"].astype(str).values)
        rep = classification_report(
            subset["y_true"],
            subset["y_pred"],
            labels=labels,
            output_dict=True,
            zero_division=0,
        )
        per_language[lang] = rep

        plot_confusion_matrix(
            subset["y_true"],
            subset["y_pred"],
            labels=labels,
            title=f"Confusion Matrix ({lang})",
            out_path=os.path.join(paths.plots_dir, f"confusion_{lang}.png"),
        )
        plot_calibration(
            subset_probas,
            subset["y_true"].astype(str).values,
            classes=labels,
            out_path=os.path.join(paths.plots_dir, f"calibration_{lang}.png"),
        )

    joblib.dump(final_model, paths.model_path)

    meta = {
        "model_name": best_name,
        "cv_f1_macro": best_score,
        "overall": report,
        "per_language": per_language,
        "labels": labels,
    }
    save_json(paths.metadata_path, meta)
    save_metrics_tables(paths, overall=report, per_language=per_language)
    plot_f1_by_language(
        per_language,
        out_path=os.path.join(paths.plots_dir, "f1_by_language.png"),
    )

    return meta
