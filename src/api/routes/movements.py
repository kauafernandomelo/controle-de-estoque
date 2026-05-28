from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.schemas.movement import MovementCreate, MovementRead
from src.services.movement_service import MovementService

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
def create_movement(
    payload: MovementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MovementRead:
    """Create an inventory movement and update stock automatically."""

    return MovementService(db).create(payload=payload, user_id=current_user.id)


@router.get("", response_model=list[MovementRead])
def list_movements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MovementRead]:
    """List inventory movement history."""

    return MovementService(db).list(skip=skip, limit=limit)
