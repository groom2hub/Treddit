from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db

from . import chatgpt
from . import naver_news_search
from . import google_trends
from . import naver_keyword_count
from . import naver_keyword_estimate
from . import naver_contents_search
from . import news_keywords
from . import realtime_searchwords
from . import topic_trends
from . import naver_encyclopedia

router = APIRouter(
     prefix='/service'
)

@router.post("/chatgpt")
def ask_question(data: chatgpt.Conversation):
    return chatgpt.get_answer(data)

@router.post("/navernews")
def search(searchWord: naver_news_search.SearchWord):
    return naver_news_search.search_news(searchWord.content, searchWord.page, searchWord.page2)

@router.get("/googletrends")
def read_google_trends():
    return google_trends.get_trends()

@router.post("/keywordcount")
def get_keyword_count(keyword: naver_keyword_count.Keyword):
    return naver_keyword_count.get_results(keyword.content)

@router.post("/searchdata")
def get_search_data(keyword: naver_keyword_estimate.Keyword):
    return naver_keyword_estimate.get_search_data(keyword.content)

@router.post("/trendnews")
def get_trend_news(searchWord: naver_news_search.SearchWord):
    return naver_news_search.get_trend_news(searchWord.content, searchWord.page, searchWord.page2)

@router.post("/contents")
def get_naver_contents(searchWord: naver_contents_search.SearchWord):
    return naver_contents_search.search_naver_contents(searchWord.content)

@router.get("/newskeywords")
def get_news_keywords(days: int = Query(50, ge=1, le=365), db: Session = Depends(get_db)):
    return news_keywords.get_news_keywords(db, days)

@router.get("/realtimesearchwords")
def get_realtime_searchwords():
    return realtime_searchwords.get_realtime_searchwords()

@router.get("/topictrends")
def get_topic_trends(days: int = Query(50, ge=1, le=365), db: Session = Depends(get_db)):
    return topic_trends.get_topic_trends(db, days)

@router.get("/wordcloud")
def get_word_cloud():
    return google_trends.get_trends_search()

@router.get("/titles")
def get_titles():
    return google_trends.get_trends_list()

@router.get("/definition")
def get_definition(keyword: str):
    return naver_encyclopedia.get_definition(keyword)
