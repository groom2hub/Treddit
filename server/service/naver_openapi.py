"""네이버 검색 Open API 공통 클라이언트."""
import html
import re

import requests
from fastapi import HTTPException

from config import settings

SEARCH_URL = "https://openapi.naver.com/v1/search/{kind}.json"
TAG_PATTERN = re.compile(r"<[^>]+>")


def strip_tags(text: str) -> str:
    """검색 결과의 <b> 강조 태그와 HTML 엔티티를 제거한다."""
    return html.unescape(TAG_PATTERN.sub("", text))


def search(kind: str, query: str, **params) -> list[dict]:
    if not settings.naver_client_id or not settings.naver_client_secret:
        raise HTTPException(status_code=503, detail="네이버 API 키가 설정되지 않았습니다.")

    response = requests.get(
        SEARCH_URL.format(kind=kind),
        params={"query": query, **params},
        headers={
            "X-Naver-Client-Id": settings.naver_client_id,
            "X-Naver-Client-Secret": settings.naver_client_secret,
        },
        timeout=5,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="네이버 검색 API 호출에 실패했습니다.")

    return response.json().get("items", [])
