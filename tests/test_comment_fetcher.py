"""اختبارات تحليل روابط/معرّفات التعليقات (بدون شبكة)."""

import pytest

from data.comment_fetcher import (
    FetchError,
    detect_source,
    extract_google_play_id,
    extract_reddit_post_url,
    extract_youtube_video_id,
)


def test_detect_youtube_url():
    """كشف مصدر YouTube من رابط watch."""
    assert detect_source("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"


def test_detect_play_package():
    """كشف Google Play من معرّف الحزمة."""
    assert detect_source("com.whatsapp") == "google_play"


def test_detect_reddit():
    """كشف Reddit من رابط المنشور."""
    assert detect_source("https://www.reddit.com/r/python/comments/abc123/title/") == "reddit"


def test_youtube_id_short():
    """استخراج معرّف فيديو YouTube من نص قصير."""
    assert extract_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_play_id_from_url():
    """استخراج معرّف تطبيق من رابط Google Play."""
    url = "https://play.google.com/store/apps/details?id=com.whatsapp&hl=ar"
    assert extract_google_play_id(url) == "com.whatsapp"


def test_play_id_from_whatsapp_site():
    """تحويل whatsapp.com إلى com.whatsapp."""
    assert extract_google_play_id("https://www.whatsapp.com/") == "com.whatsapp"


def test_invalid_youtube():
    """رفض نص غير صالح كمعرّف YouTube."""
    with pytest.raises(FetchError):
        extract_youtube_video_id("not-a-url")


def test_reddit_placeholder_rejected():
    """رفض روابط Reddit ذات placeholder (xxxxx)."""
    with pytest.raises(FetchError):
        extract_reddit_post_url(
            "https://www.reddit.com/r/technology/comments/xxxxx/some_post_title/"
        )


def test_reddit_example_from_docs_rejected():
    """رفض مثال Reddit من التوثيق (1abc2de placeholder)."""
    with pytest.raises(FetchError):
        extract_reddit_post_url(
            "https://www.reddit.com/r/technology/comments/1abc2de/post_title_here/"
        )


def test_reddit_valid_url():
    """استخراج subreddit و post_id من رابط Reddit صالح."""
    json_url, sub, post_id = extract_reddit_post_url(
        "https://www.reddit.com/r/python/comments/abc12345/what_are_you_working_on/"
    )
    assert sub == "python"
    assert post_id == "abc12345"
    assert "old.reddit.com/r/python/comments/abc12345/.json" in json_url
