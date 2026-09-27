"""파이프라인이 쓰는 테이블 정의.

server/models.py의 Article, DailyKeyword, TopicTrend와 같은 스키마를 유지해야 한다.
"""
from sqlalchemy import Column, Date, DateTime, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import declarative_base, sessionmaker

from pipeline.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Article(Base):
    __tablename__ = "article"

    article_id = Column(Integer, primary_key=True, autoincrement=True)
    article_date = Column(Date, nullable=False, index=True)
    section_code = Column(String(10), nullable=False)
    detail_section_code = Column(String(10), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    published_at = Column(DateTime)


class DailyKeyword(Base):
    __tablename__ = "daily_keyword"
    __table_args__ = (UniqueConstraint("keyword_date", "word"),)

    daily_keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_date = Column(Date, nullable=False, index=True)
    word = Column(String(100), nullable=False)
    count = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)


class TopicTrend(Base):
    __tablename__ = "topic_trend"
    __table_args__ = (UniqueConstraint("trend_date", "topic"),)

    topic_trend_id = Column(Integer, primary_key=True, autoincrement=True)
    trend_date = Column(Date, nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    frequency = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)
