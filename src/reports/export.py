"""Export analysis results to PDF and Excel."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


def export_excel_bytes(df: pd.DataFrame, sheet_name: str = "Results") -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buffer.getvalue()


def export_pdf_bytes(
    df: pd.DataFrame,
    *,
    title: str = "Sentiment Analysis Report",
    meta: Optional[Dict[str, Any]] = None,
) -> bytes:
    from fpdf import FPDF

    meta = meta or {}
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    for key, value in meta.items():
        pdf.cell(0, 6, f"{key}: {value}", ln=True)
    pdf.ln(4)

    cols = list(df.columns)[:6]
    subset = df[cols].head(200)
    pdf.set_font("Helvetica", "B", 9)
    header = " | ".join(cols)
    pdf.multi_cell(0, 6, header)
    pdf.set_font("Helvetica", "", 8)
    for _, row in subset.iterrows():
        line = " | ".join(str(row[c])[:40] for c in cols)
        pdf.multi_cell(0, 5, line)

    out = pdf.output()
    return out if isinstance(out, bytes) else out.encode("latin-1", errors="replace")
