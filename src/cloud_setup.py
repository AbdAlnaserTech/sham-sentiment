"""مساعدات تهيئة Streamlit Community Cloud (الطبقة المجانية)."""

from __future__ import annotations

import os
from urllib.parse import quote
from typing import Any
from urllib.parse import urlparse


def _apply_streamlit_secrets() -> None:
    """نقل أسرار Streamlit Cloud إلى متغيرات البيئة."""
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
    """True عند التشغيل على Streamlit Cloud أو عند تعيين SENTIMENT_CLOUD."""
    runtime = os.environ.get("STREAMLIT_RUNTIME_ENVIRONMENT", "").strip().lower()
    if runtime in {"cloud", "streamlit_cloud"}:
        return True
    # مسار Streamlit Community Cloud القياسي
    if os.path.isdir("/mount/src"):
        return True
    flag = os.environ.get("SENTIMENT_CLOUD", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def get_public_app_url(platform: dict[str, Any] | None = None) -> str | None:
    """
    رابط مشاركة التطبيق — يُعرض في الواجهة فقط على Streamlit Cloud.

    محلياً (localhost) يرجع None حتى لا يظهر رابط سحابي معطّل.
    """
    if not is_cloud_runtime():
        return None

    try:
        import streamlit as st

        current = getattr(getattr(st, "context", None), "url", None)
        if current and ".streamlit.app" in current:
            parsed = urlparse(str(current))
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass

    if platform:
        app_url = str(platform.get("app_url", "")).strip()
        if app_url:
            return app_url
    return None


def get_whatsapp_share_url(platform: dict[str, Any] | None = None) -> str | None:
    """رابط مشاركة التطبيق عبر واتساب (يفتح واتساب مع رسالة جاهزة)."""
    if not platform:
        return None
    app_url = get_public_app_url(platform) or str(platform.get("app_url", "")).strip()
    if not app_url:
        return None
    message = str(platform.get("whatsapp_share_message", "")).strip()
    if not message:
        message = (
            "📊 منصة تحليل مشاعر التعليقات — جامعة الشام\n"
            f"{app_url}\n\n"
            "🔐 للدخول:\nadmin / Admin@2026"
        )
    return f"https://wa.me/?text={quote(message)}"


def is_cloud_light_mode() -> bool:
    """استخدام نموذج BERT واحد (بدون ensemble) لملاءمة ~1 GB RAM."""
    if not is_cloud_runtime():
        return False
    flag = os.environ.get("SENTIMENT_CLOUD_LIGHT", "1").strip().lower()
    return flag not in {"0", "false", "no", "off"}


def bootstrap_cloud(db_path: str | None = None) -> None:
    """تهيئة قاعدة البيانات وإعدادات السحابة مرة واحدة لكل عملية."""
    _apply_streamlit_secrets()

    if not is_cloud_runtime():
        return

    # تعيين القيم الافتراضية لبيئة السحابة
    os.environ.setdefault("SENTIMENT_CLOUD", "1")
    os.environ.setdefault("SENTIMENT_CLOUD_LIGHT", "1")
    os.environ.setdefault("SENTIMENT_MAX_BATCH", "100")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")

    # تجنب إعادة التهيئة في نفس العملية
    if os.environ.get("SENTIMENT_DB_READY") == "1":
        return

    from db.database import init_database
    from db.repository import ensure_default_users

    init_database(db_path)
    ensure_default_users()
    os.environ["SENTIMENT_DB_READY"] = "1"


def cloud_max_batch_size(default: int = 2000) -> int:
    """إرجاع الحد الأقصى لحجم الدفعة في السحابة أو القيمة الافتراضية محلياً."""
    if not is_cloud_runtime():
        return default
    try:
        return int(os.environ.get("SENTIMENT_MAX_BATCH", "100"))
    except ValueError:
        return 100
