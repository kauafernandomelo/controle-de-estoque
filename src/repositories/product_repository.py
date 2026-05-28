from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: UUID) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.execute(select(Product).where(Product.sku == sku)).scalar_one_or_none()

    def get_by_ean(self, ean: str) -> Product | None:
        return self.db.execute(select(Product).where(Product.ean == ean)).scalar_one_or_none()

    def _build_query(
        self,
        name: str | None = None,
        category: str | None = None,
        low_stock: bool | None = None,
        active: bool | None = None,
    ):
        stmt = select(Product)
        if name:
            stmt = stmt.where(Product.name.ilike(f"%{name}%"))
        if category:
            stmt = stmt.where(Product.category.ilike(f"%{category}%"))
        if low_stock:
            stmt = stmt.where(Product.stock_quantity <= Product.minimum_stock)
        if active is not None:
            stmt = stmt.where(Product.active.is_(active))
        return stmt

    def list(
        self,
        name: str | None = None,
        category: str | None = None,
        low_stock: bool | None = None,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        stmt = self._build_query(name, category, low_stock, active)
        stmt = stmt.order_by(Product.name).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def count(
        self,
        name: str | None = None,
        category: str | None = None,
        low_stock: bool | None = None,
        active: bool | None = None,
    ) -> int:
        stmt = self._build_query(name, category, low_stock, active)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return self.db.scalar(count_stmt) or 0

    def add(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()
