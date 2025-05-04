from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.ext.declarative import declarative_base

from fastapi import Depends

from contextlib import asynccontextmanager
from typing import Type, TypeVar

from models.curve_set import CurveSet
from models.task import Task as TaskModel
from repositories.analysis_results import AnalysisResultsRepository
from repositories.base_repository import BaseRepository
from repositories.curve_set import CurveSetRepository
from repositories.task import TaskRepository
from services.analysis_results import AnalysisResultsService
from services.curve_sets import CurveSetsService
from services.task import TaskService

engine = create_async_engine('postgresql+asyncpg://phasorer:phasor123@localhost:5432/phasordb', echo=True, future=True)

SessionLocal = async_sessionmaker(bind=engine, autoflush=False)


@asynccontextmanager
async def get_session():
    session = SessionLocal()
    try:
        yield session

    except:
        await session.rollback()

    finally:
        await session.close()

# General function for repo DI

# TRepo = TypeVar('T', bounds=BaseRepository)
T = TypeVar('T', bound=BaseRepository)

async def get_repo(repo: Type[T], model: Type[DeclarativeBase]) -> T:
    async with SessionLocal() as session: 
        return repo(session=session, model=model)

# DI for each service
async def get_task_servie():
    task_repo = await get_repo(TaskRepository, TaskModel)
    return TaskService(task_repo)

async def get_curve_set_servie():
    async with SessionLocal() as session:
        rep = CurveSetRepository(session=session, model=CurveSet)
        srv = CurveSetsService(rep)
        return srv

def get_analysis_results_service(analysis_results_repo: AnalysisResultsRepository = Depends(lambda: get_repo(AnalysisResultsRepository, CurveSet))):
    return AnalysisResultsService(analysis_results_repo)