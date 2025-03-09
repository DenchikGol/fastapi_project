import logging

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations():
    """Применяет миграции к базе данных."""
    try:
        logger.info("Applying migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply migrations: {e}")
        raise


def make_migrations(message: str | None = None):
    """Создает новую миграцию."""
    if not message:
        message = "New migration"

    try:
        logger.info(f"Creating migration with message: {message}")
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message=message)
        logger.info("Migration created successfully.")
    except Exception as e:
        logger.error(f"Failed to create migration: {e}")
        raise
