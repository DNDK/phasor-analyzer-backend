from typing import List, Optional

from pydantic import BaseModel, model_validator


class UploadedCurve(BaseModel):
    time_axis: List[float]
    intensity: List[float]
    irf: Optional[List[float]] = None

    @model_validator(mode="after")
    def validate_lengths(self):
        expected_len = len(self.time_axis)
        if len(self.intensity) != expected_len:
            raise ValueError("intensity length must match time_axis length")
        if self.irf is not None and len(self.irf) != expected_len:
            raise ValueError("irf length must match time_axis length")
        return self


class UploadedCurveSet(BaseModel):
    """Payload for uploading raw curve data to attach to a task."""
    task_id: int
    description: str = "Uploaded curve set"
    curves: List[UploadedCurve]

    @model_validator(mode="after")
    def validate_curves(self):
        if not self.curves:
            raise ValueError("curves should not be empty")
        return self
