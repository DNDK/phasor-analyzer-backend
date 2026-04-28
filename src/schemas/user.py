"""Pydantic schemas for User registration, login, and responses."""

import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]{3,50}$")
_PASSWORD_MIN_LEN = 8


def _validate_username(value: str) -> str:
    if not _USERNAME_RE.match(value):
        raise ValueError(
            "Username must be 3–50 characters and contain only letters, digits, underscores, or hyphens."
        )
    return value


def _validate_password(value: str) -> str:
    if len(value) < _PASSWORD_MIN_LEN:
        raise ValueError(f"Password must be at least {_PASSWORD_MIN_LEN} characters.")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one digit.")
    return value


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class UserRegister(BaseModel):
    """Payload for creating a new account."""

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        return _validate_username(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password(v)


class UserLogin(BaseModel):
    """Payload for authenticating an existing account."""

    username: str
    password: str


class UserPublic(BaseModel):
    """Safe user representation — never exposes hashed_password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool
    is_verified: bool
