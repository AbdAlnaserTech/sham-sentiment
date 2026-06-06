"""Optional API key authentication for FastAPI."""

from __future__ import annotations

import os

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = os.environ.get("SENTIMENT_API_KEY", "").strip()
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key (X-API-Key header)")
