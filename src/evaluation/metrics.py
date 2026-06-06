import os
from typing import Dict

import pandas as pd

from paths import ProjectPaths


def save_metrics_tables(paths: ProjectPaths, overall: Dict, per_language: Dict) -> None:
    overall_df = pd.DataFrame(overall).T
    overall_df.to_csv(os.path.join(paths.models_dir, "metrics_overall.csv"), index=True)

    frames = []
    for lang, report in per_language.items():
        df_lang = pd.DataFrame(report).T
        df_lang.insert(0, "language", lang)
        frames.append(df_lang)

    if frames:
        per_lang_df = pd.concat(frames, axis=0)
        per_lang_df.to_csv(
            os.path.join(paths.models_dir, "metrics_per_language.csv"), index=True
        )
