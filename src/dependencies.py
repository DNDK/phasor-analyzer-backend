from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from fastapi import Depends

from contextlib import asynccontextmanager
from typing import Type

from models.curve_set import CurveSet
from models.task import Task
from repositories.base_repository import BaseRepository
from repositories.curve_set import CurveSetRepository
from repositories.task import TaskRepository
from services.curve_sets import CurveSetsService
from services.task import TaskService

engine = create_async_engine('postgresql+asyncpg://postgres@localhost:5473/phasordb', echo=True, future=True)

def async_session_generator():
    return async_sessionmaker(engine)

@asynccontextmanager
async def get_session():
    async_session = async_session_generator()
    session = async_session()
    try:
        yield session

    except:
        await session.rollback()

    finally:
        await session.close()

def get_repo(repo: Type[BaseRepository], model: Type[DeclarativeBase], session: AsyncSession = Depends(get_session)):
    return repo(session=session, model=model)


def get_task_servie(task_repo: TaskRepository = Depends(lambda: get_repo(TaskRepository, Task))):
    return TaskService(task_repo)

def get_curve_set_servie(curve_set_repo: CurveSetRepository = Depends(lambda: get_repo(CurveSetRepository, CurveSet))):
    return CurveSetsService(curve_set_repo)

