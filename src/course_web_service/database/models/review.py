import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from course_web_service.database.mixins.id_mixins import IDMixin
from course_web_service.database.mixins.timestamp_mixins import TimestampsMixin
from course_web_service.database.models.base import Base

if TYPE_CHECKING:
    from course_web_service.database.models.course import Course
    from course_web_service.database.models.user import User


class Review(Base, TimestampsMixin, IDMixin):
    """Модель отзыва пользователя на курс."""

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("course.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(
        Integer, CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range")
    )
    comment: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    course: Mapped["Course"] = relationship("Course", back_populates="reviews")
