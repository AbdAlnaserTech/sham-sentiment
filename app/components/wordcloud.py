import os
import platform

import streamlit as st
from wordcloud import WordCloud

from language import is_arabic

MAX_WORDCLOUD_WORDS = 80


def _resolve_font() -> str | None:
    candidates = []
    if platform.system() == "Windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        for name in ("arial.ttf", "tahoma.ttf", "segoeui.ttf"):
            candidates.append(os.path.join(windir, "Fonts", name))
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansArabic-Regular.ttf",
        ])
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def render_wordcloud(text: str) -> None:
    if not (text or "").strip():
        st.caption("لا يوجد نص لعرض سحابة الكلمات.")
        return

    tokens = text.split()
    if len(tokens) < 3:
        st.caption("💡 سحابة الكلمات تظهر بشكل أوضح مع نص أطول (3+ كلمات).")
        return

    try:
        text_for_wc = text
        font_path = _resolve_font() if is_arabic(text) else None

        if is_arabic(text):
            try:
                import arabic_reshaper
                from bidi.algorithm import get_display

                tokens = text.split()
                text_for_wc = " ".join(
                    get_display(arabic_reshaper.reshape(token)) for token in tokens
                )
            except ImportError:
                pass

        wc = WordCloud(
            width=900,
            height=450,
            background_color="white",
            font_path=font_path,
            max_words=MAX_WORDCLOUD_WORDS,
        ).generate(text_for_wc)
        st.image(wc.to_image(), use_container_width=True)
    except Exception as exc:
        st.info(f"سحابة الكلمات غير متاحة: {exc}")
