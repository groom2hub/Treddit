"""기사 전처리 → 키워드 집계 → LDA 토픽 모델링 → 토픽 트렌드 선정."""
import re
from collections import Counter
from functools import cache
from pathlib import Path

from gensim import corpora
from gensim.models.ldamodel import LdaModel

STOPWORD_FILE = Path(__file__).with_name("stopword.txt")
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:\.[A-Za-z]{2,}){0,2}\b"
)


@cache
def stopwords() -> frozenset[str]:
    return frozenset(line.strip() for line in STOPWORD_FILE.read_text(encoding="utf-8").splitlines())


@cache
def okt():
    # JVM 기동이 느리므로 처음 필요할 때 한 번만 만든다
    from konlpy.tag import Okt
    return Okt()


def clean_text(content: str) -> str:
    content = re.sub(r"\[.*?\]|\(.*?\)", "", content)
    content = EMAIL_PATTERN.sub("", content)
    content = re.sub(r"[^\w,.]", " ", content)
    return re.sub(r"\s+", " ", content).strip()


def extract_nouns(content: str) -> list[str]:
    """기사 본문에서 불용어와 한 글자 단어를 제외한 명사를 추출한다."""
    stop = stopwords()
    return [noun for noun in okt().nouns(clean_text(content)) if len(noun) > 1 and noun not in stop]


def top_keywords(documents: list[list[str]], limit: int) -> list[tuple[str, int]]:
    counter = Counter(word for doc in documents for word in doc)
    return counter.most_common(limit)


def topic_trends(documents: list[list[str]], num_topics: int) -> list[tuple[str, int]]:
    """LDA로 토픽을 뽑고, 각 토픽의 대표 단어와 그 단어의 전체 등장 빈도를 반환한다.

    대표 단어는 토픽 상위 단어 중 실제 문서에 등장하는 첫 단어다.
    여러 토픽이 같은 대표 단어를 가지면 하나로 합친다. 빈도 내림차순 정렬.
    """
    documents = [doc for doc in documents if doc]
    if not documents:
        return []

    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    lda = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15, random_state=42)

    counts = Counter(word for doc in documents for word in doc)
    trends = {}
    for _, words in lda.show_topics(num_topics=num_topics, num_words=5, formatted=False):
        representative = next((word for word, _ in words if counts[word] > 0), None)
        if representative:
            trends[representative] = counts[representative]

    return sorted(trends.items(), key=lambda item: item[1], reverse=True)
