from sqlalchemy import select
from sqlalchemy.orm import Session

from models import DailyKeyword


def get_news_keywords(db: Session, days: int):
    """최근 days일의 뉴스 키워드를 오래된 날짜부터 반환한다."""
    dates = db.scalars(
        select(DailyKeyword.keyword_date).distinct().order_by(DailyKeyword.keyword_date.desc()).limit(days)
    ).all()
    rows = db.scalars(
        select(DailyKeyword).where(DailyKeyword.keyword_date.in_(dates)).order_by(DailyKeyword.keyword_date, DailyKeyword.rank)
    ).all()

    data = {}
    for row in rows:
        data.setdefault(row.keyword_date.strftime('%Y%m%d'), []).append({'word': row.word, 'count': row.count})

    return {
        'news_keywords': [{'date': date, 'words': words} for date, words in data.items()],
        'search_dates': list(data),
    }
