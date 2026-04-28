"""JWT token response schemas."""

from pydantic import BaseModel


class TokenPair(BaseModel):
    """Returned on successful login or registration."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    """Returned on a successful token refresh."""

    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload for the token-refresh endpoint."""

    refresh_token: str
