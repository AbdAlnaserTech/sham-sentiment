"""
عمليات التصدير والحذف على مستوى الدفعات (batches).

الملفات ذات الصلة:
  - database.py   → get_connection للاتصال بـ SQLite
  - repository.py → حفظ الدفعات (save_batch_analysis)
  - export.py     → تصدير النتائج إلى Excel/PDF
"""

from __future__ import annotations

import pandas as pd

from db.database import get_connection


# ── قراءة جميع العناصر المحفوظة ──

def fetch_all_saved_items() -> pd.DataFrame:
    """
    يجلب كل عناصر التحليل مع بيانات الدفعة المرتبطة بها.

    يُستخدم في صفحة التصدير الشامل أو النسخ الاحتياطي.
    يُرجع DataFrame فارغاً بأعمدة محددة إن لم توجد سجلات.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                b.id AS batch_id,
                b.title AS batch_title,
                b.source AS batch_source,
                b.created_at AS batch_date,
                i.text AS comment,
                i.language,
                i.sentiment,
                i.confidence,
                i.is_reliable,
                i.error,
                i.created_at AS analyzed_at
            FROM analysis_items i
            JOIN analysis_batches b ON b.id = i.batch_id
            ORDER BY i.id DESC
            """
        ).fetchall()
    if not rows:
        return pd.DataFrame(
            columns=[
                "batch_id",
                "batch_title",
                "batch_source",
                "batch_date",
                "comment",
                "language",
                "sentiment",
                "confidence",
                "is_reliable",
                "error",
                "analyzed_at",
            ]
        )
    return pd.DataFrame([dict(row) for row in rows])


# ── حذف الدفعات ──

def delete_batch(batch_id: int) -> bool:
    """
    يحذف دفعة تحليل واحدة وجميع عناصرها (CASCADE عبر foreign key).

    Returns:
        True إذا وُجدت الدفعة وحُذفت، False إن لم تُوجَد.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM analysis_batches WHERE id = ?", (batch_id,))
        return cursor.rowcount > 0


def delete_all_saved_batches() -> int:
    """
    يحذف كل الدفعات المحفوظة (عملية خطرة — للمسح الكامل فقط).

    Returns:
        عدد الدفعات المحذوفة.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM analysis_batches")
        return int(cursor.rowcount or 0)
