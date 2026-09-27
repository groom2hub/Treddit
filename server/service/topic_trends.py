from sqlalchemy import select
from sqlalchemy.orm import Session

from models import TopicTrend


def get_topic_trends(db: Session, days: int):
    """최근 days일의 토픽 트렌드를 오래된 날짜부터 반환한다."""
    dates = db.scalars(
        select(TopicTrend.trend_date).distinct().order_by(TopicTrend.trend_date.desc()).limit(days)
    ).all()
    rows = db.scalars(
        select(TopicTrend).where(TopicTrend.trend_date.in_(dates)).order_by(TopicTrend.trend_date, TopicTrend.rank)
    ).all()

    data = {}
    for row in rows:
        data.setdefault(row.trend_date.strftime('%Y%m%d'), []).append({'topic': row.topic, 'frequency': row.frequency})

    return {'topic_trends': [{'date': date, 'words': words} for date, words in data.items()]}
