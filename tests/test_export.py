import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reports.export import export_excel_bytes, export_pdf_bytes


def test_export_excel_bytes():
    df = pd.DataFrame([{"text": "hello", "sentiment": "positive"}])
    data = export_excel_bytes(df)
    assert isinstance(data, bytes)
    assert len(data) > 100


def test_export_pdf_bytes_arabic_and_english():
    df = pd.DataFrame([
        {"text": "الخدمة كتير منيح", "sentiment": "positive", "language": "ar_shami", "confidence": 88.0},
        {"text": "Great product", "sentiment": "positive", "language": "en", "confidence": 90.0},
    ])
    data = export_pdf_bytes(df, title="Sentiment Report", meta={"Model": "bert", "Total": 2})
    assert isinstance(data, bytes)
    assert data.startswith(b"%PDF")
