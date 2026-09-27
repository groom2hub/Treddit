import requests
from fastapi import HTTPException

from config import settings

ENCYC_URL = "https://openapi.naver.com/v1/search/encyc.json"


def get_definition(keyword: str):
    response = requests.get(
        ENCYC_URL,
        params={"query": keyword},
        headers={
            "X-Naver-Client-Id": settings.naver_client_id,
            "X-Naver-Client-Secret": settings.naver_client_secret,
        },
        timeout=5,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="네이버 백과사전 조회에 실패했습니다.")

    items = response.json().get("items", [])
    return {"definition": items[0]["description"] if items else None}
