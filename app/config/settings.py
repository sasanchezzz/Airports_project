from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class DatabaseSettings(BaseSettings):

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_ECHO: bool

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        case_sensitive=False
    )

settings = DatabaseSettings
