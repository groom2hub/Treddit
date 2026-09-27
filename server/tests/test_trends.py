import datetime

import pytest

from models import DailyKeyword, TopicTrend

DATES = [datetime.date(2026, 9, 24), datetime.date(2026, 9, 25), datetime.date(2026, 9, 26)]


@pytest.fixture
def seeded(db):
    for date in DATES:
        db.add_all([
            TopicTrend(trend_date=date, topic="미국", frequency=20, rank=1),
            TopicTrend(trend_date=date, topic="한국", frequency=10, rank=2),
            DailyKeyword(keyword_date=date, word="서울", count=30, rank=1),
            DailyKeyword(keyword_date=date, word="정부", count=5, rank=2),
        ])
    db.commit()


def test_topic_trends_recent_days_oldest_first(client, seeded):
    trends = client.get("/api/service/topictrends?days=2").json()["topic_trends"]
    assert [t["date"] for t in trends] == ["20260925", "20260926"]
    assert trends[-1]["words"] == [{"topic": "미국", "frequency": 20}, {"topic": "한국", "frequency": 10}]


def test_news_keywords(client, seeded):
    body = client.get("/api/service/newskeywords").json()
    assert body["search_dates"] == ["20260924", "20260925", "20260926"]
    assert body["news_keywords"][0]["words"][0] == {"word": "서울", "count": 30}


def test_trends_empty_db(client):
    assert client.get("/api/service/topictrends").json() == {"topic_trends": []}


def test_days_validation(client):
    assert client.get("/api/service/topictrends?days=0").status_code == 422
