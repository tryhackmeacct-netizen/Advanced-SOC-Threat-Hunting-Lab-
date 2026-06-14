from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017/soc_db"
    mongo_db: str = "soc_db"
    opensearch_url: str = "http://localhost:9200"
    vt_api_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
