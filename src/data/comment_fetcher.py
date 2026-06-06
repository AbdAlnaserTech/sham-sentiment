"""Fetch real comments/reviews from public sources (YouTube, Google Play, Reddit)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

SourceKind = Literal["youtube", "google_play", "reddit", "auto"]

YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
PLAY_ID_RE = re.compile(r"[?&]id=([A-Za-z0-9._]+)")
REDDIT_RE = re.compile(r"reddit\.com/r/[^/]+/comments/([A-Za-z0-9]+)", re.I)


@dataclass
class FetchedComment:
    text: str
    author: str = ""
    source: str = ""
    source_id: str = ""
    likes: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FetchError(Exception):
    pass


class FetchDependencyError(FetchError):
    pass


def _looks_like_package_id(raw: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]+)+$", raw))


def detect_source(url_or_id: str) -> SourceKind:
    raw = (url_or_id or "").strip()
    lower = raw.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return "youtube"
    if "play.google.com" in lower or _looks_like_package_id(raw):
        return "google_play"
    if "reddit.com" in lower:
        return "reddit"
    if re.match(r"^[A-Za-z0-9_-]{11}$", raw):
        return "youtube"
    raise FetchError(
        "تعذّر التعرف على المصدر. استخدم رابط YouTube أو Google Play أو Reddit، "
        "أو package id مثل com.whatsapp"
    )


def extract_youtube_video_id(url_or_id: str) -> str:
    raw = (url_or_id or "").strip()
    match = YOUTUBE_ID_RE.search(raw)
    if match:
        return match.group(1)
    if re.match(r"^[A-Za-z0-9_-]{11}$", raw):
        return raw
    raise FetchError("رابط YouTube غير صالح. مثال: https://www.youtube.com/watch?v=VIDEO_ID")


def extract_google_play_id(url_or_id: str) -> str:
    raw = (url_or_id or "").strip()
    match = PLAY_ID_RE.search(raw)
    if match:
        return match.group(1)
    if re.match(r"^[A-Za-z][A-Za-z0-9._]*$", raw):
        return raw
    raise FetchError(
        "معرّف التطبيق غير صالح. مثال: com.whatsapp أو رابط Google Play كامل"
    )


def extract_reddit_post_url(url: str) -> str:
    raw = (url or "").strip().rstrip("/")
    if not REDDIT_RE.search(raw):
        raise FetchError("رابط Reddit غير صالح. مثال: https://www.reddit.com/r/.../comments/...")
    if not raw.endswith(".json"):
        raw = f"{raw.split('?')[0]}.json"
    return raw


def _clean_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def fetch_youtube_comments(
    url_or_id: str,
    max_comments: int = 500,
) -> List[FetchedComment]:
    try:
        from youtube_comment_downloader import YoutubeCommentDownloader
    except ImportError as exc:
        raise FetchDependencyError(
            "ثبّت الحزمة: pip install youtube-comment-downloader"
        ) from exc

    video_id = extract_youtube_video_id(url_or_id)
    url = f"https://www.youtube.com/watch?v={video_id}"
    downloader = YoutubeCommentDownloader()
    items: List[FetchedComment] = []

    try:
        for index, comment in enumerate(downloader.get_comments_from_url(url)):
            if index >= max_comments:
                break
            text = _clean_text(comment.get("text", ""))
            if not text:
                continue
            items.append(
                FetchedComment(
                    text=text,
                    author=str(comment.get("author", "")),
                    source="youtube",
                    source_id=video_id,
                    likes=int(comment.get("votes", 0) or 0),
                    created_at=str(comment.get("time", "")),
                )
            )
    except Exception as exc:
        raise FetchError(f"فشل جلب تعليقات YouTube: {exc}") from exc

    if not items:
        raise FetchError("لم يُعثر على تعليقات — تأكد أن الفيديو عاماً ويحتوي تعليقات.")
    return items


def fetch_google_play_reviews(
    url_or_id: str,
    max_reviews: int = 500,
    lang: str = "ar",
    country: str = "sa",
) -> List[FetchedComment]:
    try:
        from google_play_scraper import Sort, reviews
    except ImportError as exc:
        raise FetchDependencyError(
            "ثبّت الحزمة: pip install google-play-scraper"
        ) from exc

    app_id = extract_google_play_id(url_or_id)
    items: List[FetchedComment] = []
    token = None

    try:
        while len(items) < max_reviews:
            batch_size = min(200, max_reviews - len(items))
            batch, token = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=token,
            )
            if not batch:
                break
            for row in batch:
                text = _clean_text(row.get("content", ""))
                if not text:
                    continue
                items.append(
                    FetchedComment(
                        text=text,
                        author=str(row.get("userName", "")),
                        source="google_play",
                        source_id=app_id,
                        likes=int(row.get("thumbsUpCount", 0) or 0),
                        created_at=str(row.get("at", "")),
                    )
                )
                if len(items) >= max_reviews:
                    break
            if token is None:
                break
    except Exception as exc:
        raise FetchError(f"فشل جلب مراجعات Google Play: {exc}") from exc

    if not items:
        raise FetchError("لم تُعثر على مراجعات — تحقق من package id أو اللغة/البلد.")
    return items


def _flatten_reddit_comments(node: Any, out: List[FetchedComment], post_id: str, limit: int) -> None:
    if len(out) >= limit or not isinstance(node, dict):
        return
    data = node.get("data") or {}
    body = _clean_text(data.get("body", ""))
    if body and body not in ("[deleted]", "[removed]"):
        out.append(
            FetchedComment(
                text=body,
                author=str(data.get("author", "")),
                source="reddit",
                source_id=post_id,
                likes=int(data.get("ups", 0) or 0),
                created_at=str(data.get("created_utc", "")),
            )
        )
    replies = (data.get("replies") or {}).get("data", {}).get("children") or []
    for child in replies:
        if len(out) >= limit:
            break
        _flatten_reddit_comments(child, out, post_id, limit)


def fetch_reddit_comments(url: str, max_comments: int = 500) -> List[FetchedComment]:
    try:
        import requests
    except ImportError as exc:
        raise FetchDependencyError("ثبّت الحزمة: pip install requests") from exc

    json_url = extract_reddit_post_url(url)
    post_id = REDDIT_RE.search(url).group(1)
    headers = {"User-Agent": "sentiment-graduation-project/1.0 (education)"}

    try:
        response = requests.get(json_url, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise FetchError(f"فشل جلب تعليقات Reddit: {exc}") from exc

    items: List[FetchedComment] = []
    if isinstance(payload, list) and len(payload) >= 2:
        comments_listing = payload[1].get("data", {}).get("children", [])
        for child in comments_listing:
            _flatten_reddit_comments(child, items, post_id, max_comments)
            if len(items) >= max_comments:
                break

    if not items:
        raise FetchError("لم يُعثر على تعليقات — تأكد أن المنشور عاماً.")
    return items


def fetch_comments(
    url_or_id: str,
    source: SourceKind = "auto",
    max_items: int = 500,
    *,
    play_lang: str = "ar",
    play_country: str = "sa",
) -> tuple[List[FetchedComment], str]:
    """Return (comments, resolved_source)."""
    resolved = detect_source(url_or_id) if source == "auto" else source
    if resolved == "youtube":
        return fetch_youtube_comments(url_or_id, max_comments=max_items), "youtube"
    if resolved == "google_play":
        return (
            fetch_google_play_reviews(
                url_or_id,
                max_reviews=max_items,
                lang=play_lang,
                country=play_country,
            ),
            "google_play",
        )
    if resolved == "reddit":
        return fetch_reddit_comments(url_or_id, max_comments=max_items), "reddit"
    raise FetchError(f"مصدر غير مدعوم: {resolved}")


def comments_to_texts(comments: List[FetchedComment]) -> List[str]:
    return [item.text for item in comments if item.text.strip()]


def save_fetched_csv(comments: List[FetchedComment], path: str) -> str:
    import pandas as pd

    df = pd.DataFrame([item.to_dict() for item in comments])
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path
