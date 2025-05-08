from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
import enum
from typing import Optional


from .analysis_result import AnalysisResult
from enums.task_status import TaskStatus

class TaskBase(BaseModel):
	created_at: datetime
	status: TaskStatus = TaskStatus.PENDING

class TaskCreate(TaskBase):
    """
    Task creation model
    """
    model_config = ConfigDict(from_attributes=True)
    
    analysis_results_id: Optional[int] = None
    analalysis_results: Optional[AnalysisResult] = None

    processing_time: Optional[float] = None

class Task(TaskCreate):
    id: int
