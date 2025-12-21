from pydantic import BaseModel, ConfigDict, validator
from datetime import date, datetime
import enum
from typing import Optional
from sqlalchemy.orm import DeclarativeBase

from schemas.curve_set import CurveSet, CurveSetCreate


from .analysis_result import AnalysisResult
from enums.task_status import TaskStatus

class TaskBase(BaseModel):
    created_at: datetime
    status: TaskStatus = TaskStatus.PENDING
    title: str = 'Task'

class TaskCreate(TaskBase):
    """
    Task creation model
    """
    model_config = ConfigDict(from_attributes=True)
    
    analysis_results_id: Optional[int] = None
    analalysis_results: Optional[AnalysisResult] = None

    processing_time: Optional[float] = None
    title: str = 'Task'
    curve_set: Optional[CurveSetCreate] = None

class Task(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
    analysis_results_id: Optional[int] = None
    analalysis_results: Optional[AnalysisResult] = None

    processing_time: Optional[float] = None
    title: str = 'Task'
    curve_set: Optional[CurveSet] = None

class TaskPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    analysis_results_id: int | None = None
    analalysis_results: AnalysisResult | None = None

    processing_time: float | None = None
    title: str | None = None
    curve_set: CurveSetCreate | None = None
    status: TaskStatus | None = None
