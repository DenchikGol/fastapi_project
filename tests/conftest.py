import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
async def test_db():
    # Создаем тестовую базу данных
    conn = await asyncpg.connect(
        database="postgres", user="postgres", password="postgres", host="localhost"
    )
    await conn.execute("CREATE DATABASE test_db")
    await conn.close()

    # Применяем миграции к тестовой базе данных
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url", "postgresql+asyncpg://postgres:postgres@localhost/test_db"
    )
    command.upgrade(alembic_cfg, "head")

    yield "postgresql+asyncpg://postgres:postgres@localhost/test_db"

    # Удаляем тестовую базу данных после завершения тестов
    conn = await asyncpg.connect(
        database="postgres", user="postgres", password="postgres", host="localhost"
    )
    await conn.execute("DROP DATABASE test_db")
    await conn.close()


@pytest.fixture
async def async_session(test_db):
    engine = create_async_engine(test_db)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
