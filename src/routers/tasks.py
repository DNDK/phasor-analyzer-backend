from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from typing import List

from computing import Curve
from typemodels import SignalGenerationParameters

router = APIRouter()

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


@router.post('/create')
async def create_task(request: SignalGenerationParameters):
    pass
    # return {'plots': plots}