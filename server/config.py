from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str
    jwt_secret_key: str
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    naver_client_id: str = ""
    naver_client_secret: str = ""
    naver_ad_api_key: str = ""
    naver_ad_secret_key: str = ""
    naver_ad_customer_id: str = ""

    openai_key: str = ""
    openai_model: str = "gpt-4o-mini"


settings = Settings()
