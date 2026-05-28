from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.models.enums import MovementType
from src.models.movement import Movement
from src.models.product import Product


class MovementRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, movement: Movement) -> Movement:
        self.db.add(movement)
        return movement

    def count(
        self,
        movement_type: MovementType | None = None,
        product_id: UUID | None = None,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
    ) -> int:
        stmt = select(func.count(Movement.id))
        if movement_type:
            stmt = stmt.where(Movement.movement_type == movement_type)
        if product_id:
            stmt = stmt.where(Movement.product_id == product_id)
        if date_start:
            stmt = stmt.where(Movement.created_at >= date_start)
        if date_end:
            stmt = stmt.where(Movement.created_at <= date_end)
        return self.db.scalar(stmt) or 0

    def list_movements(
        self,
        movement_type: MovementType | None = None,
        product_id: UUID | None = None,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Movement]:
        statement = (
            select(Movement)
            .options(selectinload(Movement.product))
            .order_by(Movement.created_at.desc())
        )
        if movement_type:
            statement = statement.where(Movement.movement_type == movement_type)
        if product_id:
            statement = statement.where(Movement.product_id == product_id)
        if date_start:
            statement = statement.where(Movement.created_at >= date_start)
        if date_end:
            statement = statement.where(Movement.created_at <= date_end)

        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def exists_for_product(self, product_id: UUID) -> bool:
        total = self.db.scalar(
            select(func.count(Movement.id)).where(Movement.product_id == product_id)
        )
        return bool(total)

    def most_moved_products(self, limit: int = 10) -> list[tuple[UUID, str, str, int]]:
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
        statement = select(func.sum(Movement.quantity)).where(
            Movement.movement_type == movement_type,
            Movement.created_at >= start_at,
            Movement.created_at <= end_at,
        )
        return int(self.db.scalar(statement) or 0)
