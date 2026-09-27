from pipeline import analysis


def test_clean_text():
    text = "[서울=연합뉴스] 홍길동 기자(hong@yna.co.kr) = 반도체 수출이 증가했다!"
    cleaned = analysis.clean_text(text)
    assert "연합뉴스" not in cleaned
    assert "@" not in cleaned
    assert "!" not in cleaned
    assert "반도체 수출이 증가했다" in cleaned


def test_extract_nouns_filters_single_chars_and_stopwords():
    nouns = analysis.extract_nouns("정부는 반도체 산업에 대한 투자를 늘린다고 밝혔다.")
    assert "반도체" in nouns
    assert "투자" in nouns
    assert all(len(noun) > 1 for noun in nouns)
    assert not set(nouns) & analysis.stopwords()


def test_top_keywords():
    documents = [["반도체", "수출"], ["반도체", "정부"], ["반도체", "수출"]]
    assert analysis.top_keywords(documents, 2) == [("반도체", 3), ("수출", 2)]


def test_topic_trends_sorted_and_unique():
    documents = [["반도체", "수출", "증가"], ["반도체", "투자"], ["선거", "후보", "투표"], ["선거", "후보"]] * 5
    trends = analysis.topic_trends(documents, num_topics=2)

    words = [word for word, _ in trends]
    frequencies = [freq for _, freq in trends]
    assert len(words) == len(set(words))
    assert frequencies == sorted(frequencies, reverse=True)
    assert set(words) <= {"반도체", "수출", "증가", "투자", "선거", "후보", "투표"}


def test_topic_trends_empty():
    assert analysis.topic_trends([[], []], num_topics=5) == []
