"""User service: registration and authentication logic."""

from fastapi import HTTPException, status

from auth.security import hash_password, verify_password, create_access_token, create_refresh_token
from models.user import User
from repositories.user import UserRepository
from schemas.token import TokenPair
from schemas.user import UserPublic, UserRegister


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.repo = user_repo

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, data: UserRegister) -> TokenPair:
        """Create a new user account and return a token pair."""
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        if self.repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken.",
            )

        hashed = hash_password(data.password)
        user = self.repo.create_user(
            email=data.email,
            username=data.username,
            hashed_password=hashed,
        )
        return _issue_token_pair(user.id)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> TokenPair:
        """Verify credentials and return a token pair."""
        # Accept login by username or email
        user = self.repo.get_by_username(username) or self.repo.get_by_email(username)

        # Use constant-time comparison even when user is not found to prevent
        # timing-based user enumeration attacks.
        dummy_hash = "$2b$12$notarealhashandwillalwaysfail000000000000000000000"
        stored_hash = user.hashed_password if user else dummy_hash

        if not verify_password(password, stored_hash) or user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated.",
            )

        return _issue_token_pair(user.id)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    def get_public(self, user_id: int) -> UserPublic:
        user = self.get_by_id(user_id)
        return UserPublic.model_validate(user)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _issue_token_pair(user_id: int) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )
