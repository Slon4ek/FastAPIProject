from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    CORS_ORIGINS: str = "http://localhost:3000,http://frontend:80"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
