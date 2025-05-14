from fastapi import APIRouter, Depends
from pydantic import BaseModel
import uuid
from typing import List

from schemas import Task, TaskCreate
from schemas.task import TaskBase, TaskPatch, TaskStatus

from datetime import datetime

from dependencies import get_task_servie
from services.task import TaskService

tasks_router = APIRouter()

# class TaskData(BaseModel):
#     a1: float
#     tau1: float = 1.0
#     tau2: float = 3.0
#     dt: float = 0.05
#     num_points: int
#     apply_convolution: bool = True
#     add_noise: bool = True

# class Task(TaskData):
#     id: str

# @router.post('/create')
# def handle_task_create(task: TaskCreate):
#     pass

@tasks_router.get('')
@tasks_router.get('/')
def handle_get_all_tasks(service: TaskService = Depends(get_task_servie)):
    tasks = service.get_all_tasks()
    return tasks

@tasks_router.post('/create')
def handle_create_task(task_service: TaskService = Depends(get_task_servie)):
	task_base = TaskBase(created_at = datetime.now(), status = TaskStatus.PENDING)
	initted_task = task_service.init_task(task_base)
	return initted_task

@tasks_router.get("/{id}")
def handle_get_task(id: int, service: TaskService = Depends(get_task_servie)):
    task = service.get_task(id)
    return task

@tasks_router.patch("/{id}")
def handle_patch_task(id: int, data: TaskPatch, service: TaskService = Depends(get_task_servie)):
    task = service.update_task(id, data)
    return task

@tasks_router.delete("/{id}")
def handle_delete_task(id: int, service: TaskService = Depends(get_task_servie)):
    success = service.delete_task(id)
    if success:
        return {"message": "OK"}
    else:
        return {"message": "FAIL"}