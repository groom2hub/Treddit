from . import naver_openapi


def get_definition(keyword: str):
    items = naver_openapi.search("encyc", keyword)
    return {"definition": naver_openapi.strip_tags(items[0]["description"]) if items else None}
