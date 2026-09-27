import datetime

from sqlalchemy import func, select

from pipeline import __main__ as cli
from pipeline.db import Article, DailyKeyword, TopicTrend

DATE = datetime.date(2026, 9, 26)


def count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_save_results_is_idempotent(session):
    cli.save_results(session, DATE, [("반도체", 3), ("수출", 2)], [("반도체", 3)])
    session.commit()
    cli.save_results(session, DATE, [("정부", 5)], [("정부", 5)])
    session.commit()

    assert count(session, DailyKeyword) == 1
    assert session.scalars(select(TopicTrend.topic)).all() == ["정부"]


def test_run_skip_crawl_analyzes_saved_articles(session, monkeypatch):
    monkeypatch.setattr(cli, "SessionLocal", lambda: session)
    monkeypatch.setattr(cli.settings, "num_topics", 2)
    session.add_all(
        Article(article_date=DATE, section_code="105", detail_section_code="230",
                title=f"기사{i}", content="정부가 반도체 산업 투자를 확대한다", url=f"https://example.com/{i}")
        for i in range(3)
    )
    session.commit()

    cli.run(DATE, skip_crawl=True)

    keywords = session.scalars(select(DailyKeyword).order_by(DailyKeyword.rank)).all()
    assert keywords[0].keyword_date == DATE
    assert keywords[0].count == 3
    assert count(session, TopicTrend) > 0


def test_import_csv(session, monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "SessionLocal", lambda: session)
    day = tmp_path / "20240919"
    day.mkdir()
    (day / "documents.csv").write_text("﻿document\n서울 한국 서울\n서울 정부\n", encoding="utf-8")
    # 원본 CSV에는 같은 토픽이 중복으로 들어 있는 경우가 있다
    (day / "topic_trends.csv").write_text("﻿Topic,Frequency\n서울,1118\n한국,939\n서울,1118\n", encoding="utf-8")

    cli.import_csv(tmp_path)

    date = datetime.date(2024, 9, 19)
    keywords = session.scalars(select(DailyKeyword).where(DailyKeyword.keyword_date == date).order_by(DailyKeyword.rank)).all()
    assert [(k.word, k.count) for k in keywords] == [("서울", 3), ("한국", 1), ("정부", 1)]
    trends = session.scalars(select(TopicTrend).order_by(TopicTrend.rank)).all()
    assert [(t.topic, t.frequency) for t in trends] == [("서울", 1118), ("한국", 939)]
