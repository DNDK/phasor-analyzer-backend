from pydantic import BaseModel, ConfigDict

from .curve import Curve, CurveCreate

class CurveSetBase(BaseModel):
    description: str

class CurveSetCreate(CurveSetBase):
    model_config = ConfigDict(from_attributes=True)
    curves: list[CurveCreate]
    description: str = "Sample"

class CurveSet(CurveSetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    curves: list[Curve]
    task_id: int | None = None
    description: str

class CurveSetPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    curves: list[Curve] | None = None
    task_id: int | None = None
    description: str | None = None