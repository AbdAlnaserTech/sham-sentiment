import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from config import load_config, resolve_dataset_path  # noqa: E402
from logging_utils import logger  # noqa: E402
from models.trainer import train_and_evaluate  # noqa: E402
from paths import ProjectPaths  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Train multilingual sentiment model")
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ProjectPaths.from_project_root(_ROOT)
    data_path = resolve_dataset_path(config, paths, override=args.data)

    meta = train_and_evaluate(data_path, root_dir=_ROOT, config=config)
    logger.info(
        "Saved model and metadata. Overall f1_macro=%.4f",
        float(meta["overall"]["macro avg"]["f1-score"]),
    )


if __name__ == "__main__":
    main()
