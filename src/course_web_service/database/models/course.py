from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from course_web_service.database.mixins.id_mixins import IDMixin, IDMixinUUID
from course_web_service.database.mixins.timestamp_mixins import TimestampsMixin
from course_web_service.database.models.base import Base

if TYPE_CHECKING:
    from course_web_service.database.models.content import Assignment, UserProgress
    from course_web_service.database.models.payment import Purchase
    from course_web_service.database.models.review import Review
    from course_web_service.database.models.user import Curator


class Course(Base, TimestampsMixin, IDMixin):
    """Модель курса."""

    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    curator_id: Mapped[int] = mapped_column(Integer, ForeignKey("curator.id", ondelete="CASCADE"))

    curator: Mapped["Curator"] = relationship("Curator", back_populates="courses")
    topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="course")
    purchases: Mapped[list["Purchase"]] = relationship("Purchase", back_populates="course")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="course")


class Topic(Base, TimestampsMixin, IDMixin):
    """Модель темы курса."""

    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("course.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, CheckConstraint("order > 0"))

    course: Mapped["Course"] = relationship("Course", back_populates="topics")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="topic")


class Lesson(Base, TimestampsMixin, IDMixinUUID):
    """Модель урока."""

    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topic.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, CheckConstraint("order > 0"))

    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="lesson")
    progress: Mapped[list["UserProgress"]] = relationship("UserProgress", back_populates="lesson")
