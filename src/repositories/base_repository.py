from sqlalchemy.orm import DeclarativeBase, Session
from pydantic import BaseModel
from abc import ABC, abstractmethod

from typing import Type, TypeVar, Generic

TModel = TypeVar('TModel', bound=DeclarativeBase)
TSchema = TypeVar('TSchema', bound=BaseModel)
TCreateSchema = TypeVar('TCreateSchema', bound=BaseModel)

class BaseRepository(Generic[TModel]):
    def __init__(self, session: Session, model: Type[TModel]):
        self._session = session
        self.model = model

    def get_by_id(self, pk, options=()):
        res = self._session.get(self.model, pk, options=options)

    def create(self, data: BaseModel):
        db_item = self.model(**data.model_dump())
        self._session.add(db_item)
        self._session.commit()
        self._session.refresh(db_item)
        return db_item

    def update(self, pk, data):
        db_item = self._session.get(self.model, pk)
        if not db_item:
            raise ValueError(f'{self.model.__name__} with pk={pk} was not found')

        for key, value in data.items():
            setattr(db_item, key, value)

        self._session.commit()
        self._session.refresh(db_item)
        return db_item

    def delete(self, pk):
        obj = self._session.get(self.model, pk)
        self._session.delete(obj)
        self._session.commit()
