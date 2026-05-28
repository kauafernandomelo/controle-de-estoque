from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.user import User


class UserRepository:
    """Persistence operations for users."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        """Find a user by id."""

        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Find a user by email."""

        return self.db.scalar(select(User).where(User.email == email.lower()))

    def count(self) -> int:
        """Return the total number of users."""

        return self.db.scalar(select(func.count(User.id))) or 0

    def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users using offset pagination."""

        return list(self.db.scalars(select(User).offset(skip).limit(limit)).all())

    def add(self, user: User) -> User:
        """Add a user to the current unit of work."""

        self.db.add(user)
        return user
