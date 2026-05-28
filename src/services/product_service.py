from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError, NotFoundError
from src.models.product import Product
from src.repositories.movement_repository import MovementRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)
        self.movements = MovementRepository(db)

    def get_by_id(self, product_id: UUID) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Produto não encontrado")
        return product

    def get_by_sku(self, sku: str) -> Product:
        product = self.repo.get_by_sku(sku.strip().upper())
        if not product:
            raise NotFoundError("Produto não encontrado")
        return product

    def list(
        self,
        name: str | None = None,
        category: str | None = None,
        low_stock: bool | None = None,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        return self.repo.list(
            name=name,
            category=category,
            low_stock=low_stock,
            active=active,
            limit=limit,
            offset=offset,
        )

    def create(self, data: ProductCreate) -> Product:
        if self.repo.get_by_sku(data.sku):
            raise ConflictError("SKU já cadastrado")

        if data.ean and self.repo.get_by_ean(data.ean):
            raise ConflictError("EAN já cadastrado")

        product = Product(**data.model_dump())
        self.repo.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: UUID, data: ProductUpdate) -> Product:
        product = self.get_by_id(product_id)
        update_data = data.model_dump(exclude_unset=True)

        if "sku" in update_data:
            sku = update_data["sku"].strip().upper()
            existing = self.repo.get_by_sku(sku)
            if existing and existing.id != product_id:
                raise ConflictError("SKU já cadastrado")
            update_data["sku"] = sku

        if "ean" in update_data and update_data["ean"] is not None:
            existing = self.repo.get_by_ean(update_data["ean"])
            if existing and existing.id != product_id:
                raise ConflictError("EAN já cadastrado")

        for key, value in update_data.items():
            setattr(product, key, value)

        self.repo.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: UUID) -> None:
        product = self.get_by_id(product_id)
        if self.movements.exists_for_product(product.id):
            raise ConflictError("Produto possui movimentações vinculadas")
        self.repo.delete(product)
        self.db.commit()
