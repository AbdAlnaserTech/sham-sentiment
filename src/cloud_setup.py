"""Bootstrap helpers for Streamlit Community Cloud (free tier)."""

from __future__ import annotations

import os


def _apply_streamlit_secrets() -> None:
    """Map Streamlit Cloud secrets into environment variables."""
    try:
        import streamlit as st

        for key in (
            "SENTIMENT_CLOUD",
            "SENTIMENT_CLOUD_LIGHT",
            "SENTIMENT_MAX_BATCH",
            "SENTIMENT_API_KEY",
        ):
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:
        return


def is_cloud_runtime() -> bool:
    """True when running on Streamlit Cloud or SENTIMENT_CLOUD is set."""
    runtime = os.environ.get("STREAMLIT_RUNTIME_ENVIRONMENT", "").strip().lower()
    if runtime in {"cloud", "streamlit_cloud"}:
        return True
    flag = os.environ.get("SENTIMENT_CLOUD", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def is_cloud_light_mode() -> bool:
    """Use a single BERT model (no ensemble) to fit ~1 GB RAM."""
    if not is_cloud_runtime():
        return False
    flag = os.environ.get("SENTIMENT_CLOUD_LIGHT", "1").strip().lower()
    return flag not in {"0", "false", "no", "off"}


def bootstrap_cloud(db_path: str | None = None) -> None:
    """Initialize DB and cloud flags once per process."""
    _apply_streamlit_secrets()

    if not is_cloud_runtime():
        return

    os.environ.setdefault("SENTIMENT_CLOUD", "1")
    os.environ.setdefault("SENTIMENT_CLOUD_LIGHT", "1")
    os.environ.setdefault("SENTIMENT_MAX_BATCH", "100")

    if os.environ.get("SENTIMENT_DB_READY") == "1":
        return

    from db.database import init_database
    from db.repository import ensure_default_users

    init_database(db_path)
    ensure_default_users()
    os.environ["SENTIMENT_DB_READY"] = "1"


def cloud_max_batch_size(default: int = 2000) -> int:
    if not is_cloud_runtime():
        return default
    try:
        return int(os.environ.get("SENTIMENT_MAX_BATCH", "100"))
    except ValueError:
        return 100
