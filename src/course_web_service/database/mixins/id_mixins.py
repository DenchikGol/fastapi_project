import uuid

from sqlalchemy import UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column


class IDMixinUUID:
    """Mixin для добавления UUID первичного ключа в модели SQLAlchemy."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class IDMixin:
    """Mixin для добавления ID первичного ключа в модели SQLAlchemy."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
