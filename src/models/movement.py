from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from src.database.base import Base
from src.models.enums import MovementType


class Movement(Base):
    """Stock movement history record."""

    __tablename__ = "movements"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(
            MovementType,
            name="movement_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True
    )

    product = relationship("Product", back_populates="movements")
    user = relationship("User", back_populates="movements")
