from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./capital_tracker.db"
    app_name: str = "Capital Tracker API"

    class Config:
        env_file = ".env"


settings = Settings()
