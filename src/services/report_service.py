from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.product import Product
from src.schemas.report import InventoryTotals, LowStockProduct


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def low_stock_products(self) -> list[LowStockProduct]:
        statement = select(Product).where(
            Product.active.is_(True), Product.stock_quantity <= Product.minimum_stock
        )
        products = self.db.scalars(statement).all()
        return [
            LowStockProduct.model_validate(product, from_attributes=True) for product in products
        ]

    def inventory_totals(self) -> InventoryTotals:
        statement = select(
            func.coalesce(func.sum(Product.cost_price * Product.stock_quantity), 0),
            func.coalesce(func.sum(Product.stock_quantity), 0),
        ).where(Product.active.is_(True))
        total_value, total_items = self.db.execute(statement).one()
        return InventoryTotals(
            total_stock_value=total_value,
            total_items=int(total_items or 0),
        )
