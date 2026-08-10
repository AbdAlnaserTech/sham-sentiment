"""
قراءة configs/default.yaml وتحويلها لكائن AppConfig.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict

import yaml

from paths import ProjectPaths, get_project_root


# ── بلوك 1: حاوية الإعدادات ────────────────────────────────────────────────
@dataclass
class AppConfig:
    """حاوية الإعدادات — كل قسم YAML = dict."""
    data: Dict[str, Any] = field(default_factory=dict)
    inference: Dict[str, Any] = field(default_factory=dict)
    ui: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    platform: Dict[str, Any] = field(default_factory=dict)

    @property
    def confidence_threshold(self) -> float:
        """أقل من هذه النسبة → is_reliable=False (افتراضي 55%)."""
        return float(self.inference.get("confidence_threshold", 55.0))

    @property
    def max_text_length(self) -> int:
        """أقصى طول تعليق — 5000 حرف."""
        return int(self.inference.get("max_text_length", 5000))


# ── بلوك 2: تحميل YAML ───────────────────────────────────────────────────────
def load_config(config_path: str | None = None) -> AppConfig:
    """يقرأ YAML ويرجع AppConfig. إن لم يوجد الملف → إعدادات فارغة."""
    root = get_project_root()
    path = config_path or os.path.join(root, "configs", "default.yaml")
    if not os.path.exists(path):
        return AppConfig()

    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    inference = dict(raw.get("inference", {}))
    try:
        from cloud_setup import is_cloud_runtime

        if is_cloud_runtime():
            inference["use_finetuned"] = False
    except ImportError:
        pass

    return AppConfig(
        data=raw.get("data", {}),
        inference=inference,
        ui=raw.get("ui", {}),
        logging=raw.get("logging", {}),
        platform=raw.get("platform", {}),
    )


# ── بلوك 3: مسار مجموعة البيانات ─────────────────────────────────────────────
def resolve_dataset_path(config: AppConfig, paths: ProjectPaths, override: str | None = None) -> str:
    """مسار dataset — مع override من CLI."""
    if override:
        return override if os.path.isabs(override) else os.path.join(paths.root_dir, override)
    default_rel = config.data.get("default_dataset", "data/sentiment_dataset_multilingual.csv")
    return os.path.join(paths.root_dir, default_rel)
