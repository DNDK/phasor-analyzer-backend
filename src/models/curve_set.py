from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from models.curve import Curve

Base = declarative_base()

class CurveSet(Base):
    __tablename__ = 'curve_sets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)

    curves = relationship(Curve)
