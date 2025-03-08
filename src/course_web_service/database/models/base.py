from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy. Автоматически генерирует имя таблицы."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        if hasattr(cls, "__tablename_override__"):
            return cls.__tablename_override__
        return cls.__name__.lower()
