"""Treddit 데이터 파이프라인.

    python -m pipeline run [--date YYYYMMDD] [--skip-crawl]
    python -m pipeline import-csv <outputs 디렉터리>
"""
import argparse
import csv
import datetime
import logging
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select

from pipeline import analysis, crawler
from pipeline.config import settings
from pipeline.db import Article, DailyKeyword, SessionLocal, TopicTrend

log = logging.getLogger("pipeline")
KST = ZoneInfo("Asia/Seoul")


def parse_date(value: str) -> datetime.date:
    return datetime.datetime.strptime(value, "%Y%m%d").date()


def yesterday_kst() -> datetime.date:
    return datetime.datetime.now(KST).date() - datetime.timedelta(days=1)


def save_results(session, date, keywords, trends):
    """해당 날짜의 결과를 교체한다. 같은 날짜로 다시 실행해도 중복되지 않는다."""
    session.execute(delete(DailyKeyword).where(DailyKeyword.keyword_date == date))
    session.execute(delete(TopicTrend).where(TopicTrend.trend_date == date))
    session.add_all(
        DailyKeyword(keyword_date=date, word=word, count=count, rank=rank)
        for rank, (word, count) in enumerate(keywords, start=1)
    )
    session.add_all(
        TopicTrend(trend_date=date, topic=topic, frequency=frequency, rank=rank)
        for rank, (topic, frequency) in enumerate(trends, start=1)
    )


def run(date: datetime.date, skip_crawl: bool):
    with SessionLocal() as session:
        if not skip_crawl:
            # 기사는 여러 날짜 목록에 걸쳐 나올 수 있으므로 날짜 구분 없이 저장된 URL을 모두 건너뛴다
            skip_urls = set(session.scalars(select(Article.url)))
            log.info("%s 크롤링 시작 (저장된 기사 %d건 건너뜀)", date, len(skip_urls))
            total = 0
            # 섹션 단위로 커밋해, 중간에 실패해도 그때까지 수집한 기사는 남긴다
            for batch in crawler.crawl(date, skip_urls):
                session.add_all(
                    Article(
                        article_date=date,
                        section_code=a.section_code,
                        detail_section_code=a.detail_section_code,
                        title=a.title[:500],
                        content=a.content,
                        url=a.url,
                        published_at=a.published_at,
                    )
                    for a in batch
                )
                session.commit()
                total += len(batch)
            log.info("신규 기사 %d건 저장", total)

        contents = session.scalars(select(Article.content).where(Article.article_date == date)).all()
        if not contents:
            log.warning("%s 기사가 없어 분석을 건너뜀", date)
            return

        log.info("기사 %d건 전처리", len(contents))
        documents = [analysis.extract_nouns(content) for content in contents]

        keywords = analysis.top_keywords(documents, settings.top_keywords)
        log.info("LDA 토픽 모델링 (토픽 %d개)", settings.num_topics)
        trends = analysis.topic_trends(documents, settings.num_topics)

        save_results(session, date, keywords, trends)
        session.commit()
        log.info("완료: 키워드 %d개, 토픽 트렌드 %d개", len(keywords), len(trends))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def import_csv(outputs_dir: Path):
    """KbyC 시절의 outputs/{YYYYMMDD}/*.csv 결과를 DB로 옮긴다."""
    with SessionLocal() as session:
        for date_dir in sorted(p for p in outputs_dir.iterdir() if p.is_dir()):
            date = parse_date(date_dir.name)
            documents_csv = date_dir / "documents.csv"
            trends_csv = date_dir / "topic_trends.csv"

            keywords = []
            if documents_csv.exists():
                documents = [row["document"].split() for row in read_csv(documents_csv)]
                keywords = analysis.top_keywords(documents, settings.top_keywords)

            trends = {}
            if trends_csv.exists():
                for row in read_csv(trends_csv):
                    trends.setdefault(row["Topic"], int(row["Frequency"]))
            trends = sorted(trends.items(), key=lambda item: item[1], reverse=True)

            save_results(session, date, keywords, trends)
            log.info("%s: 키워드 %d개, 토픽 트렌드 %d개", date, len(keywords), len(trends))
        session.commit()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("gensim").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(prog="pipeline")
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="기사 수집부터 트렌드 분석까지 실행")
    run_parser.add_argument("--date", type=parse_date, default=None, help="YYYYMMDD (기본: 어제, KST)")
    run_parser.add_argument("--skip-crawl", action="store_true", help="DB에 저장된 기사로 분석만 다시 실행")

    import_parser = commands.add_parser("import-csv", help="기존 CSV 결과를 DB로 이관")
    import_parser.add_argument("outputs_dir", type=Path)

    args = parser.parse_args()

    if args.command == "run":
        run(args.date or yesterday_kst(), args.skip_crawl)
    elif args.command == "import-csv":
        import_csv(args.outputs_dir)


if __name__ == "__main__":
    main()
