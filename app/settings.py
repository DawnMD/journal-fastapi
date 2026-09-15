from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    CLERK_SECRET_KEY: str
    CLERK_JWT_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
