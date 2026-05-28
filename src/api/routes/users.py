from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_auth_user
from src.database.session import get_db
from src.models.user import User
from src.schemas.user import UserRead
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(get_auth_user),
) -> UserRead:
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    _: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    return UserService(db).list(skip=skip, limit=limit)
