import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from course_web_service.database.mixins.id_mixins import IDMixinUUID
from course_web_service.database.mixins.timestamp_mixins import TimestampsMixin
from course_web_service.database.models.base import Base

if TYPE_CHECKING:
    from course_web_service.database.models.course import Lesson
    from course_web_service.database.models.user import User


class Assignment(Base, TimestampsMixin, IDMixinUUID):
    """Модель задания для урока."""

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID, ForeignKey("lesson.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="assignments")
    progress: Mapped[list["UserProgress"]] = relationship(
        "UserProgress", back_populates="assignment"
    )


class UserProgress(Base, TimestampsMixin, IDMixinUUID):
    """Модель прогресса пользователя по уроку."""

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lesson.id", ondelete="CASCADE"))
    assignment_id: Mapped[int] = mapped_column(
        uuid.UUID, ForeignKey("assignment.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String, default="начато")
    score: Mapped[float] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="progress")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")
    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="progress")
