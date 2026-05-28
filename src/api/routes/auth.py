from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.auth import RefreshTokenRequest, Token
from src.schemas.user import UserRead, UserRegister
from src.services.auth_service import AuthService
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    """Register a new user. The first registered user becomes administrator."""

    return UserService(db).register(payload)  # type: ignore[return-value]


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """Authenticate with email and password and return JWT tokens."""

    return AuthService(db).login(email=form_data.username, password=form_data.password)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> Token:
    """Refresh an access token using a valid refresh token."""

    return AuthService(db).refresh(payload.refresh_token)
