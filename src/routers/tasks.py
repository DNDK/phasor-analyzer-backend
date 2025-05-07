from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from typing import List

from schemas import Task, TaskCreate


router = APIRouter(prefix='/tasks')

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