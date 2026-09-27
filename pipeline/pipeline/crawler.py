"""네이버 뉴스 섹션별 속보 목록에서 기사를 수집한다."""
import datetime
import logging
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.config import settings

log = logging.getLogger(__name__)

SECTION_URL = "https://news.naver.com/breakingnews/section/{section}/{detail}?date={date}"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)

# 100: 정치, 101: 경제, 102: 사회, 103: 생활/문화, 104: 세계, 105: IT/과학
SECTIONS = {
    # 대통령실, 국회/정당, 행정, 국방/외교, 북한, 정치 일반
    "100": ["264", "265", "266", "267", "268", "269"],
    # 금융, 증권, 산업/재계, 중기/벤처, 부동산, 글로벌 경제, 생활 경제, 경제 일반
    "101": ["259", "258", "261", "771", "260", "262", "310", "263"],
    # 사건사고, 교육, 노동, 언론, 환경, 인권/복지, 식품/의료, 지역, 인물, 사회 일반
    "102": ["249", "250", "251", "254", "252", "59b", "255", "256", "276", "257"],
    # 건강정보, 자동차/시승기, 도로/교통, 여행/레저, 음식/맛집, 패션/뷰티, 공연/전시, 책, 종교, 날씨, 생활문화 일반
    "103": ["241", "239", "240", "237", "238", "376", "242", "243", "244", "248", "245"],
    # 아시아/호주, 미국/중남미, 유럽, 중동/아프리카, 세계 일반
    "104": ["231", "232", "233", "234", "322"],
    # 모바일, 인터넷/SNS, 통신/뉴미디어, IT 일반, 보안/해킹, 컴퓨터, 게임/리뷰, 과학 일반
    "105": ["731", "226", "227", "230", "732", "283", "229", "228"],
}


@dataclass
class CrawledArticle:
    section_code: str
    detail_section_code: str
    title: str
    content: str
    url: str
    published_at: datetime.datetime | None


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def list_article_urls(session: requests.Session, section: str, detail: str, date: datetime.date) -> list[str]:
    url = SECTION_URL.format(section=section, detail=detail, date=date.strftime("%Y%m%d"))
    response = session.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return [a["href"] for a in soup.select("div.sa_text > a[href]")]


def parse_article(html: str) -> tuple[str, str, datetime.datetime | None] | None:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h2", id="title_area")
    content_tag = soup.find("article", id="dic_area") or soup.find("div", id="newsct_article")
    if not title_tag or not content_tag:
        return None

    title = re.sub(r"\[.*?\]|\(.*?\)", "", title_tag.get_text(strip=True)).strip()
    content = content_tag.get_text(" ", strip=True)

    published_at = None
    date_tag = soup.select_one("span._ARTICLE_DATE_TIME[data-date-time]")
    if date_tag:
        published_at = datetime.datetime.strptime(date_tag["data-date-time"], "%Y-%m-%d %H:%M:%S")

    return title, content, published_at


def crawl(date: datetime.date, skip_urls: set[str]) -> Iterator[list[CrawledArticle]]:
    """섹션마다 새로 수집한 기사 묶음을 내놓는다.

    같은 기사가 여러 섹션 목록에 올라오므로, 수집한 URL은 skip_urls에 추가해 다시 받지 않는다.
    """
    session = make_session()

    for section, details in SECTIONS.items():
        for detail in details:
            try:
                urls = list_article_urls(session, section, detail, date)
            except requests.RequestException as e:
                log.warning("섹션 목록 수집 실패 %s/%s: %s", section, detail, e)
                continue

            articles = []
            for url in urls:
                if url in skip_urls:
                    continue
                skip_urls.add(url)
                try:
                    response = session.get(url, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as e:
                    log.warning("기사 수집 실패 %s: %s", url, e)
                    continue

                parsed = parse_article(response.text)
                if parsed:
                    title, content, published_at = parsed
                    articles.append(CrawledArticle(section, detail, title, content, url, published_at))
                time.sleep(settings.crawl_delay)

            log.info("섹션 %s/%s: 신규 %d건", section, detail, len(articles))
            yield articles
