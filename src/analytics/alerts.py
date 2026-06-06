"""Alert detection for negative sentiment spikes and low confidence."""

from __future__ import annotations

from typing import Any, Dict, List


def detect_batch_alerts(
    results: List[Dict[str, Any]],
    *,
    negative_threshold: float = 0.45,
    low_confidence_threshold: float = 50.0,
) -> List[Dict[str, Any]]:
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


def predict_trend_label(positive: int, negative: int, neutral: int) -> Dict[str, str]:
    total = positive + negative + neutral
    if total == 0:
        return {"trend": "unknown", "label_ar": "لا توجد بيانات", "recommendation_ar": "—"}

    pos_ratio = positive / total
    neg_ratio = negative / total

    if pos_ratio >= 0.55 and neg_ratio <= 0.25:
        return {
            "trend": "positive",
            "label_ar": "اتجاه إيجابي",
            "recommendation_ar": "حافظ على مستوى الخدمة الحالي وراقب التعليقات دورياً.",
        }
    if neg_ratio >= 0.45:
        return {
            "trend": "negative",
            "label_ar": "اتجاه سلبي",
            "recommendation_ar": "يُنصح بمراجعة الشكاوى المتكررة ومعالجة أسبابها بسرعة.",
        }
    return {
        "trend": "mixed",
        "label_ar": "اتجاه مختلط",
        "recommendation_ar": "تابع التعليقات المحايدة والسلبية وحدّد المواضيع الأكثر تكراراً.",
    }
