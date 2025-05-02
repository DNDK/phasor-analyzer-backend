from pydantic import BaseModel

from .curve import Curve

class CurveSetCreate(BaseModel):
    description: str

    curves: list[Curve]

class CurveSet(CurveSetCreate):
    id: int