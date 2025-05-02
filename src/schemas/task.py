from pydantic import BaseModel
from datetime import datetime
import enum


from .analysis_result import AnalysisResult

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskCreate(BaseModel):
    """
    Task creation model
    """
    created_at: datetime
    status: TaskStatus
    
    analysis_results_id: int
    analalysis_results: AnalysisResult

    processing_time: float

class Task(TaskCreate):
    id: int