from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from pwdlib import PasswordHash

from src.core.config import settings

pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_access_token(subject: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "type": "access", "exp": expires_at}
    result = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(result)


def create_refresh_token(subject: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "type": "refresh", "exp": expires_at}
    result = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(result)


def decode_token(token: str) -> dict[str, str]:
    try:
        result = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return dict(result)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
