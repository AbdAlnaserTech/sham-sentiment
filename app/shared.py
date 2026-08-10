"""
إعدادات مشتركة للواجهة (Streamlit).

هذا الملف يربط بين:
  - تهيئة المشروع (مجلدات، DB، YAML)
  - تحميل نموذج BERT (مرة واحدة مع cache)
  - إعدادات الشريط الجانبي وكشف اللغة
  - سجل تحليلات الجلسة (history)
"""

import bootstrap  # noqa: F401 — يضيف src/ إلى sys.path
from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st

from components.app_header import render_sidebar_brand
from components.sidebar_panel import render_sidebar_extras
from config import load_config
from language import detect_language
from models.registry import load_predictor
from paths import ProjectPaths, ensure_dirs, get_project_root
from cloud_setup import bootstrap_cloud, is_cloud_runtime

ModelKind = str
MODEL_KIND = "bert"


def init_app() -> tuple[ProjectPaths, Any]:
    """
    يُستدعى مرة عند فتح التطبيق (أول rerun).

    الخطوات:
      1) ProjectPaths — مسارات data/, models/, reports/
      2) ensure_dirs — إنشاء المجلدات إن لم تكن موجودة
      3) bootstrap_cloud — نسخ DB على Streamlit Cloud إن لزم
      4) load_config — قراءة configs/default.yaml
      5) session_state — history, dark_mode, model_kind
    """
    paths = ProjectPaths.from_project_root(get_project_root())
    ensure_dirs(paths.data_dir, paths.models_dir, paths.reports_dir)
    bootstrap_cloud(paths.db_path)
    config = load_config()

    # سجل تحليلات الجلسة — يظهر في الشريط الجانبي
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    st.session_state["model_kind"] = MODEL_KIND

    # محلياً: النموذج جاهز فوراً — bert_ready للسحابة فقط
    if not is_cloud_runtime():
        st.session_state.setdefault("bert_ready", True)

    return paths, config


@st.cache_resource(show_spinner="جاري تحميل نموذج BERT من HuggingFace (قد يستغرق 1-3 دقائق)...")
def get_predictor():
    """يحمّل BERT مرة واحدة لكل عملية خادم."""
    return load_predictor(root_dir=get_project_root())


def ensure_bert_ready() -> bool:
    """
    تهيئة BERT على Streamlit Cloud — مرة واحدة لكل جلسة.

    يعرض رسالة واضحة أثناء تنزيل النموذج بدل spinner صامت.
    """
    if st.session_state.get("bert_ready"):
        return True

    if not is_cloud_runtime():
        st.session_state["bert_ready"] = True
        return True

    with st.status("جاري تهيئة نموذج الذكاء الاصطناعي...", expanded=True) as status:
        st.caption(
            "أول تشغيل على السحابة: يتم تنزيل النموذج من HuggingFace. "
            "قد يستغرق 1–3 دقائق — لا تغلق الصفحة."
        )
        try:
            get_predictor()
            from models.bert_predictor import warmup_bert_model

            warmup_bert_model(get_project_root())
            st.session_state["bert_ready"] = True
            status.update(label="✅ النموذج جاهز للتحليل", state="complete", expanded=False)
            return True
        except Exception as exc:
            status.update(label="❌ تعذّر تحميل النموذج", state="error")
            st.error(f"خطأ تحميل BERT: {exc}")
            return False


def append_history(result: Dict[str, Any]) -> None:
    """
    يضيف نتيجة تحليل واحدة لملخص الجلسة في الشريط الجانبي.

    يُستدعى بعد تحليل «تعليق واحد» — ليس للدفعات (لها append_batch_to_history).
    """
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
    """
    يبني الشريط الجانبي ويرجع إعدادات التحليل.

    المخرجات (tuple):
      auto_lang   — True = كشف تلقائي | False = لغة يدوية
      lang_choice — en | ar_fusha | ar_shami (عند auto_lang=False)
      model_kind  — دائماً "bert" في الواجهة
      rtl_mode    — True = واجهة RTL للعربية
      dark_mode   — True = الوضع الداكن
    """
    ui_config = ui_config or load_config().ui
    model_kind = MODEL_KIND
    rtl_mode = True

    with st.sidebar:
        render_sidebar_brand(ui_config)
        auto_lang, lang_choice, dark_mode = render_sidebar_extras(ui_config)

    return auto_lang, lang_choice, model_kind, rtl_mode, dark_mode


def resolve_language(text: str, auto_lang: bool, lang_choice: str) -> str:
    """
    يحدّد لغة التعليق قبل إرساله للنموذج.

    auto_lang=True  → detect_language(text) من language.py
    auto_lang=False → اللغة المختارة يدوياً من الشريط (en/ar_fusha/ar_shami)
    """
    return detect_language(text) if auto_lang else lang_choice
