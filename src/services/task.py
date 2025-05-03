from schemas.task import TaskCreate, Task

from repositories.task import TaskRepository

class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.repo = task_repository

    async def get_task(self, id) -> Task:
        task = await self.repo.get_by_id(id)
        task_ser = Task.model_validate(task)

        return task_ser

    async def create_task(self, data: TaskCreate) -> Task:
        task = await self.repo.create(data=data.model_dump())

        return Task.model_validate(task)

    # maybe more, for now will be enough