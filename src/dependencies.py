# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy.orm import DeclarativeBase, Session
# from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine

from fastapi import Depends

from contextlib import asynccontextmanager
from typing import Type, TypeVar

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
from sqlalchemy import MetaData
import asyncio
from models.base import Base

engine = create_engine('postgresql://phasorer:phasor123@localhost:5432/phasordb?options=-c%20search_path%3Dphsch', echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

meta = MetaData()

meta.create_all(engine)

Base.metadata.create_all(bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session

    except:
        session.rollback()

    finally:
        session.close()

# General function for repo DI

# TRepo = TypeVar('T', bounds=BaseRepository)
T = TypeVar('T', bound=BaseRepository)

def get_repo(repo: Type[T], model: Type[DeclarativeBase]) -> T:
    with SessionLocal() as session: 
        return repo(session=session, model=model)

# DI for each service
def get_task_servie():
    task_repo = get_repo(TaskRepository, TaskModel)
    return TaskService(task_repo)

def get_curve_set_servie():
    with SessionLocal() as session:
        rep = CurveSetRepository(session=session, model=CurveSet)
        crep = CurveRepository(session=session, model=Curve)
        srv = CurveSetsService(rep, crep)
        return srv

def get_analysis_results_service(
    analysis_results_repo: AnalysisResultsRepository = Depends(lambda: get_repo(AnalysisResultsRepository, AnalysisResult)),
    curve_set_repo: CurveSetRepository = Depends(lambda: get_repo(CurveSetRepository, CurveSet))
    ):
    return AnalysisResultsService(analysis_results_repo, curve_set_repo)