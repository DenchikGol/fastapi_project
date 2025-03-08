from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from course_web_service.database.mixins.id_mixins import IDMixin
from course_web_service.database.mixins.timestamp_mixins import TimestampsMixin
from course_web_service.database.models.base import Base


class User(Base, TimestampsMixin, IDMixin):
    """Модель пользователя."""

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
