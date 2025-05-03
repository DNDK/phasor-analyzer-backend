from pydantic import BaseModel, ConfigDict

from .curve import Curve

class CurveSetCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    description: str
    curves: list[Curve]

class CurveSet(CurveSetCreate):
    id: int