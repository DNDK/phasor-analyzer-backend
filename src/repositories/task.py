from .base_repository import BaseRepository

from models.task import Task
from schemas.task import TaskBase

class TaskRepository(BaseRepository[Task]):
    def init_task(self, t_base: TaskBase):
        db_task = Task(**t_base.model_dump(exclude_unset=True))
        self._session.add(db_task)
        self._session.commit()
        self._session.refresh(db_task)

        return db_task
