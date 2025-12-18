# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy.orm import DeclarativeBase, Session
# from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine

from fastapi import Depends

from contextlib import asynccontextmanager
from typing import Type, TypeVar, Generator
import os

from models.analysis_results import AnalysisResult
from models.curve_set import CurveSet
from models.task import Task as TaskModel
from models.curve import Curve
from repositories.analysis_results import AnalysisResultsRepository
from repositories.base_repository import BaseRepository
from repositories.curve import CurveRepository
from repositories.curve_set import CurveSetRepository
from repositories.task import TaskRepository
from services.analysis_results import AnalysisResultsService
from services.curve_sets import CurveSetsService
from services.task import TaskService
from sqlalchemy import MetaData, text
import asyncio
from models.base import Base
from contextlib import contextmanager

# Use env override, fall back to in-container Postgres service (with schema phsch)
raw_db_url = os.getenv("DATABASE_URL", "").strip()
# Explicitly force psycopg2 driver if not provided
DATABASE_URL = (
    raw_db_url
    or "postgresql+psycopg2://analyzer:analyzer_pass@db:5432/analyzer?options=-csearch_path%3Dphsch"
)

# One engine/sessionmaker, no duplicates
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Ensure schema exists, then create tables
with engine.begin() as conn:
  conn.execute(text("CREATE SCHEMA IF NOT EXISTS phsch"))
  Base.metadata.create_all(bind=conn)

T = TypeVar('T', bound=BaseRepository)

# Универсальный менеджер сессий
@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Фабрика репозиториев
def get_repository(repo_type: Type[T], model: Type[DeclarativeBase]) -> T:
    with get_db() as session:
        return repo_type(session=session, model=model)

# DI для сервисов
def get_task_servie():
    with get_db() as session:
        task_repo = TaskRepository(session=session, model=TaskModel)
        yield TaskService(task_repo)

def get_curve_set_servie():
    with get_db() as session:
        curve_set_repo = CurveSetRepository(session=session, model=CurveSet)
        curve_repo = CurveRepository(session=session, model=Curve)
        yield CurveSetsService(curve_set_repo, curve_repo)

def get_analysis_results_service():
    with get_db() as session:
        analysis_repo = AnalysisResultsRepository(session=session, model=AnalysisResult)
        curve_set_repo = CurveSetRepository(session=session, model=CurveSet)
        yield AnalysisResultsService(analysis_repo, curve_set_repo)
