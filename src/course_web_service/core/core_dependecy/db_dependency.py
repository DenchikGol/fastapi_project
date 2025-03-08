from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from course_web_service.core.settings import settings


class DBDependency:
    """Класс для управления зависимостями базы данных."""

    def __init__(self) -> None:
        """Инициализирует асинхронный движок и фабрику сессий."""
        self._engine = create_async_engine(
            url=settings.db_settings.db_url, echo=settings.db_settings.db_echo
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
        )

    @property
    def db_session(self) -> async_sessionmaker[AsyncSession]:
        """Возвращает фабрику асинхронных сессий."""
        return self._session_factory

    async def close(self):
        """Закрывает асинхронный движок."""
        await self._engine.dispose()
