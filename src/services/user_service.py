from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError, NotFoundError
from src.core.security import hash_password
from src.models.enums import UserRole
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserRegister


class UserService:
    """Business rules for user management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserRegister) -> User:
        """Register a public user. The first user becomes administrator."""

        if self.users.get_by_email(payload.email):
            raise ConflictError("Email already registered")

        role = UserRole.ADMIN if self.users.count() == 0 else UserRole.OPERATOR
        user = User(
            name=payload.name,
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            role=role,
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create(self, payload: UserCreate) -> User:
        """Create a user with an explicit role."""

        if self.users.get_by_email(payload.email):
            raise ConflictError("Email already registered")

        user = User(
            name=payload.name,
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List registered users."""

        return self.users.list(skip=skip, limit=limit)

    def get_by_email_or_fail(self, email: str) -> User:
        """Return an active user by email or raise a domain error."""

        user = self.users.get_by_email(email)
        if not user or not user.active:
            raise NotFoundError("User not found")
        return user
