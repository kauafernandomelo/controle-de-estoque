from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError, NotFoundError
from src.models.product import Product
from src.repositories.movement_repository import MovementRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Business rules for product management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = ProductRepository(db)
        self.movements = MovementRepository(db)

    def create(self, payload: ProductCreate) -> Product:
        """Create a product ensuring SKU uniqueness."""

        if self.products.get_by_sku(payload.sku):
            raise ConflictError("SKU already registered")

        product = Product(**payload.model_dump())
        self.products.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: UUID, payload: ProductUpdate) -> Product:
        """Partially update a product and keep SKU unique."""

        product = self.get(product_id)
        data = payload.model_dump(exclude_unset=True)

        if "sku" in data:
            existing = self.products.get_by_sku(data["sku"])
            if existing and existing.id != product.id:
                raise ConflictError("SKU already registered")

        for field, value in data.items():
            setattr(product, field, value)


        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: UUID) -> None:
        """Delete a product only when there is no movement history."""

        product = self.get(product_id)
        if self.movements.exists_for_product(product.id):
            raise ConflictError("Product with movement history cannot be deleted")
        self.products.delete(product)
        self.db.commit()

    def get(self, product_id: UUID) -> Product:
        """Return a product by id or raise not found."""

        product = self.products.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def get_by_sku(self, sku: str) -> Product:
        """Return a product by SKU or raise not found."""

        product = self.products.get_by_sku(sku)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def list(self, skip: int = 0, limit: int = 100, name: str | None = None) -> list[Product]:
        """List products with optional name filtering."""

        return self.products.list(skip=skip, limit=limit, name=name)
