from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class AnalysisResult(Base):
    """
    Model for Phasor Analysis results.
    Stores dw coefficients, Fourier approximation, tau1/tau2, a1/a2 estimations.
    """

    __tablename__ = "analysis_results"
    __table_args__ = {"schema": "phsch"}

    # meta
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processing_time = Column(Float, nullable=True)  # seconds

    # Ownership via CurveSet (single access path)
    curve_set_id = Column(Integer, ForeignKey("phsch.curve_sets.id"), nullable=False, index=True)
    curve_set = relationship("CurveSet", back_populates="analysis_results")

    # Results
    dw_real = Column(ARRAY(Float))
    dw_imag = Column(ARRAY(Float))

    coeff_v = Column(Float)
    coeff_u = Column(Float)

    tau1 = Column(Float)
    tau2 = Column(Float)

    a1_coeffs = Column(ARRAY(Float))
    a2_coeffs = Column(ARRAY(Float))
    omega = Column(Float)