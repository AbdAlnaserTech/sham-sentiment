"""Backward-compatible re-exports from src package."""

import sys
import os

_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from language import (  # noqa: F401
    AR_STOPWORDS,
    EN_STOPWORDS,
    SHAMI_HINT_WORDS,
    detect_language,
    is_arabic,
    normalize_arabic,
    safe_percent,
)
from logging_utils import logger, load_json, save_json, setup_logging  # noqa: F401
from paths import ProjectPaths, ensure_dirs, get_project_root  # noqa: F401
