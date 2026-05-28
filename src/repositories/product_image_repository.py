from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, image_id: UUID) -> ProductImage | None:
        return self.db.get(ProductImage, image_id)

    def list_by_product(self, product_id: UUID) -> list[ProductImage]:
        stmt = (
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )
        return list(self.db.execute(stmt).scalars().all())

    def add(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        self.db.flush()
        return image

    def delete(self, image: ProductImage) -> None:
        self.db.delete(image)
        self.db.flush()
