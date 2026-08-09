"""
تهيئة قاعدة SQLite وإدارة الاتصالات.

الملفات ذات الصلة:
  - schema.sql  → تعريف الجداول (users, batches, items, alerts)
  - auth.py     → تسجيل الدخول
  - repository.py → قراءة/كتابة السجلات
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from paths import ProjectPaths, ensure_dirs


def _schema_sql() -> str:
    """يقرأ ملف schema.sql المجاور لهذا الملف."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as handle:
        return handle.read()


def init_database(db_path: str | None = None) -> str:
    """
    ينشئ قاعدة البيانات إن لم تكن موجودة وينفّذ schema.sql.

    ترتيب تحديد المسار:
      1) المعامل db_path إن وُجد
      2) متغير البيئة SENTIMENT_DB_PATH (للنشر السحابي)
      3) data/sentiment_platform.db (افتراضي محلي)
    """
    paths = ProjectPaths.from_project_root()
    db_path = db_path or os.environ.get("SENTIMENT_DB_PATH") or paths.db_path
    ensure_dirs(os.path.dirname(db_path))
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_schema_sql())
        conn.commit()
    return db_path


@contextmanager
def get_connection(db_path: str | None = None) -> Iterator[sqlite3.Connection]:
    """
    Context manager آمن للاتصال بـ SQLite.

    - ينشئ DB تلقائياً إن لم يوجد
    - row_factory = Row → الوصول للأعمدة بالاسم
    - PRAGMA foreign_keys = ON → سلامة العلاقات
    - commit عند النجاح / rollback عند الخطأ
    - check_same_thread=False → Streamlit قد يستخدم threads مختلفة
    """
    paths = ProjectPaths.from_project_root()
    path = db_path or os.environ.get("SENTIMENT_DB_PATH") or paths.db_path
    if not os.path.exists(path):
        init_database(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
