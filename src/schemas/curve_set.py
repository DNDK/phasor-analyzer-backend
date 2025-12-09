from pydantic import BaseModel, ConfigDict, model_validator

from .curve import Curve, CurveCreate

class CurveSetBase(BaseModel):
    description: str

class CurveSetCreate(CurveSetBase):
    model_config = ConfigDict(from_attributes=True)
    curves: list[CurveCreate]
    description: str = "Sample"

class CurveSetUserDataCreate(BaseModel):
    """Payload for attaching user-provided curves to an existing task."""
    task_id: int
    description: str = "User provided curve set"
    curves: list[CurveCreate]

    @model_validator(mode="after")
    def validate_curves(self):
        if not self.curves:
            raise ValueError("curves should not be empty")
        return self

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
