import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from course_web_service.database.mixins.id_mixins import IDMixin, IDMixinUUID
from course_web_service.database.mixins.timestamp_mixins import TimestampsMixin
from course_web_service.database.models.base import Base

if TYPE_CHECKING:
    from course_web_service.database.models.content import UserProgress
    from course_web_service.database.models.course import Course
    from course_web_service.database.models.payment import Purchase
    from course_web_service.database.models.review import Review


class User(Base, TimestampsMixin, IDMixinUUID):
    """Модель пользователя."""

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.id", ondelete="CASCADE"))

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    purchases: Mapped[list["Purchase"]] = relationship("Purchase", back_populates="user")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")
    progress: Mapped[list["UserProgress"]] = relationship("UserProgress", back_populates="user")


class Role(Base, TimestampsMixin, IDMixin):
    """Модель пользовательских ролей."""

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class RefreshToken(Base, IDMixinUUID, TimestampsMixin):
    """Модель refresh-tokens для пользователей."""

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)


class Curator(Base, TimestampsMixin, IDMixin):
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    bio: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship("User")
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="curator")
