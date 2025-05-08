from schemas.task import TaskBase, TaskCreate, Task

from repositories.task import TaskRepository

class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.repo = task_repository

    def get_task(self, id) -> Task:
        task = self.repo.get_by_id(id)
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