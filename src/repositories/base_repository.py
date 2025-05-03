from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from abc import ABC, abstractmethod

from typing import Type, TypeVar, Generic

TModel = TypeVar('TModel', bound=DeclarativeBase)
# TSchema = TypeVar('TSchema', bound=BaseModel)
# TCreateSchema = TypeVar('TCreateSchema', bound=BaseModel)

class BaseRepository(Generic[TModel]):
    def __init__(self, session: AsyncSession, model: Type[TModel]):
        self._session = session
        self.model = model

    async def get_by_id(self, pk, options=()):
        res = await self._session.get(self.model, pk, options=options)
        return res

    async def create(self, data):
        db_item = self.model(**data)
        self._session.add(db_item)
        await self._session.commit()
        await self._session.refresh(db_item)
        return db_item

    async def update(self, pk, data):
        db_item = await self._session.get(self.model, pk)
        if not db_item:
            raise ValueError(f'{self.model.__name__} with pk={pk} was not found')

        for key, value in data.items():
            setattr(db_item, key, value)

        await self._session.commit()
        await self._session.refresh(db_item)
        return db_item

    async def delete(self, pk):
        obj = await self._session.get(self.model, pk)
        await self._session.delete(obj)
        await self._session.commit()
