import datetime

from pipeline import crawler

SECTION_HTML = """
<ul>
  <li><div class="sa_text"><a href="https://n.news.naver.com/mnews/article/001/1">기사1</a></div></li>
  <li><div class="sa_text"><a href="https://n.news.naver.com/mnews/article/001/2">기사2</a></div></li>
  <li><div class="sa_text_lede">요약</div></li>
</ul>
"""

ARTICLE_HTML = """
<h2 id="title_area">[속보] 오픈AI 에이전트(종합) 발표</h2>
<span class="media_end_head_info_datestamp_time _ARTICLE_DATE_TIME" data-date-time="2026-09-26 14:44:13">2026.09.26. 오후 2:44</span>
<article id="dic_area">첫 문단<br>둘째 문단</article>
"""


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.requested = []

    def get(self, url, timeout):
        self.requested.append(url)
        return FakeResponse(self.pages.get(url, SECTION_HTML))


def test_list_article_urls():
    session = FakeSession({})
    urls = crawler.list_article_urls(session, "105", "230", datetime.date(2026, 9, 26))
    assert urls == ["https://n.news.naver.com/mnews/article/001/1", "https://n.news.naver.com/mnews/article/001/2"]
    assert session.requested == ["https://news.naver.com/breakingnews/section/105/230?date=20260926"]


def test_parse_article():
    title, content, published_at = crawler.parse_article(ARTICLE_HTML)
    assert title == "오픈AI 에이전트 발표"
    assert content == "첫 문단 둘째 문단"
    assert published_at == datetime.datetime(2026, 9, 26, 14, 44, 13)


def test_parse_article_without_body():
    assert crawler.parse_article("<html><body>삭제된 기사</body></html>") is None


def test_crawl_skips_duplicate_urls_across_sections(monkeypatch):
    monkeypatch.setattr(crawler, "SECTIONS", {"105": ["230", "731"]})
    monkeypatch.setattr(crawler.settings, "crawl_delay", 0)
    pages = {
        "https://n.news.naver.com/mnews/article/001/1": ARTICLE_HTML,
        "https://n.news.naver.com/mnews/article/001/2": ARTICLE_HTML,
    }
    monkeypatch.setattr(crawler, "make_session", lambda: FakeSession(pages))

    skip = {"https://n.news.naver.com/mnews/article/001/2"}
    batches = list(crawler.crawl(datetime.date(2026, 9, 26), skip))

    # 두 섹션 목록에 같은 기사가 있어도 한 번만, 이미 저장된 기사는 수집하지 않는다
    assert [[a.url for a in batch] for batch in batches] == [["https://n.news.naver.com/mnews/article/001/1"], []]
