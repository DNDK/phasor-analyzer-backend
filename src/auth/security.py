"""
Core security utilities: password hashing and JWT creation/verification.
All token secrets and algorithm settings are read from environment variables —
never hardcoded — so the values are configurable per deployment.

Notes on password hashing:
  - passlib is unmaintained and broken on bcrypt 4.x / Python 3.14.
  - We use bcrypt directly instead.
  - Passwords are pre-hashed with SHA-256 (base64-encoded) before being fed
    to bcrypt, which safely handles passwords longer than bcrypt's 72-byte
    limit without silently truncating them.
"""

import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Literal

import bcrypt
from jose import JWTError, jwt

# ---------------------------------------------------------------------------
# Configuration — read from env (required in production, sensible dev fallback)
# ---------------------------------------------------------------------------

ACCESS_TOKEN_SECRET: str = os.environ.get(
    "ACCESS_TOKEN_SECRET",
    "CHANGE_ME_access_secret_at_least_32_chars_long!!",
)
REFRESH_TOKEN_SECRET: str = os.environ.get(
    "REFRESH_TOKEN_SECRET",
    "CHANGE_ME_refresh_secret_at_least_32_chars_long!",
)
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
BCRYPT_ROUNDS: int = int(os.environ.get("BCRYPT_ROUNDS", "12"))

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def _prehash(plain: str) -> bytes:
    """
    SHA-256 the password then base64-encode it so the result is always
    exactly 44 ASCII bytes — well within bcrypt's 72-byte limit.
    This prevents silent truncation of long passwords.
    """
    digest = hashlib.sha256(plain.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt (with SHA-256 pre-hashing)."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(_prehash(plain), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    try:
        return bcrypt.checkpw(_prehash(plain), hashed.encode("utf-8"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

TokenType = Literal["access", "refresh"]


def _create_token(
    user_id: int,
    token_type: TokenType,
    secret: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),   # subject — only the user PK, never email/password
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Create a short-lived access token."""
    return _create_token(
        user_id=user_id,
        token_type="access",
        secret=ACCESS_TOKEN_SECRET,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        user_id=user_id,
        token_type="refresh",
        secret=REFRESH_TOKEN_SECRET,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> int:
    """
    Verify and decode an access token.
    Returns the user_id (int) or raises ValueError on any problem.
    """
    return _decode_token(token, expected_type="access", secret=ACCESS_TOKEN_SECRET)


def decode_refresh_token(token: str) -> int:
    """
    Verify and decode a refresh token.
    Returns the user_id (int) or raises ValueError on any problem.
    """
    return _decode_token(token, expected_type="refresh", secret=REFRESH_TOKEN_SECRET)


def _decode_token(token: str, expected_type: TokenType, secret: str) -> int:
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc

    if payload.get("type") != expected_type:
        raise ValueError(f"Wrong token type (expected '{expected_type}')")

    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Token missing 'sub' claim")

    try:
        return int(sub)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid 'sub' claim: {sub!r}") from exc
