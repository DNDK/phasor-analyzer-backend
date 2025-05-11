from schemas.task import TaskBase, TaskCreate, Task

from repositories.task import TaskRepository

from fastapi import HTTPException

class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.repo = task_repository

    def get_task(self, id) -> Task | None:
        task = self.repo.get_by_id(id)
        print('\n\n\n\n', task, '\n\n\n\n')
        if task is None:
            raise HTTPException(status_code=404, detail='Task not found')

        task_ser = Task.model_validate(task)

        return task_ser

    def create_task(self, data: TaskCreate) -> Task:
        task = self.repo.create(data=data)

        return Task.model_validate(task)


    def init_task(self, data: TaskBase):
        initted_task_db = self.repo.init_task(data)
        task = Task.model_validate(initted_task_db, from_attributes=True)
        return task
    # maybe more, for now will be enough