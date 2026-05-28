from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import AppException, NotFoundError
from src.models.enums import MovementType
from src.models.movement import Movement
from src.repositories.movement_repository import MovementRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.movement import MovementCreate


class MovementService:
    """Business rules for stock movements."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = ProductRepository(db)
        self.movements = MovementRepository(db)

    def create(self, payload: MovementCreate, user_id: UUID) -> Movement:
        """Create a stock movement and update product stock atomically."""

        product = self.products.get_by_id(payload.product_id)
        if not product:
            raise NotFoundError("Product not found")

        new_quantity = product.stock_quantity
        if payload.movement_type == MovementType.IN:
            new_quantity += payload.quantity
        elif payload.movement_type == MovementType.OUT:
            new_quantity -= payload.quantity
        else:
            new_quantity += payload.quantity

        if new_quantity < 0:
            raise AppException("Stock cannot become negative", status_code=400)

        product.stock_quantity = new_quantity
        movement = Movement(
            product_id=payload.product_id,
            user_id=user_id,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            observation=payload.observation,
        )
        self.movements.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def list(self, skip: int = 0, limit: int = 100) -> list[Movement]:
        """List stock movement history."""

        return self.movements.list(skip=skip, limit=limit)
