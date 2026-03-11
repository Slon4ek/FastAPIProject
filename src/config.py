from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# определяем абсолютный путь до корня проекта
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    @property
    def DB_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        # pathlib позволяет формировать путь
        # с помощью оператора "/", аналогично os.path.join()
        env_file=BASE_DIR
        / ".env",
    )


settings = Settings()
