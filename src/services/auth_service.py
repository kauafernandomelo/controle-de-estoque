from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.repositories.user_repository import UserRepository
from src.schemas.auth import Token


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(self, email: str, password: str) -> Token:
        user = self.users.get_by_email(email)
        if not user or not user.active or not verify_password(password, user.hashed_password):
            raise AppException("Invalid credentials", status_code=401)

        return Token(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> Token:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            user_id = UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise AppException("Invalid refresh token", status_code=401) from exc

        user = self.users.get_by_id(user_id)
        if not user or not user.active:
            raise AppException("Invalid refresh token", status_code=401)

        return Token(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
