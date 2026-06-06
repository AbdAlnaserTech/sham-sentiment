"""Build an expanded validation CSV (~108 samples) from manual rows + ASTD."""

import os
from typing import List

import pandas as pd

from paths import ProjectPaths, get_project_root


def build_expanded_validation(
    root_dir: str | None = None,
    target_per_cell: int = 12,
    random_state: int = 42,
) -> str:
    paths = ProjectPaths.from_project_root(root_dir)
    manual_path = os.path.join(paths.data_dir, "real", "validation_comments.csv")
    astd_path = os.path.join(paths.data_dir, "real", "astd_processed.csv")
    out_path = manual_path

    manual = pd.read_csv(manual_path) if os.path.exists(manual_path) else pd.DataFrame(
        columns=["text", "sentiment", "language"]
    )
    manual = manual.dropna(subset=["text", "sentiment"]).reset_index(drop=True)

    frames: List[pd.DataFrame] = [manual]
    if os.path.exists(astd_path):
        astd = pd.read_csv(astd_path).dropna(subset=["text", "sentiment", "language"])
        astd["text"] = astd["text"].astype(str).str.strip()
        astd = astd[astd["text"].str.len().between(8, 280)]

        existing_texts = set(manual["text"].str.strip().tolist())
        for lang in ["ar_fusha", "ar_shami", "en"]:
            for sentiment in ["negative", "neutral", "positive"]:
                have = len(
                    manual[
                        (manual["language"] == lang) & (manual["sentiment"] == sentiment)
                    ]
                )
                need = max(0, target_per_cell - have)
                if need == 0:
                    continue
                pool = astd[
                    (astd["language"] == lang) & (astd["sentiment"] == sentiment)
                ]
                if lang == "ar_shami" and len(pool) < need:
                    shami_hint = astd[astd["language"] == "ar_fusha"]
                    pool = pd.concat([pool, shami_hint], ignore_index=True)
                pool = pool[~pool["text"].isin(existing_texts)]
                if pool.empty:
                    continue
                sample = pool.sample(n=min(need, len(pool)), random_state=random_state)
                frames.append(sample[["text", "sentiment", "language"]])
                existing_texts.update(sample["text"].tolist())

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["text"]).reset_index(drop=True)
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path
