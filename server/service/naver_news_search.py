from collections import Counter
from email.utils import parsedate_to_datetime

from pydantic import BaseModel

from nlp import okt
from . import naver_openapi

PAGE_SIZE = 10


class SearchWord(BaseModel):
    content: str
    page: int
    page2: int


def fetch_news(keyword: str, page: int, page2: int) -> list[dict]:
    """네이버 뉴스 검색 API로 page ~ page2 페이지(페이지당 10건)의 기사를 가져온다."""
    news = []
    for p in range(max(page, 1), max(page, page2) + 1):
        items = naver_openapi.search("news", keyword, display=PAGE_SIZE, start=(p - 1) * PAGE_SIZE + 1, sort="sim")
        for item in items:
            news.append({
                "date": parsedate_to_datetime(item["pubDate"]).strftime("%Y-%m-%d %H:%M:%S"),
                "title": naver_openapi.strip_tags(item["title"]),
                "link": item["link"],
                "content": naver_openapi.strip_tags(item["description"]),
            })
        if len(items) < PAGE_SIZE:
            break
    return news


def search_news(searchWord: str, page: int, page2: int):
    return {"news": fetch_news(searchWord, page, page2)}


def get_trend_news(searchWord: str, page: int, page2: int):
    """키워드 관련 뉴스와, 뉴스 제목에 자주 나온 명사 상위 10개를 반환한다."""
    news = fetch_news(searchWord, page, page2)

    nouns = [noun for item in news for noun in okt().nouns(item["title"]) if len(noun) > 1]
    top_10 = Counter(nouns).most_common(10)

    return {
        "news": [{"link": item["link"], "title": item["title"]} for item in news[:10]],
        "top_10_words": [word for word, _ in top_10],
        "words_count": top_10,
    }
