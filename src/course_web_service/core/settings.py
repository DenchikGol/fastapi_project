from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_echo: bool

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"


class AuthSettings(BaseSettings):
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int
    refrsh_token_expire_days: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()
    auth_settings: AuthSettings = AuthSettings()


settings = Settings()
