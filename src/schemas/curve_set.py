from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from enums.curve_set_status import CurveSetStatus
from .curve import Curve, CurveCreate


class CurveSetCreate(BaseModel):
    """Internal schema used when programmatically creating a curve set."""

    title: str = "Research"
    description: str = "Sample"
    curves: list[CurveCreate] = []


class CurveSetUserDataCreate(BaseModel):
    """Payload for creating a curve set from user-provided curve data."""

    title: str = "Research"
    description: str = "User provided curve set"
    curves: list[CurveCreate]

    @model_validator(mode="after")
    def validate_curves(self):
        if not self.curves:
            raise ValueError("curves should not be empty")
        if any(curve.irf is None for curve in self.curves):
            raise ValueError("irf must be provided for all user-supplied curves")
        return self

    def to_curve_set_create(self) -> "CurveSetCreate":
        return CurveSetCreate(
            title=self.title,
            description=self.description,
            curves=self.curves,
        )


class CurveSet(BaseModel):
    """Full curve set representation returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: CurveSetStatus
    processing_time: Optional[float]
    created_at: datetime
    user_id: int
    curves: list[Curve] = []


class CurveSetSummary(BaseModel):
    """Lightweight curve set representation for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: CurveSetStatus
    processing_time: Optional[float]
    created_at: datetime


class CurveSetPatch(BaseModel):
    """Partial update schema — all fields optional."""

    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CurveSetStatus] = None
    processing_time: Optional[float] = None
