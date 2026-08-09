"""
اكتشاف التنبيهات: ارتفاع المشاعر السلبية وانخفاض ثقة النموذج.

يُستدعى بعد تحليل الدفعة وقبل save_batch_analysis في repository.py.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ── كشف تنبيهات الدفعة ──

def detect_batch_alerts(
    results: List[Dict[str, Any]],
    *,
    negative_threshold: float = 0.45,
    low_confidence_threshold: float = 50.0,
) -> List[Dict[str, Any]]:
    """
    يفحص نتائج الدفعة ويُنشئ قائمة تنبيهات.

    أنواع التنبيهات:
      - empty_batch      → لا توجد نتائج صالحة
      - negative_spike   → نسبة سلبية ≥ negative_threshold
      - low_confidence   → ≥35% من التعليقات بثقة < low_confidence_threshold

    Args:
        results: قائمة dict لكل تعليق (sentiment, confidence, error).
        negative_threshold: حد نسبة السلبية (0–1).
        low_confidence_threshold: حد الثقة المنخفضة (0–100).
    """
    valid = [r for r in results if not r.get("error")]
    if not valid:
        return [{
            "severity": "warning",
            "alert_type": "empty_batch",
            "message": "لم يتم تحليل أي تعليق صالح في هذه الدفعة.",
            "metric_value": 0,
            "threshold": 0,
        }]

    total = len(valid)
    negative = sum(1 for r in valid if r.get("sentiment") == "negative")
    neg_ratio = negative / total
    low_conf = sum(1 for r in valid if float(r.get("confidence", 0)) < low_confidence_threshold)

    alerts: List[Dict[str, Any]] = []

    if neg_ratio >= negative_threshold:
        severity = "critical" if neg_ratio >= 0.6 else "warning"
        alerts.append({
            "severity": severity,
            "alert_type": "negative_spike",
            "message": (
                f"تنبيه: نسبة التعليقات السلبية {neg_ratio:.0%} "
                f"({negative} من {total}) — راجع جودة الخدمة أو المنتج."
            ),
            "metric_value": neg_ratio,
            "threshold": negative_threshold,
        })

    if low_conf / total >= 0.35:
        alerts.append({
            "severity": "info",
            "alert_type": "low_confidence",
            "message": (
                f"ملاحظة: {low_conf} تعليق ({low_conf/total:.0%}) بثقة منخفضة "
                f"(أقل من {low_confidence_threshold:.0f}%)."
            ),
            "metric_value": low_conf / total,
            "threshold": 0.35,
        })

    return alerts
