import bootstrap  # noqa: F401
from datetime import datetime, timezone
from typing import Any, Dict, List

import streamlit as st

from components.app_header import render_author_badge
from config import load_config
from language import detect_language
from models.registry import available_models, load_predictor
from paths import ProjectPaths, ensure_dirs, get_project_root
from cloud_setup import bootstrap_cloud, cloud_max_batch_size, is_cloud_runtime

ModelKind = str


def init_app() -> tuple[ProjectPaths, Any]:
    paths = ProjectPaths.from_project_root(get_project_root())
    ensure_dirs(paths.data_dir, paths.models_dir, paths.reports_dir)
    bootstrap_cloud(paths.db_path)
    config = load_config()

    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "model_kind" not in st.session_state:
        default_model = config.inference.get("default_model", "bert")
        if is_cloud_runtime():
            default_model = "bert"
        st.session_state["model_kind"] = default_model
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False

    return paths, config


@st.cache_resource(show_spinner="جاري تحميل النموذj...")
def get_predictor(model_kind: str = "tfidf"):
    return load_predictor(model_kind, root_dir=get_project_root())


def append_history(result: Dict[str, Any]) -> None:
    st.session_state["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "language": result["language"],
        "sentiment": result["sentiment"],
        "confidence": result["confidence"],
        "is_reliable": result.get("is_reliable", True),
        "text": result["text"],
    })


def render_sidebar_settings(ui_config: Dict[str, Any] | None = None) -> tuple[bool, str, str, bool, bool, bool]:
    ui_config = ui_config or load_config().ui
    with st.sidebar:
        render_author_badge(ui_config, compact=True)
        st.markdown("### الإعدادات")

        models = available_models(get_project_root())
        options = [key for key, info in models.items() if info.get("available", True)]
        labels = {key: models[key]["label"] for key in options}

        current = st.session_state.get("model_kind", "bert")
        if current not in options:
            current = options[0]

        st.markdown("**النموذj**")
        model_kind = st.selectbox(
            "Model",
            options=options,
            index=options.index(current),
            format_func=lambda x: labels.get(x, x),
            label_visibility="collapsed",
        )
        st.session_state["model_kind"] = model_kind
        st.caption(models[model_kind].get("description", ""))

        st.divider()
        st.markdown("**اللغة**")
        auto_lang = st.toggle("كشف تلقائي للغة", value=True)
        lang_choice = st.selectbox(
            "Language",
            options=["en", "ar_fusha", "ar_shami"],
            disabled=auto_lang,
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**المظهر**")
        dark_mode = st.toggle("الوضع الداكن", value=st.session_state.get("dark_mode", False))
        st.session_state["dark_mode"] = dark_mode
        rtl_mode = st.toggle("واجهة عربية (RTL)", value=True)

        st.divider()
        st.markdown("**خيارات متقدمة**")
        compare_models = st.toggle("مقارنة TF-IDF vs BERT", value=False)

        st.divider()
        if is_cloud_runtime():
            st.info("☁️ نسخة سحابية — أول تحميل لـ BERT قد يستغرق دقائق.")
            st.caption(f"حد الدفعة على السحابة: {cloud_max_batch_size()} تعليق")

        st.divider()
        st.markdown("**تصدير**")
        history: List[Dict[str, Any]] = st.session_state.get("history", [])
        if history:
            import pandas as pd

            hist_df = pd.DataFrame(history)
            st.download_button(
                "تحميل سجل التحليلات CSV",
                data=hist_df.to_csv(index=False).encode("utf-8"),
                file_name=f"predictions_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption(f"{len(history)} تحليل محفوظ")
        else:
            st.caption("لم تُجرَ أي تحليلات بعد.")

    return auto_lang, lang_choice, model_kind, compare_models, rtl_mode, dark_mode


def resolve_language(text: str, auto_lang: bool, lang_choice: str) -> str:
    return detect_language(text) if auto_lang else lang_choice
