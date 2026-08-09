"""
جلب تعليقات حقيقية من الإنternet.

المصادر:
  - YouTube  (youtube-comment-downloader)
  - Google Play (google-play-scraper)
  - Reddit (requests + JSON) — موجود في الكود؛ الواجهة تستخدم YouTube/Play فقط

الواجهة تستدعي: fetch_comments() من app/tabs/live.py
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal

# ── بلوك: أنواع المصادر ─────────────────────────────────────────────────────
SourceKind = Literal["youtube", "google_play", "reddit", "auto"]

# ── بلوك: Regex لاستخراج المعرّفات من الروابط ─────────────────────────────
YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
PLAY_ID_RE = re.compile(r"[?&]id=([A-Za-z0-9._]+)")
REDDIT_RE = re.compile(r"reddit\.com/r/([^/]+)/comments/([A-Za-z0-9]+)", re.I)

# ── بلوك: روابط وهمية/أمثلة — نرفضها برسالة واضحة ─────────────────────────
REDDIT_PLACEHOLDER_IDS = frozenset({"xxxxx", "id", "post_id", "postid", "abc", "123", "title", "1abc2de"})
REDDIT_PLACEHOLDER_SLUGS = frozenset({"post_title_here", "some_post_title", "example_title", "title"})


@dataclass
class FetchedComment:
    """شكل موحّد لتعليق مجلوب — يُحوّل لاحقاً لقائمة نصوص للتحليل."""
    text: str
    author: str = ""
    source: str = ""
    source_id: str = ""
    likes: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى dict — للحفظ في CSV."""
        return asdict(self)


class FetchError(Exception):
    """خطأ في الرابط أو الجلب — يُعرض للمستخدم بالعربية."""


class FetchDependencyError(FetchError):
    """مكتبة خارجية غير مثبتة (pip install ...)."""


def _looks_like_package_id(raw: str) -> bool:
    """التحقق إن كان الإدخال package id لـ Google Play (مثل com.whatsapp)."""
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]+)+$", raw))


def detect_source(url_or_id: str) -> SourceKind:
    """
    يحدد المصدر تلقائياً من الرابط أو المعرّف.
    يرفع FetchError إذا لم يُفهم الإدخال.
    """
    raw = (url_or_id or "").strip()
    lower = raw.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return "youtube"
    if "play.google.com" in lower or _looks_like_package_id(raw):
        return "google_play"
    if "reddit.com" in lower:
        return "reddit"
    if re.match(r"^[A-Za-z0-9_-]{11}$", raw):
        return "youtube"  # video id مباشر (11 حرف)
    raise FetchError(
        "تعذّر التعرف على المصدر. استخدم رابط YouTube أو Google Play أو Reddit، "
        "أو package id مثل com.whatsapp"
    )


def extract_youtube_video_id(url_or_id: str) -> str:
    """يستخرج VIDEO_ID (11 حرف) من رابط YouTube أو من id مباشر."""
    raw = (url_or_id or "").strip()
    match = YOUTUBE_ID_RE.search(raw)
    if match:
        return match.group(1)
    if re.match(r"^[A-Za-z0-9_-]{11}$", raw):
        return raw
    raise FetchError("رابط YouTube غير صالح. مثال: https://www.youtube.com/watch?v=VIDEO_ID")


def extract_google_play_id(url_or_id: str) -> str:
    """يستخرج package id من رابط Play أو من com.xxx مباشر."""
    raw = (url_or_id or "").strip()
    match = PLAY_ID_RE.search(raw)
    if match:
        return match.group(1)
    if re.match(r"^[A-Za-z][A-Za-z0-9._]*$", raw):
        return raw
    raise FetchError(
        "معرّف التطبيق غير صالح. مثال: com.whatsapp أو رابط Google Play كامل"
    )


def extract_reddit_post_url(url: str) -> tuple[str, str, str]:
    """
    يبني رابط JSON لـ Reddit.
    يرجع: (json_url, subreddit, post_id)
    """
    raw = (url or "").strip().rstrip("/")
    match = REDDIT_RE.search(raw)
    if not match:
        raise FetchError(
            "رابط Reddit غير صالح. افتح منشوراً على Reddit ثم انسخ الرابط من المتصفح."
        )
    subreddit, post_id = match.group(1), match.group(2).lower()
    slug = raw.split(f"/comments/{match.group(2)}/")[-1].split("/")[0].split("?")[0].lower()
    # ── رفض روابط الأمثلة الوهمية ──
    if post_id in REDDIT_PLACEHOLDER_IDS or slug in REDDIT_PLACEHOLDER_SLUGS or len(post_id) < 5:
        raise FetchError(
            "الرابط يبدو مثالاً وليس منشوراً حقيقياً. "
            "افتح Reddit، اختر منشوراً، وانسخ رابطه الكامل."
        )
    json_url = (
        f"https://old.reddit.com/r/{subreddit}/comments/{post_id}/.json"
        f"?limit=500&raw_json=1"
    )
    return json_url, subreddit, post_id


