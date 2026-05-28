from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.deps import require_admin
from src.database.session import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserRead
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserRead:
    """Create a user with a selected role. Administrator only."""

    return UserService(db).create(payload)


@router.get("", response_model=list[UserRead])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    """List users. Administrator only."""

    return UserService(db).list(skip=skip, limit=limit)
