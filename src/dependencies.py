import os
from contextlib import contextmanager
from typing import Generator, Type, TypeVar

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from auth.security import decode_access_token
from models.analysis_results import AnalysisResult
from models.base import Base
from models.curve import Curve
from models.curve_set import CurveSet
from models.user import User
from repositories.analysis_results import AnalysisResultsRepository
from repositories.base_repository import BaseRepository
from repositories.curve import CurveRepository
from repositories.curve_set import CurveSetRepository
from repositories.user import UserRepository
from services.analysis_results import AnalysisResultsService
from services.curve_sets import CurveSetsService
from services.user import UserService

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

raw_db_url = os.getenv("DATABASE_URL", "").strip()
DATABASE_URL = (
    raw_db_url
    or "postgresql+psycopg2://analyzer:analyzer_pass@db:5432/analyzer?options=-csearch_path%3Dphsch"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # set True only during development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Ensure schema exists and all tables are created on startup
with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS phsch"))
    Base.metadata.create_all(bind=conn)

T = TypeVar("T", bound=BaseRepository)

# ---------------------------------------------------------------------------
# Session context manager
# ---------------------------------------------------------------------------

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Yield a database session, rolling back on error."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ---------------------------------------------------------------------------
# Service DI factories
# ---------------------------------------------------------------------------

def get_user_service():
    with get_db() as session:
        user_repo = UserRepository(session=session, model=User)
        yield UserService(user_repo)


def get_curve_set_service():
    with get_db() as session:
        curve_set_repo = CurveSetRepository(session=session, model=CurveSet)
        curve_repo = CurveRepository(session=session, model=Curve)
        yield CurveSetsService(curve_set_repo, curve_repo)


def get_analysis_results_service():
    with get_db() as session:
        analysis_repo = AnalysisResultsRepository(session=session, model=AnalysisResult)
        curve_set_repo = CurveSetRepository(session=session, model=CurveSet)
        yield AnalysisResultsService(analysis_repo, curve_set_repo)

# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Validate the Bearer token and return the authenticated User.
    Raises HTTP 401 if the token is missing, malformed, or expired.
    Raises HTTP 403 if the account is deactivated.
    """
    try:
        user_id = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_service.get_by_id(user_id)  # raises 404 if user deleted

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return user
