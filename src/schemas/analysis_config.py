from pydantic import BaseModel, model_validator

from schemas.curve import CurveCreate
from schemas.curve_set import CurveSetCreate

class AnalysisConfig(BaseModel):
    task_id: int

class UserDataAnalysisConfig(BaseModel):
    """Payload for processing user-provided curves end-to-end."""
    task_title: str = "User data task"
    description: str = "User provided curve set"
    curves: list[CurveCreate]

    @model_validator(mode="after")
    def validate_curves(self):
        if not self.curves:
            raise ValueError("curves should not be empty")
        if any(curve.irf is None for curve in self.curves):
            raise ValueError("irf must be provided for all curves when processing user data")
        return self

    def to_curve_set_create(self) -> CurveSetCreate:
        return CurveSetCreate(description=self.description, curves=self.curves)
