from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_auth_user
from src.database.session import get_db
from src.models.enums import MovementType
from src.models.user import User
from src.repositories.movement_repository import MovementRepository
from src.schemas.movement import MovementCreate, MovementRead
from src.services.movement_service import MovementService

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
def create_movement(
    payload: MovementCreate,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
) -> MovementRead:
    movement = MovementService(db).create(payload=payload, user_id=current_user.id)
    return MovementRead.model_validate({
        "id": movement.id,
        "product_id": movement.product_id,
        "product_name": movement.product.name if movement.product else "",
        "user_id": movement.user_id,
        "movement_type": movement.movement_type,
        "quantity": movement.quantity,
        "observation": movement.observation,
        "created_at": movement.created_at,
    })


@router.get("", response_model=list[MovementRead])
def list_movements(
    tipo: MovementType | None = Query(None),
    produto_id: UUID | None = Query(None),
    data_inicio: datetime | None = Query(None),
    data_fim: datetime | None = Query(None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    response: Response = None,
    _: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
) -> list[MovementRead]:
    repo = MovementRepository(db)
    movements = repo.list_movements(
        movement_type=tipo,
        product_id=produto_id,
        date_start=data_inicio,
        date_end=data_fim,
        skip=skip,
        limit=limit,
    )
    response.headers["X-Total-Count"] = str(repo.count(
        movement_type=tipo,
        product_id=produto_id,
        date_start=data_inicio,
        date_end=data_fim,
    ))
    result = [
        MovementRead.model_validate({
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name if m.product else "",
            "user_id": m.user_id,
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "observation": m.observation,
            "created_at": m.created_at,
        })
        for m in movements
    ]
    return result
