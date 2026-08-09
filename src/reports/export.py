"""
تصدير نتائج التحليل إلى Excel و PDF.

يدعم العربية في PDF عبر arabic_reshaper + bidi وخطوط Unicode.
"""

from __future__ import annotations

import io
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from paths import get_project_root


# ── تصدير Excel ──

def export_excel_bytes(df: pd.DataFrame, sheet_name: str = "Results") -> bytes:
    """
    يُحوّل DataFrame إلى ملف Excel في الذاكرة (bytes).

    Args:
        df: جدول النتائج.
        sheet_name: اسم الورقة (حد Excel 31 حرفاً).
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buffer.getvalue()


# ── دعم العربية في PDF ──

def _reshape_arabic(text: str) -> str:
    """يعيد تشكيل النص العربي وعكس اتجاهه للعرض الصحيح في PDF."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        if any("\u0600" <= char <= "\u06FF" for char in text):
            return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        pass
    return text


def _find_unicode_font() -> str | None:
    """
    يبحث عن خط يدعم Unicode/العربية (Noto, Arial, Tahoma, DejaVu).

    Returns:
        مسار الخط أو None إن لم يُوجَد.
    """
    root = get_project_root()
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates = [
        os.path.join(root, "assets", "fonts", "NotoSansArabic-Regular.ttf"),
        os.path.join(windir, "Fonts", "arial.ttf"),
        os.path.join(windir, "Fonts", "tahoma.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _pdf_safe_text(text: Any, *, max_len: int = 120) -> str:
    """ينظّف النص للطباعة في PDF مع اقتطاع الطول ودعم العربية."""
    value = str(text or "").replace("\t", " ").replace("\n", " ").strip()
    if len(value) > max_len:
        value = value[: max_len - 3] + "..."
    return _reshape_arabic(value) if value else "-"


def _write_pdf_line(pdf, text: str, *, height: float = 6.0, font_size: int = 10) -> None:
    """
    يكتب سطراً في PDF مع fallback إلى ASCII عند فشل multi_cell.

    Args:
        pdf: كائن FPDF.
        text: النص بعد _pdf_safe_text.
    """
    pdf.set_font_size(font_size)
    pdf.set_x(pdf.l_margin)
    try:
        pdf.multi_cell(pdf.epw, height, text)
    except Exception:
        ascii_text = re.sub(r"\s+", " ", str(text)).encode("ascii", errors="ignore").decode("ascii")
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, height, ascii_text or "-")


# ── تصدير PDF ──

def export_pdf_bytes(
    df: pd.DataFrame,
    *,
    title: str = "Sentiment Analysis Report",
    meta: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    يُنشئ تقرير PDF مختصر من DataFrame (حتى 200 صف، 6 أعمدة).

    Args:
        df: جدول النتائج.
        title: عنوان التقرير.
        meta: بيانات وصفية إضافية (model, source, ...).

    Returns:
        محتوى PDF كـ bytes للتنزيل أو الإرسال.
    """
    from fpdf import FPDF

    meta = meta or {}
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = _find_unicode_font()
    font_name = "BodyFont"
    if font_path:
        pdf.add_font(font_name, "", font_path)
        pdf.set_font(font_name, size=11)
    else:
        font_name = "Helvetica"
        pdf.set_font(font_name, size=11)

    _write_pdf_line(pdf, _pdf_safe_text(title, max_len=200), height=8, font_size=16)
    _write_pdf_line(
        pdf,
        _pdf_safe_text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", max_len=200),
        height=6,
        font_size=10,
    )
    for key, value in meta.items():
        _write_pdf_line(
            pdf,
            _pdf_safe_text(f"{key}: {value}", max_len=200),
            height=6,
            font_size=10,
        )
    pdf.ln(4)

    cols = list(df.columns)[:6]
    subset = df[cols].head(200)
    _write_pdf_line(pdf, _pdf_safe_text(" | ".join(cols), max_len=400), height=6, font_size=9)
    for _, row in subset.iterrows():
        line = " | ".join(_pdf_safe_text(row[c], max_len=40) for c in cols)
        _write_pdf_line(pdf, line, height=5, font_size=8)

    out = pdf.output()
    if isinstance(out, bytes):
        return out
    if isinstance(out, bytearray):
        return bytes(out)
    return str(out).encode("latin-1", errors="replace")
