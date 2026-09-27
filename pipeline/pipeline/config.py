from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str

    # 기사 요청 사이 대기 시간(초). 네이버에 부담을 주지 않도록 둔다.
    crawl_delay: float = 0.1
    # LDA 토픽 수
    num_topics: int = 100
    # 날짜별로 저장할 상위 키워드 수
    top_keywords: int = 100


settings = Settings()
