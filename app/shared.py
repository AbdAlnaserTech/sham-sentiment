import bootstrap  # noqa: F401
from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st

from components.app_header import render_sidebar_brand
from components.sidebar_panel import render_sidebar_extras
from config import load_config
from language import detect_language
from models.registry import load_predictor
from paths import ProjectPaths, ensure_dirs, get_project_root
from cloud_setup import bootstrap_cloud

ModelKind = str
DEFAULT_MODEL = "bert"


def init_app() -> tuple[ProjectPaths, Any]:
    paths = ProjectPaths.from_project_root(get_project_root())
    ensure_dirs(paths.data_dir, paths.models_dir, paths.reports_dir)
    bootstrap_cloud(paths.db_path)
    config = load_config()

    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    st.session_state["model_kind"] = DEFAULT_MODEL

    return paths, config


@st.cache_resource(show_spinner="جاري تحميل النظام...")
def get_predictor(model_kind: str = DEFAULT_MODEL):
    return load_predictor(model_kind, root_dir=get_project_root())


def append_history(result: Dict[str, Any]) -> None:
    text = result.get("text", "")
    st.session_state["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "language": result.get("language") or detect_language(str(text)),
        "sentiment": result.get("sentiment", "neutral"),
        "confidence": result.get("confidence", 0.0),
        "is_reliable": result.get("is_reliable", True),
        "text": text,
    })


def render_sidebar_settings(ui_config: Dict[str, Any] | None = None) -> tuple[bool, str, str, bool, bool]:
    ui_config = ui_config or load_config().ui
    model_kind = DEFAULT_MODEL
    rtl_mode = True

    with st.sidebar:
        render_sidebar_brand(ui_config)
        auto_lang, lang_choice, dark_mode = render_sidebar_extras(ui_config)

    return auto_lang, lang_choice, model_kind, rtl_mode, dark_mode


def resolve_language(text: str, auto_lang: bool, lang_choice: str) -> str:
    return detect_language(text) if auto_lang else lang_choice
