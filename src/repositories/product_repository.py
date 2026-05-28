from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.models.product import Product


class ProductRepository:
    """Persistence operations for products."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: UUID) -> Product | None:
        """Find a product by id."""

        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        """Find a product by SKU."""

        return self.db.scalar(select(Product).where(Product.sku == sku.upper()))

    def list(self, skip: int = 0, limit: int = 100, name: str | None = None) -> list[Product]:
        """List products with optional case-insensitive name search."""

        statement = select(Product).order_by(Product.name).offset(skip).limit(limit)
        if name:
            statement = (
                select(Product)
                .where(Product.name.ilike(f"%{name}%"))
                .order_by(Product.name)
                .offset(skip)
                .limit(limit)
            )
        return list(self.db.scalars(statement).all())

    def add(self, product: Product) -> Product:
        """Add a product to the current unit of work."""

        self.db.add(product)
        return product

    def delete(self, product: Product) -> None:
        """Remove a product from the current unit of work."""

        self.db.execute(delete(Product).where(Product.id == product.id))
