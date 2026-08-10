"""
تهيئة مسار الاستيراد — يُستورد أولاً في أي ملف داخل app/.

المشكلة: ملفات الواجهة في app/ بينما المنطق في src/
الحل: إضافة src/ إلى sys.path حتى يعمل:
    from language import detect_language
    from models.registry import load_predictor
"""

import os
import sys

# ── بلوك 1: حساب مسارات المشروع ─────────────────────────────────────────────
# ROOT = مجلد sentiment_project/ (أب app/)
# SRC  = مجلد sentiment_project/src/ (الكود الأساسي)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

# app/ + src/ — ضروري على Streamlit Cloud عند تشغيل app/main.py
for path in (APP, SRC):
    if path not in sys.path:
        sys.path.insert(0, path)

# ── بلوك 3: ثابت جذر المشروع — يُستخدم أحياناً في المسارات النسبية ─────────
from paths import get_project_root  # noqa: E402 — بعد تعديل sys.path

PROJECT_ROOT = get_project_root()
