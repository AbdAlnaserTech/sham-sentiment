"""Data access layer for users, batches, items, and alerts."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from db.auth import hash_password, public_user, verify_password
from db.database import get_connection, init_database
from paths import ProjectPaths


def ensure_default_users() -> None:
    init_database()
    defaults = [
        ("admin", "Admin@2026", "admin", "عبد الناصر حسون", "Abd Al-Nasser Hassoun"),
        ("analyst", "Analyst@2026", "analyst", "محلل", "Analyst"),
        ("viewer", "Viewer@2026", "viewer", "عارض", "Viewer"),
    ]
    with get_connection() as conn:
        for username, password, role, name_ar, name_en in defaults:
            exists = conn.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,)
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name_ar, full_name_en)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, hash_password(password), role, name_ar, name_en),
            )


def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username.strip(),),
        ).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            return None
        return public_user(dict(row))


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return public_user(dict(row)) if row else None


def save_batch_analysis(
    *,
    user_id: int | None,
    title: str,
    source: str,
    model_kind: str,
    results: List[Dict[str, Any]],
    alerts: List[Dict[str, Any]] | None = None,
) -> int:
    valid = [r for r in results if not r.get("error")]
    pos = sum(1 for r in valid if r.get("sentiment") == "positive")
    neg = sum(1 for r in valid if r.get("sentiment") == "negative")
    neu = sum(1 for r in valid if r.get("sentiment") == "neutral")
    avg_conf = (
        sum(float(r.get("confidence", 0)) for r in valid) / len(valid) if valid else 0.0
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_batches
            (user_id, title, source, model_kind, total_count, positive_count,
             negative_count, neutral_count, avg_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, source, model_kind, len(results), pos, neg, neu, avg_conf),
        )
        batch_id = int(cursor.lastrowid)

        conn.executemany(
            """
            INSERT INTO analysis_items
            (batch_id, text, language, sentiment, confidence, is_reliable, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    batch_id,
                    str(r.get("text", "")),
                    r.get("language") or "",
                    r.get("sentiment", "neutral"),
                    float(r.get("confidence", 0)),
                    1 if r.get("is_reliable", True) else 0,
                    r.get("error") or "",
                )
                for r in results
            ],
        )

        for alert in alerts or []:
            conn.execute(
                """
                INSERT INTO alerts (batch_id, severity, alert_type, message, metric_value, threshold)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    alert.get("severity", "info"),
                    alert.get("alert_type", "general"),
                    alert.get("message", ""),
                    alert.get("metric_value"),
                    alert.get("threshold"),
                ),
            )
        return batch_id


def fetch_dashboard_stats(limit: int = 12) -> Dict[str, Any]:
    with get_connection() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS batches,
                COALESCE(SUM(total_count), 0) AS items,
                COALESCE(SUM(positive_count), 0) AS positive,
                COALESCE(SUM(negative_count), 0) AS negative,
                COALESCE(SUM(neutral_count), 0) AS neutral,
                COALESCE(AVG(avg_confidence), 0) AS avg_confidence
            FROM analysis_batches
            """
        ).fetchone()

        recent = conn.execute(
            """
            SELECT id, title, source, model_kind, total_count, positive_count,
                   negative_count, neutral_count, avg_confidence, created_at
            FROM analysis_batches
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        unread_alerts = conn.execute(
            "SELECT COUNT(*) AS c FROM alerts WHERE is_read = 0"
        ).fetchone()["c"]

        recent_alerts = conn.execute(
            """
            SELECT a.id, a.severity, a.alert_type, a.message, a.created_at, b.title
            FROM alerts a
            JOIN analysis_batches b ON b.id = a.batch_id
            ORDER BY a.created_at DESC
            LIMIT 10
            """
        ).fetchall()

    return {
        "totals": dict(totals),
        "recent_batches": [dict(row) for row in recent],
        "unread_alerts": unread_alerts,
        "recent_alerts": [dict(row) for row in recent_alerts],
    }


def fetch_batch_items(batch_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT text, language, sentiment, confidence, is_reliable, error, created_at
            FROM analysis_items WHERE batch_id = ?
            ORDER BY id
            """,
            (batch_id,),
        ).fetchall()
    return pd.DataFrame([dict(row) for row in rows])


def list_batches(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, source, model_kind, total_count, created_at,
                   positive_count, negative_count, neutral_count
            FROM analysis_batches ORDER BY created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
