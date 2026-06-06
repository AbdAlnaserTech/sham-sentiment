from preprocessing import TextPreprocessor


def test_preprocess_english_removes_stopwords():
    pre = TextPreprocessor(remove_stopwords=True)
    result = pre.preprocess("The product is great", language="en")
    assert "the" not in result.tokens
    assert "product" in result.tokens


def test_preprocess_arabic_normalization():
    pre = TextPreprocessor(remove_stopwords=False)
    result = pre.preprocess("المنتج ممتاز", language="ar_fusha")
    assert result.language == "ar_fusha"
    assert result.cleaned_text


def test_preprocess_emoji_token():
    pre = TextPreprocessor(remove_stopwords=False, min_token_len=1)
    result = pre.preprocess("Great 😊", language="en")
    assert "emoji_pos" in result.tokens


def test_preprocess_empty_text():
    pre = TextPreprocessor()
    result = pre.preprocess("", language="en")
    assert result.cleaned_text == ""
