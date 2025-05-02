import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
	__tablename__ = 'tasks'
	    
	id = Column(Integer, primary_key=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
	analysis_results_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=True)
	analysis_results = relationship("AnalysisResults")
	processing_time = Column(Float, nullable=True)  # Время выполнения (сек)


