from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/corner_analytics"
    REDIS_URL: str = "redis://localhost:6379/0"
    API_FOOTBALL_KEY: str = ""
    API_FOOTBALL_HOST: str = "v3.football.api-sports.io"
    SECRET_KEY: str = "change_me"

    model_config = {"env_file": ".env"}


settings = Settings()
