"""Repository for User model operations."""

from sqlalchemy import select

from models.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self._session.execute(stmt).scalar_one_or_none()

    def create_user(self, email: str, username: str, hashed_password: str) -> User:
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
        )
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
