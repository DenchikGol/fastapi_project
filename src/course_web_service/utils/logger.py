import logging
import sys
from abc import ABC, abstractmethod
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from course_web_service.core.settings import settings


class LogFormatter(ABC):
    """Абстрактный базовый класс для форматтеров логов."""

    @abstractmethod
    def create_formatter(self) -> logging.Formatter:
        pass


class DefaultFileFormatter(LogFormatter):
    """Форматтер для файловых логов."""

    def __init__(self, fmt: str = None):
        self.fmt = fmt or settings.logger_settings.log_format

    def create_formatter(self) -> logging.Formatter:
        return logging.Formatter(self.fmt)


class ConsoleFormatter(LogFormatter):
    """Упрощенный форматтер для консоли."""

    def create_formatter(self) -> logging.Formatter:
        return logging.Formatter("%(levelname)s - %(message)s")


class LoggerConfig:
    """Класс конфигурации логгера."""

    def __init__(
        self,
        name: str = settings.app_name,
        log_dir: str | Path = settings.logger_settings.log_dir,
        log_file: str = settings.logger_settings.log_file,
        level: int = logging.INFO,
        backup_count: int = settings.logger_settings.backup_count,
        max_log_size: int = settings.logger_settings.max_log_size,
        when: str = "midnight",
        encoding: str = "utf-8",
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_file = log_file
        self.level = level
        self.backup_count = backup_count
        self.max_log_size = max_log_size
        self.when = when
        self.encoding = encoding


class AppLogger:
    """Основной класс логгера приложения."""

    def __init__(self, config: LoggerConfig):
        self.config = config
        self._logger: logging.Logger | None = None
        self._setup_done = False

    @property
    def logger(self) -> logging.Logger:
        if not self._setup_done:
            raise RuntimeError("Logger not initialized. Call setup() first.")
        return self._logger

    def setup(self) -> None:
        """Настройка логгера с обработчиками."""
        if self._setup_done:
            return
        try:
            self._validate_config()
            self._create_log_directory()
            self._logger = logging.getLogger(self.config.name)
            self._logger.setLevel(self.config.level)

            self._add_console_handler()
            self._add_file_handler()

            self._setup_done = True
            self._logger.info("Logger initialized successfully")

        except Exception as e:
            logging.critical(f"Failed to initialize logger: {e}")
            raise

    def _validate_config(self) -> None:
        """Проверка валидности конфигурации."""
        if not isinstance(self.config.level, int):
            raise ValueError("Log level must be an integer")

    def _create_log_directory(self) -> None:
        """Создание директории для логов."""
        try:
            self.config.log_dir.mkdir(exist_ok=True, mode=0o755)
        except PermissionError as e:
            raise PermissionError(f"Can't create log directory: {e}") from e

    def _add_console_handler(self) -> None:
        """Добавление обработчика для консоли."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ConsoleFormatter().create_formatter())
        self._logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """Добавление обработчика для файла."""
        file_path = self.config.log_dir / self.config.log_file
        file_handler = TimedRotatingFileHandler(
            filename=file_path,
            when=self.config.when,
            backupCount=self.config.backup_count,
            encoding=self.config.encoding,
        )
        file_handler.setFormatter(DefaultFileFormatter().create_formatter())
        self._logger.addHandler(file_handler)
