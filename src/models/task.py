import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .base import Base

from enums.task_status import TaskStatus

class Task(Base):
    __tablename__ = 'tasks'
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(TaskStatus, native_enum=True), default=TaskStatus.PENDING)
    analysis_results_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=True)
    analysis_results = relationship("AnalysisResult")
    processing_time = Column(Float, nullable=True)  # Время выполнения (сек)
    title = Column(String, default='Task')
    curve_set = relationship("CurveSet", back_populates='task', uselist=False)


