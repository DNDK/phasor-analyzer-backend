from typing import List

from pydantic import BaseModel, model_validator


class UploadedCurve(BaseModel):
    time_axis: List[float]
    intensity: List[float]

    @model_validator(mode="after")
    def validate_lengths(self):
        expected_len = len(self.time_axis)
        if len(self.intensity) != expected_len:
            raise ValueError("intensity length must match time_axis length")
        return self


class UploadedCurveSet(BaseModel):
    """Payload for uploading raw curve data to attach to a task."""
    task_id: int
    description: str = "Uploaded curve set"
    irf: List[float]
    curves: List[UploadedCurve]

    @model_validator(mode="after")
    def validate_curves(self):
        if not self.curves:
            raise ValueError("curves should not be empty")
        if self.irf is None or len(self.irf) == 0:
            raise ValueError("irf must be provided for the curve set")

        expected_len = len(self.irf)
        for curve in self.curves:
            if len(curve.time_axis) != expected_len:
                raise ValueError("irf length must match each curve time_axis length")
        return self
