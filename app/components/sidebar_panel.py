"""
محتوى الشريط الجانبي — ملخص الجلسة، اللغة، المظهر، الخروج.

يُستدعى من shared.render_sidebar_settings عبر render_sidebar_extras.
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from components.auth_panel import current_user


def _session_stats(history: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    يحسب إحصائيات تحليلات الجلسة الحالية.

    يرجع: total, positive, negative, neutral
    """
    counts = {"total": len(history), "positive": 0, "negative": 0, "neutral": 0}
    for item in history:
        sentiment = item.get("sentiment", "neutral")
        if sentiment in counts:
            counts[sentiment] += 1
    return counts


def render_session_summary() -> None:
    """
    يعرض ملخص تحليلات الجلسة في الشريط الجانبي.

    يقرأ من st.session_state["history"] — يُملأ عبر append_history / append_batch_to_history.
    """
    history: List[Dict[str, Any]] = st.session_state.get("history", [])
    stats = _session_stats(history)

    st.markdown("**ملخص الجلسة**")
    if stats["total"] == 0:
        st.caption("لم تُجرَ تحليلات بعد.")
        return

    c1, c2 = st.columns(2)
    c1.metric("تحليلات", stats["total"])
    avg_conf = sum(float(h.get("confidence", 0)) for h in history) / stats["total"]
    c2.metric("متوسط اليقين", f"{avg_conf:.0f}%")

    p, n, u = stats["positive"], stats["negative"], stats["neutral"]
    st.caption(f"إيجابي {p} · سلبي {n} · محايد {u}")


def render_sidebar_extras(ui_config: Dict[str, Any]) -> tuple[bool, str, bool]:
    """
    يبني عناصر الشريط الجانبي (بعد العلامة التجارية).

    Args:
        ui_config: قسم ui من YAML (غير مستخدم حالياً — محجوز للتوسع)

    المخرجات (tuple):
      auto_lang   — True = كشف تلقائي
      lang_choice — en | ar_fusha | ar_shami
      dark_mode   — الوضع الداكن
    """
    st.divider()
    render_session_summary()

    # ── إعدادات اللغة ──
    st.divider()
    st.markdown("**اللغة**")
    auto_lang = st.toggle("كشف تلقائي للغة", value=True)
    lang_choice = "ar_shami"
    if not auto_lang:
        lang_choice = st.selectbox(
            "اللغة",
            options=["en", "ar_fusha", "ar_shami"],
            format_func=lambda x: {"en": "English", "ar_fusha": "عربي فصحى", "ar_shami": "عربي شامي"}[x],
            label_visibility="collapsed",
        )
    st.caption("يدعم: عربي · English · شامي")

    # ── إعدادات المظهر ──
    st.divider()
    st.markdown("**المظهر**")
    dark_mode = st.toggle(
        "الوضع الداكن",
        value=st.session_state.get("dark_mode", False),
    )
    st.session_state["dark_mode"] = dark_mode

    render_sidebar_account()

    return auto_lang, lang_choice, dark_mode


def render_sidebar_account() -> None:
    """زر تسجيل الخروج — يظهر فقط للمستخدم المسجّل."""
    user = current_user()
    if not user:
        return

    st.divider()
    if st.button("تسجيل الخروج", key="sidebar_logout", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()
