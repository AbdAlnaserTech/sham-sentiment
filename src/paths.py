"""
مسارات المشروع — data/, models/, db, configs.

ProjectPaths: كل المسارات المهمة كـ properties.
"""

import os
from dataclasses import dataclass


# ── بلوك 1: جذر المشروع ──────────────────────────────────────────────────────
def get_project_root() -> str:
    """جذر المشروع (مجلد sentiment_project/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── بلوك 2: مسارات ثابتة للمشروع ─────────────────────────────────────────────
@dataclass(frozen=True)
class ProjectPaths:
    """مسارات ثابتة — تُنشأ مرة من root_dir."""
    root_dir: str

    @classmethod
    def from_project_root(cls, root_dir: str | None = None) -> "ProjectPaths":
        return cls(root_dir=root_dir or get_project_root())

    @property
    def data_dir(self) -> str:
        return os.path.join(self.root_dir, "data")

    @property
    def models_dir(self) -> str:
        return os.path.join(self.root_dir, "models")

    @property
    def plots_dir(self) -> str:
        return os.path.join(self.models_dir, "plots")

    @property
    def reports_dir(self) -> str:
        return os.path.join(self.models_dir, "reports")

    @property
    def configs_dir(self) -> str:
        return os.path.join(self.root_dir, "configs")

    @property
    def bert_finetuned_dir(self) -> str:
        """مجلد BERT بعد fine-tune."""
        return os.path.join(self.models_dir, "bert_finetuned")

    @property
    def db_path(self) -> str:
        """SQLite — sentiment_platform.db"""
        return os.path.join(self.data_dir, "sentiment_platform.db")


# ── بلوك 3: إنشاء مجلدات ─────────────────────────────────────────────────────
def ensure_dirs(*dirs: str) -> None:
    """ينشئ مجلدات إن لم تكن موجودة."""
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
