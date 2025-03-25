import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy. Автоматически генерирует имя таблицы."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        if hasattr(cls, "__tablename_override__"):
            return cls.__tablename_override__
        name = cls.__name__
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return cls.__name__.lower()

    def __repr__(self) -> str:
        """Удобное представление объекта для отладки."""
        attrs = ", ".join(
            f"{key}={value!r}" for key, value in self.__dict__.items() if not key.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"
