from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import select
from pydantic import BaseModel

from typing import Sequence, Type, TypeVar, Generic

TModel = TypeVar('TModel', bound=DeclarativeBase)
TSchema = TypeVar('TSchema', bound=BaseModel)
TCreateSchema = TypeVar('TCreateSchema', bound=BaseModel)

class BaseRepository(Generic[TModel]):
    def __init__(self, session: Session, model: Type[TModel]):
        self._session = session
        self.model = model

    def get_all(self) -> Sequence[TModel]:
        stmt = select(self.model)
        res = self._session.execute(stmt).scalars().all()
        return res

    def get_by_id(self, pk, options=()):
        res = self._session.get(self.model, pk, options=options)
        return res

    def create(self, data: BaseModel):
        db_item = self.model(**data.model_dump())
        self._session.add(db_item)
        self._session.commit()
        self._session.refresh(db_item)
        return db_item

    def update(self, pk, data: BaseModel):
        db_item = self._session.get(self.model, pk)
        if not db_item:
            raise ValueError(f'{self.model.__name__} with pk={pk} was not found')

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_item, key, value)

        self._session.commit()
        self._session.refresh(db_item)
        return db_item

    def delete(self, pk):
        obj = self._session.get(self.model, pk)
        self._session.delete(obj)
        self._session.commit()
