from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_name = Column(String(50), unique=True, nullable=False)
    user_password = Column(String(100), nullable=False)
    user_email = Column(String(50), unique=True, index=True, nullable=False)
    user_status = Column(String(50))
    created_at = Column(DateTime, nullable=False)
    last_connected_at = Column(DateTime)

    posts = relationship('Post', back_populates='writer')
    comments = relationship('Comment', back_populates='writer')

class Post(Base):
    __tablename__ = 'post'

    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    title = Column(String(50), index=True, nullable=False)
    content = Column(Text, nullable=False)
    post_date = Column(DateTime, nullable=False)
    writer_email = Column(String(50), ForeignKey('user.user_email'), nullable=False)
    writer_name = Column(String(50), nullable=False)
    tag = Column(String(50))

    writer = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')

class Comment(Base):
    __tablename__ = 'comment'

    comment_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    content = Column(Text, nullable=False)
    comment_date = Column(DateTime, nullable=False)
    writer_email = Column(String(50), ForeignKey('user.user_email'), nullable=False)
    writer_name = Column(String(50), nullable=False)
    post_id = Column(Integer, ForeignKey('post.post_id'), nullable=False)

    writer = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')

class Google_Keyword(Base):
    __tablename__ = 'google_keyword'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String(50), nullable=False)
    count = Column(Integer, nullable=False)

class Realtime_Keyword(Base):
    __tablename__ = 'realtime_keyword'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String(50), nullable=False)
    count = Column(Integer, nullable=False)


# 아래 테이블은 데이터 파이프라인(pipeline/pipeline/db.py)이 채운다. 스키마를 함께 맞춰야 한다.
class Article(Base):
    __tablename__ = 'article'

    article_id = Column(Integer, primary_key=True, autoincrement=True)
    article_date = Column(Date, nullable=False, index=True)
    section_code = Column(String(10), nullable=False)
    detail_section_code = Column(String(10), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text().with_variant(MEDIUMTEXT(), 'mysql'), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    published_at = Column(DateTime)

class DailyKeyword(Base):
    __tablename__ = 'daily_keyword'
    __table_args__ = (UniqueConstraint('keyword_date', 'word'),)

    daily_keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_date = Column(Date, nullable=False, index=True)
    word = Column(String(100), nullable=False)
    count = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)

class TopicTrend(Base):
    __tablename__ = 'topic_trend'
    __table_args__ = (UniqueConstraint('trend_date', 'topic'),)

    topic_trend_id = Column(Integer, primary_key=True, autoincrement=True)
    trend_date = Column(Date, nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    frequency = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)
