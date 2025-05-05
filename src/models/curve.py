from sqlalchemy import Column, ForeignKey, Integer, String, Float, ARRAY, null
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .base import Base

class Curve(Base):
    """
    stores information about a single curve
    """
    __tablename__ = 'curves'
        
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_axis = Column(ARRAY(Float))
    
    raw = Column(ARRAY(Float))  # Значения интенсивности [I1, I2, ...]
    raw_scaled = Column(ARRAY(Float))

    convolved = Column(ARRAY(Float), nullable=True)
    noisy = Column(ARRAY(Float), nullable=True)

    irf = Column(ARRAY(Float), nullable=True)  # Импульсный отклик (опционально)
    irf_scaled = Column(ARRAY(Float), nullable=True)

    curve_set_id = Column(Integer, ForeignKey('curve_sets.id'))
    curve_set = relationship('CurveSet', back_populates='curves')
