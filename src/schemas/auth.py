from pydantic import BaseModel


class Token(BaseModel):
    """JWT token pair returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Payload used to renew an access token."""

    refresh_token: str
