from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from enums.curve_set_status import CurveSetStatus
from .base import Base


class CurveSet(Base):
    __tablename__ = "curve_sets"
    __table_args__ = {"schema": "phsch"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, default="Research")
    description = Column(String(1000), nullable=True)
    status = Column(
        Enum(CurveSetStatus, native_enum=True, schema="phsch"),
        nullable=False,
        default=CurveSetStatus.PENDING,
    )
    processing_time = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Ownership
    user_id = Column(Integer, ForeignKey("phsch.users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="curve_sets")

    # Children
    curves = relationship("Curve", back_populates="curve_set", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="curve_set", cascade="all, delete-orphan")