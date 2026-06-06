"""Password hashing and user authentication."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Any, Dict, Optional

DEFAULT_ITERATIONS = 120_000


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
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


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


def user_can_analyze(role: str) -> bool:
    return role in {"admin", "analyst"}


def user_can_admin(role: str) -> bool:
    return role == "admin"


def public_user(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "full_name_ar": row.get("full_name_ar") or row["username"],
        "full_name_en": row.get("full_name_en") or row["username"],
    }
