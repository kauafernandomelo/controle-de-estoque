from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.enums import MovementType
from src.models.movement import Movement
from src.models.product import Product


class MovementRepository:
    """Persistence and reporting operations for stock movements."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, movement: Movement) -> Movement:
        """Add a movement to the current unit of work."""

        self.db.add(movement)
        return movement

    def list(self, skip: int = 0, limit: int = 100) -> list[Movement]:
        """List stock movements ordered by creation date descending."""

        statement = select(Movement).order_by(Movement.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def exists_for_product(self, product_id: UUID) -> bool:
        """Return whether a product has movements."""

        total = self.db.scalar(
            select(func.count(Movement.id)).where(Movement.product_id == product_id)
        )
        return bool(total)

    def most_moved_products(self, limit: int = 10) -> list[tuple[UUID, str, str, int]]:
        """Return products with the highest absolute moved quantity."""

        statement = (
            select(
                Product.id,
                Product.name,
                Product.sku,
                func.sum(func.abs(Movement.quantity)).label("total_quantity"),
            )
            .join(Movement, Movement.product_id == Product.id)
            .group_by(Product.id, Product.name, Product.sku)
            .order_by(func.sum(func.abs(Movement.quantity)).desc())
            .limit(limit)
        )
        return [
            (row[0], row[1], row[2], int(row[3] or 0))
            for row in self.db.execute(statement).all()
        ]

    def totals_by_type_and_period(
        self, movement_type: MovementType, start_at: datetime, end_at: datetime
    ) -> int:
        """Return total movement quantity for a movement type and period."""

        statement = select(func.sum(Movement.quantity)).where(
            Movement.movement_type == movement_type,
            Movement.created_at >= start_at,
            Movement.created_at <= end_at,
        )
        return int(self.db.scalar(statement) or 0)
