"""Merge synthetic + ASTD training data with held-out validation split (no leakage)."""

import os
from typing import Tuple

import pandas as pd

from paths import ProjectPaths


def merge_training_and_validation(
    root_dir: str | None = None,
    astd_val_ratio: float = 0.2,
    random_state: int = 42,
) -> Tuple[str, str, dict]:
    paths = ProjectPaths.from_project_root(root_dir)
    synthetic_path = os.path.join(paths.data_dir, "sentiment_dataset_multilingual.csv")
    astd_path = os.path.join(paths.data_dir, "real", "astd_processed.csv")
    manual_val_path = os.path.join(paths.data_dir, "real", "validation_manual.csv")
    train_out = os.path.join(paths.data_dir, "combined_training.csv")
    val_out = os.path.join(paths.data_dir, "real", "validation_comments.csv")

    synthetic = pd.read_csv(synthetic_path).dropna(subset=["text", "sentiment", "language"])
    synthetic = synthetic[["text", "sentiment", "language"]].drop_duplicates(subset=["text"])

    manual = pd.read_csv(manual_val_path) if os.path.exists(manual_val_path) else None
    if manual is None:
        old_val = os.path.join(paths.data_dir, "real", "validation_comments.csv")
        if os.path.exists(old_val):
            manual = pd.read_csv(old_val).head(35)
            manual.to_csv(manual_val_path, index=False, encoding="utf-8-sig")

    astd = pd.read_csv(astd_path).dropna(subset=["text", "sentiment", "language"])
    astd = astd[["text", "sentiment", "language"]].drop_duplicates(subset=["text"])
    astd["text"] = astd["text"].astype(str).str.strip()
    astd = astd[astd["text"].str.len().between(8, 280)]

    astd_parts = []
    for sentiment in ["negative", "neutral", "positive"]:
        subset = astd[astd["sentiment"] == sentiment]
        if subset.empty:
            continue
        n_val = max(1, int(len(subset) * astd_val_ratio))
        val_part = subset.sample(n=n_val, random_state=random_state)
        train_part = subset.drop(val_part.index)
        astd_parts.append((train_part, val_part))

    astd_train = pd.concat([p[0] for p in astd_parts], ignore_index=True)
    astd_val = pd.concat([p[1] for p in astd_parts], ignore_index=True)

    train_df = pd.concat([synthetic, astd_train], ignore_index=True).drop_duplicates(subset=["text"])
    val_frames = [astd_val]
    if manual is not None and len(manual):
        manual = manual.dropna(subset=["text", "sentiment"])
        val_frames.insert(0, manual[["text", "sentiment", "language"]])

    val_df = pd.concat(val_frames, ignore_index=True).drop_duplicates(subset=["text"])
    train_df.to_csv(train_out, index=False, encoding="utf-8-sig")
    val_df.to_csv(val_out, index=False, encoding="utf-8-sig")

    stats = {
        "synthetic_train": len(synthetic),
        "astd_train": len(astd_train),
        "astd_val": len(astd_val),
        "manual_val": len(manual) if manual is not None else 0,
        "total_train": len(train_df),
        "total_val": len(val_df),
        "train_path": train_out,
        "val_path": val_out,
    }
    return train_out, val_out, stats


def main() -> None:
    train_path, val_path, stats = merge_training_and_validation()
    print(f"Training set: {stats['total_train']} rows -> {train_path}")
    print(f"  synthetic: {stats['synthetic_train']} | ASTD train: {stats['astd_train']}")
    print(f"Validation: {stats['total_val']} rows -> {val_path}")
    print(f"  manual: {stats['manual_val']} | ASTD holdout: {stats['astd_val']}")


if __name__ == "__main__":
    main()
