from sqlalchemy import ARRAY, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class Curve(Base):
    """Stores information about a single decay curve."""

    __tablename__ = "curves"
    __table_args__ = {"schema": "phsch"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_axis = Column(ARRAY(Float))

    raw = Column(ARRAY(Float))       # raw intensity values [I1, I2, ...]
    raw_scaled = Column(ARRAY(Float))

    convolved = Column(ARRAY(Float), nullable=True)
    noisy = Column(ARRAY(Float), nullable=True)

    irf = Column(ARRAY(Float), nullable=True)        # instrument response function
    irf_scaled = Column(ARRAY(Float), nullable=True)

    curve_set_id = Column(Integer, ForeignKey("phsch.curve_sets.id"), nullable=False, index=True)
    curve_set = relationship("CurveSet", back_populates="curves")