def _reddit_request_headers() -> Dict[str, str]:
    """رأس طلب يشبه المتصفح — Reddit يرفض bots بدون User-Agent."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }


def _reddit_fetch_error(status_code: int) -> FetchError:
    """رسائل عربية بدل أخطاء HTTP خام."""
    if status_code == 404:
        return FetchError("المنشور غير موجود — تحقق أن الرابط صحيحاً.")
    if status_code == 403:
        return FetchError(
            "تعذّر الوصول إلى Reddit من هذا الجهاز. "
            "جرّب رابط منشور آخر، أو استخدم YouTube / Google Play."
        )
    if status_code == 429:
        return FetchError("طلبات كثيرة — انتظر دقيقة ثم أعد المحاولة.")
    return FetchError("تعذّر جلب التعليقات — تحقق من الرابط أو جرّب مصدراً آخر.")


def _clean_text(text: str) -> str:
    """إزالة مسافات زائدة وتطبيع سطر التعليق."""
    return " ".join(str(text or "").split()).strip()


def fetch_youtube_comments(
    url_or_id: str,
    max_comments: int = 500,
) -> List[FetchedComment]:
    """يجلب تعليقات فيديو YouTube واحد عبر youtube-comment-downloader."""
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
    """
    يجلب مراجعات تطبيق من Google Play.
    lang/country يحددان لغة وبلد المراجعات (ar/sa للعربية السعودية).
    """
    try:
        from google_play_scraper import Sort, reviews
    except ImportError as exc:
        raise FetchDependencyError(
            "ثبّت الحزمة: pip install google-play-scraper"
        ) from exc

    app_id = extract_google_play_id(url_or_id)
    items: List[FetchedComment] = []
    token = None  # رمز pagination للدفعات التالية

    try:
        # ── جلب على دفعات (حتى 200 لكل طلب) ──
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
    """يمرّ على شجرة ردود Reddit JSON ويجمع النصوص (recursive)."""
    if len(out) >= limit or not isinstance(node, dict):
        return
    data = node.get("data") or {}
    body = _clean_text(data.get("body", ""))
    # ── تخطّي التعليقات المحذوفة ──
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
    """يجلب تعليقات منشور Reddit عبر JSON API (old.reddit.com)."""
    try:
        import requests
    except ImportError as exc:
        raise FetchDependencyError("ثبّت الحزمة: pip install requests") from exc

    json_url, _subreddit, post_id = extract_reddit_post_url(url)
    headers = _reddit_request_headers()
    fallback_url = json_url.replace("old.reddit.com", "www.reddit.com")

    try:
        response = requests.get(json_url, headers=headers, timeout=30)
        # ── fallback إلى www إذا فشل old ──
        if response.status_code in (403, 404) and "old.reddit.com" in json_url:
            response = requests.get(fallback_url, headers=headers, timeout=30)
        if response.status_code >= 400:
            raise _reddit_fetch_error(response.status_code)
        payload = response.json()
    except FetchError:
        raise
    except requests.RequestException as exc:
        raise FetchError("تعذّر الاتصال بـ Reddit. تحقق من الإنترنت والرابط.") from exc
    except ValueError as exc:
        raise FetchError("استجابة Reddit غير متوقعة — جرّب رابطاً آخر.") from exc

    items: List[FetchedComment] = []
    # payload[0] = المنشور، payload[1] = قائمة التعليقات
    if isinstance(payload, list) and len(payload) >= 2:
        comments_listing = payload[1].get("data", {}).get("children", [])
        for child in comments_listing:
            _flatten_reddit_comments(child, items, post_id, max_comments)
            if len(items) >= max_comments:
                break

    if not items:
        raise FetchError("لم يُعثر على تعليقات — تأكد أن المنشور عاماً ويحتوي رداً.")
    return items


def fetch_comments(
    url_or_id: str,
    source: SourceKind = "auto",
    max_items: int = 500,
    *,
    play_lang: str = "ar",
    play_country: str = "sa",
) -> tuple[List[FetchedComment], str]:
    """
    نقطة الدخول الرئيسية — تُستدعى من الواجهة.
    يرجع: (قائمة تعليقات، اسم المصدر الفعلي)
    """
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
    """يحوّل FetchedComment[] إلى list[str] للتحليل."""
    return [item.text for item in comments if item.text.strip()]


def save_fetched_csv(comments: List[FetchedComment], path: str) -> str:
    """حفظ التعليقات المجلوبة لملف CSV (للسكربتات CLI)."""
    import pandas as pd

    df = pd.DataFrame([item.to_dict() for item in comments])
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path
