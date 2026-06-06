import os
from dataclasses import dataclass


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class ProjectPaths:
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
    def model_path(self) -> str:
        return os.path.join(self.models_dir, "sentiment_model.pkl")

    @property
    def metadata_path(self) -> str:
        return os.path.join(self.models_dir, "model_metadata.json")

    @property
    def db_path(self) -> str:
        return os.path.join(self.data_dir, "sentiment_platform.db")


def ensure_dirs(*dirs: str) -> None:
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
