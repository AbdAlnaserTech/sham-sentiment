import os
from typing import Dict, List, Optional

import pandas as pd

from language import detect_language
from paths import ProjectPaths, ensure_dirs


LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "pos": "positive",
    "neg": "negative",
    "neu": "neutral",
    "0": "negative",
    "1": "neutral",
    "2": "positive",
}


def normalize_sentiment(value: str) -> str:
    key = str(value).strip().lower()
    if key not in LABEL_MAP:
        raise ValueError(f"Unknown sentiment label: {value}")
    return LABEL_MAP[key]


def normalize_language(value: str | None, text: str) -> str:
    if value and str(value).strip():
        lang = str(value).strip().lower()
        if lang in {"en", "ar_fusha", "ar_shami"}:
            return lang
    return detect_language(text)


def load_labeled_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"text", "sentiment"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")

    df = df.dropna(subset=["text", "sentiment"]).copy()
    df["text"] = df["text"].astype(str)
    df["sentiment"] = df["sentiment"].map(normalize_sentiment)

    if "language" in df.columns:
        df["language"] = [
            normalize_language(row.get("language"), row["text"])
            for _, row in df.iterrows()
        ]
    else:
        df["language"] = df["text"].map(detect_language)

    return df.reset_index(drop=True)


def merge_datasets(paths: List[str]) -> pd.DataFrame:
    frames = [load_labeled_csv(path) for path in paths]
    merged = pd.concat(frames, axis=0, ignore_index=True)
    merged = merged.drop_duplicates(subset=["text"], keep="first")
    return merged.sample(frac=1.0, random_state=42).reset_index(drop=True)


def save_processed(df: pd.DataFrame, out_path: str) -> str:
    ensure_dirs(os.path.dirname(out_path))
    df.to_csv(out_path, index=False, encoding="utf-8")
    return out_path


def list_real_datasets(root_dir: str | None = None) -> Dict[str, str]:
    paths = ProjectPaths.from_project_root(root_dir)
    real_dir = os.path.join(paths.data_dir, "real")
    if not os.path.isdir(real_dir):
        return {}

    files = {}
    for name in os.listdir(real_dir):
        if name.lower().endswith(".csv"):
            files[name] = os.path.join(real_dir, name)
    return files
