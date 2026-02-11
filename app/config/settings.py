from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class DatabaseSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )

    DB_HOST: str = "localhost"
    DB_PORT: int = 55432
    DB_NAME: str = "demo"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "5621"

    @property
    def get_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = DatabaseSettings()
