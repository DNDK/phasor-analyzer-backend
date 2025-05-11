from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from models.curve import Curve

from .base import Base

class CurveSet(Base):
    __tablename__ = 'curve_sets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)

    curves = relationship('Curve', back_populates='curve_set')
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship("Task", back_populates="curve_set", uselist=False)