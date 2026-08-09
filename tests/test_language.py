"""اختبارات كشف اللغة والتطبيع العربي — language.py."""

from language import detect_language, is_arabic, normalize_arabic, safe_percent


def test_detect_english():
    """كشف نص إنجليزي."""
    assert detect_language("This product is great") == "en"


def test_detect_fusha():
    """كشف العربية الفصحى."""
    assert detect_language("المنتج ممتاز جدا") == "ar_fusha"


def test_detect_shami():
    """كشف اللهجة الشامية."""
    assert detect_language("الخدمة كتير منيح") == "ar_shami"


def test_normalize_arabic():
    """تطبيع أشكال الألف (إأآا → ا)."""
    assert "ا" in normalize_arabic("إأآا")


def test_is_arabic():
    """تمييز النص العربي عن الإنجليزي."""
    assert is_arabic("مرحبا")
    assert not is_arabic("hello")


def test_safe_percent_bounds():
    """تقييد النسبة المئوية بين 0 و 100."""
    assert safe_percent(-5) == 0.0
    assert safe_percent(150) == 100.0
    assert safe_percent(42.5) == 42.5
