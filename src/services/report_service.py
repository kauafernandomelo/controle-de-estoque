from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.enums import MovementType
from src.models.product import Product
from src.repositories.movement_repository import MovementRepository
from src.schemas.report import (
    InventoryTotals,
    LowStockProduct,
    MostMovedProduct,
    PeriodMovementTotal,
)


class ReportService:
    """Read-only reporting use cases for inventory analytics."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.movements = MovementRepository(db)

    def low_stock_products(self) -> list[LowStockProduct]:
        """Return active products below or equal to their configured minimum stock."""

        statement = select(Product).where(
            Product.active.is_(True), Product.stock_quantity <= Product.minimum_stock
        )
        products = self.db.scalars(statement).all()
        return [
            LowStockProduct.model_validate(product, from_attributes=True) for product in products
        ]

    def most_moved_products(self, limit: int = 10) -> list[MostMovedProduct]:
        """Return products ordered by total movement volume."""

        return [
            MostMovedProduct(
                product_id=product_id,
                name=name,
                sku=sku,
                total_quantity=total_quantity,
            )
            for product_id, name, sku, total_quantity in self.movements.most_moved_products(
                limit=limit
            )
        ]

    def movement_total_by_period(
        self, movement_type: MovementType, start_at: datetime, end_at: datetime
    ) -> PeriodMovementTotal:
        """Return total movement quantity for a type inside a date range."""

        total = self.movements.totals_by_type_and_period(movement_type, start_at, end_at)
        return PeriodMovementTotal(movement_type=movement_type, total_quantity=total)

    def inventory_totals(self) -> InventoryTotals:
        """Return total stock value and quantity across active products."""

        statement = select(
            func.coalesce(func.sum(Product.cost_price * Product.stock_quantity), 0),
            func.coalesce(func.sum(Product.stock_quantity), 0),
        ).where(Product.active.is_(True))
        total_value, total_items = self.db.execute(statement).one()
        return InventoryTotals(
            total_stock_value=Decimal(total_value or 0),
            total_items=int(total_items or 0),
        )
