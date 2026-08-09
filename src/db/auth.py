"""
تشفير كلمات المرور والتحقق من هوية المستخدمين.

الملفات ذات الصلة:
  - repository.py → استدعاء hash_password و verify_password عند تسجيل الدخول
  - schema.sql    → جدول users (password_hash, role)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Any, Dict, Optional

# ── ثوابت التشفير ──
DEFAULT_ITERATIONS = 120_000


# ── تشفير والتحقق من كلمة المرور ──

def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    """
    يُنشئ hash آمن لكلمة المرور باستخدام PBKDF2-HMAC-SHA256.

    الصيغة المُخزَّنة: pbkdf2_sha256$iterations$salt$digest_hex
    """
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    يتحقق من تطابق كلمة المرور مع الـ hash المُخزَّن.

    يستخدم hmac.compare_digest لمنع هجمات التوقيت (timing attacks).
    """
    try:
        scheme, iter_str, salt, digest_hex = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(computed.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


# ── صلاحيات الأدوار ──

def user_can_analyze(role: str) -> bool:
    """هل يُسمح لهذا الدور بتشغيل التحليل؟ (admin أو analyst)"""
    return role in {"admin", "analyst"}


def user_can_admin(role: str) -> bool:
    """هل يملك هذا الدور صلاحيات الإدارة الكاملة؟"""
    return role == "admin"


# ── تمثيل المستخدم للواجهة ──

def public_user(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    يُرجع بيانات المستخدم الآمنة للعرض (بدون password_hash).

    يُستخدم بعد تسجيل الدخول الناجح أو عند جلب ملف المستخدم.
    """
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "full_name_ar": row.get("full_name_ar") or row["username"],
        "full_name_en": row.get("full_name_en") or row["username"],
    }
