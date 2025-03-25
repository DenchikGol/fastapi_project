from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """Настройки для подключения к базе данных."""

    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_echo: bool

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self) -> str:
        """Возвращает URL для подключения к базе данных."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"


class AuthSettings(BaseSettings):
    """Настройки для аутентификации и JWT."""

    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


class InitialAppSettings(BaseSettings):
    """Настройки для инициалтзации приложения."""

    admin_email: EmailStr
    admin_password: SecretStr
    manager_email: EmailStr
    manager_password: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


class LoggerSettings(BaseSettings):
    """Настройки для логгера."""

    log_dir: str
    log_file: str
    log_format: str
    max_log_size: int
    backup_count: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


class Settings(BaseSettings):
    """Основные настройки приложения."""

    app_name: str
    db_settings: DBSettings = DBSettings()
    auth_settings: AuthSettings = AuthSettings()
    init_app_settings: InitialAppSettings = InitialAppSettings()
    logger_settings: LoggerSettings = LoggerSettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


settings = Settings()
