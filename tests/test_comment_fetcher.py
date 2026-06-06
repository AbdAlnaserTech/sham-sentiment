"""Tests for comment URL/id parsing (no network)."""

import pytest

from data.comment_fetcher import (
    FetchError,
    detect_source,
    extract_google_play_id,
    extract_youtube_video_id,
)


def test_detect_youtube_url():
    assert detect_source("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"


def test_detect_play_package():
    assert detect_source("com.whatsapp") == "google_play"


def test_detect_reddit():
    assert detect_source("https://www.reddit.com/r/python/comments/abc123/title/") == "reddit"


def test_youtube_id_short():
    assert extract_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_play_id_from_url():
    url = "https://play.google.com/store/apps/details?id=com.whatsapp&hl=ar"
    assert extract_google_play_id(url) == "com.whatsapp"


def test_invalid_youtube():
    with pytest.raises(FetchError):
        extract_youtube_video_id("not-a-url")
