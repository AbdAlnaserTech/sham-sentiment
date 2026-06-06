import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import yaml

from paths import ProjectPaths, get_project_root


@dataclass
class AppConfig:
    data: Dict[str, Any] = field(default_factory=dict)
    model: Dict[str, Any] = field(default_factory=dict)
    training: Dict[str, Any] = field(default_factory=dict)
    inference: Dict[str, Any] = field(default_factory=dict)
    ui: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    platform: Dict[str, Any] = field(default_factory=dict)

    @property
    def labels(self) -> List[str]:
        return list(self.model.get("labels", ["negative", "neutral", "positive"]))

    @property
    def ngram_range(self) -> Tuple[int, int]:
        raw = self.model.get("vectorizer", {}).get("ngram_range", [1, 2])
        return int(raw[0]), int(raw[1])

    @property
    def max_features(self) -> int:
        return int(self.model.get("vectorizer", {}).get("max_features", 15000))

    @property
    def confidence_threshold(self) -> float:
        return float(self.inference.get("confidence_threshold", 55.0))

    @property
    def max_text_length(self) -> int:
        return int(self.inference.get("max_text_length", 5000))


def load_config(config_path: str | None = None) -> AppConfig:
    root = get_project_root()
    path = config_path or os.path.join(root, "configs", "default.yaml")
    if not os.path.exists(path):
        return AppConfig()

    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    return AppConfig(
        data=raw.get("data", {}),
        model=raw.get("model", {}),
        training=raw.get("training", {}),
        inference=raw.get("inference", {}),
        ui=raw.get("ui", {}),
        logging=raw.get("logging", {}),
        platform=raw.get("platform", {}),
    )


def resolve_dataset_path(config: AppConfig, paths: ProjectPaths, override: str | None = None) -> str:
    if override:
        return override if os.path.isabs(override) else os.path.join(paths.root_dir, override)
    default_rel = config.data.get("default_dataset", "data/sentiment_dataset_multilingual.csv")
    return os.path.join(paths.root_dir, default_rel)
