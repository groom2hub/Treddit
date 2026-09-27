import pytest

from service import naver_openapi

SAMPLE = [
    {"title": "<b>AI</b> 반도체 수출 &quot;역대 최대&quot;", "link": "https://n.news.naver.com/a/1",
     "description": "<b>AI</b> 반도체 수요", "pubDate": "Sat, 26 Sep 2026 14:44:00 +0900"},
    {"title": "정부, <b>AI</b> 반도체 투자", "link": "https://n.news.naver.com/a/2",
     "description": "투자 확대", "pubDate": "Sat, 26 Sep 2026 10:00:00 +0900"},
]


@pytest.fixture
def fake_search(monkeypatch):
    calls = []

    def search(kind, query, **params):
        calls.append((kind, query, params))
        return SAMPLE

    monkeypatch.setattr(naver_openapi, "search", search)
    return calls


def test_strip_tags():
    assert naver_openapi.strip_tags("<b>AI</b> &quot;최대&quot; &amp; 성장") == 'AI "최대" & 성장'


def test_missing_keys_returns_503(client):
    response = client.get("/api/service/definition?keyword=AI")
    assert response.status_code == 503


def test_navernews(client, fake_search):
    body = client.post("/api/service/navernews", json={"content": "AI", "page": 1, "page2": 1}).json()
    assert body["news"][0] == {
        "date": "2026-09-26 14:44:00",
        "title": 'AI 반도체 수출 "역대 최대"',
        "link": "https://n.news.naver.com/a/1",
        "content": "AI 반도체 수요",
    }
    assert fake_search[0] == ("news", "AI", {"display": 10, "start": 1, "sort": "sim"})


def test_trendnews_top_words(client, fake_search):
    body = client.post("/api/service/trendnews", json={"content": "AI", "page": 1, "page2": 1}).json()
    assert body["top_10_words"][0] == "반도체"
    assert body["news"][1] == {"link": "https://n.news.naver.com/a/2", "title": "정부, AI 반도체 투자"}


def test_definition(client, fake_search):
    body = client.get("/api/service/definition?keyword=AI").json()
    assert body == {"definition": "AI 반도체 수요"}
