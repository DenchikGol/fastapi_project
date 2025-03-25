import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from course_web_service.database.mixins import id_mixins, timestamp_mixins
from course_web_service.database.models.base import Base

if TYPE_CHECKING:
    from course_web_service.database.models.course import Course
    from course_web_service.database.models.user import User


class Purchase(Base, timestamp_mixins.TimestampsMixin, id_mixins.IDMixinUUID):
    """Модель покупки курса."""

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("course.id", ondelete="CASCADE"))
    purchase_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))

    user: Mapped["User"] = relationship("User", back_populates="purchases")
    course: Mapped["Course"] = relationship("Course", back_populates="purchases")


class Payment(Base, timestamp_mixins.TimestampsMixin, id_mixins.IDMixinUUID):
    """Модель платежа."""

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("course.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    payment_method: Mapped[str] = mapped_column(String(50))
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="ожидание")

    user: Mapped["User"] = relationship("User", back_populates="payments")
    course: Mapped["Course"] = relationship("Course", back_populates="payments")
