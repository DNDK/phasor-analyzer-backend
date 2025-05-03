from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    status: TaskStatus
    
    analysis_results_id: int
    analalysis_results: AnalysisResult

    processing_time: float

class Task(TaskCreate):
    id: int