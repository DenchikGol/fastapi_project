import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    """Mixin для добавления временной метки создания записи."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.datetime.now(datetime.UTC),
    )


class UpdatedAtMixin:
    """Mixin для добавления временной метки обновления записи."""

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=datetime.datetime.now(datetime.UTC),
    )


class TimestampsMixin(CreatedAtMixin, UpdatedAtMixin):
    """Mixin, объединяющий CreatedAtMixin и UpdatedAtMixin."""

    pass
