from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.exceptions import AppException, ForbiddenError
from src.core.security import decode_token
from src.database.session import get_db
from src.models.enums import UserRole
from src.models.user import User
from src.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Resolve the authenticated user from an access token."""

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AppException("Invalid authentication token", status_code=401) from exc

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.active:
        raise AppException("Invalid authentication token", status_code=401)
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has administrator permissions."""

    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError()
    return current_user
