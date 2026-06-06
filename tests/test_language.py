from language import detect_language, is_arabic, normalize_arabic, safe_percent


def test_detect_english():
    assert detect_language("This product is great") == "en"


def test_detect_fusha():
    assert detect_language("المنتج ممتاز جدا") == "ar_fusha"


def test_detect_shami():
    assert detect_language("الخدمة كتير منيح") == "ar_shami"


def test_normalize_arabic():
    assert "ا" in normalize_arabic("إأآا")


def test_is_arabic():
    assert is_arabic("مرحبا")
    assert not is_arabic("hello")


def test_safe_percent_bounds():
    assert safe_percent(-5) == 0.0
    assert safe_percent(150) == 100.0
    assert safe_percent(42.5) == 42.5
