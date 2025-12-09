from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator

class CurveCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time_axis: List[float]

    # Accept raw user traces or generated/scaled variants; at least one should be provided
    raw: Optional[List[float]] = None  # Значения интенсивности [I1, I2, ...]
    raw_scaled: Optional[List[float]] = None

    convolved: Optional[List[float]] = None
    noisy: Optional[List[float]] = None

    irf: Optional[List[float]] = None  # Импульсный отклик (опционально)
    irf_scaled: Optional[List[float]] = None

    @model_validator(mode="after")
    def validate_lengths(self):
        """Ensure provided data vectors match the time axis length and something to analyze exists."""
        provided = [
            ("raw", self.raw),
            ("raw_scaled", self.raw_scaled),
            ("convolved", self.convolved),
            ("noisy", self.noisy),
        ]

        if all(series is None for _, series in provided):
            raise ValueError("At least one of raw, raw_scaled, convolved or noisy must be provided")

        expected_len = len(self.time_axis)
        for name, series in provided:
            if series is not None and len(series) != expected_len:
                raise ValueError(f"{name} length must match time_axis length")

        if self.irf is not None and len(self.irf) != expected_len:
            raise ValueError("irf length must match time_axis length")
        if self.irf_scaled is not None and len(self.irf_scaled) != expected_len:
            raise ValueError("irf_scaled length must match time_axis length")

        return self

class Curve(CurveCreate):
    """
    stores information about a single curve
    """
    id: int

""" UNCOMMENT IF NEEDED """
# class CurvePatch(BaseModel):
#     """
#     Schema for updating a Curve, all fields are optional
#     """
#     time_axis: Optional[List[float]] = None
#     raw: Optional[List[float]] = None
#     raw_scaled: Optional[List[float]] = None
#     convolved: Optional[List[float]] = None
#     noisy: Optional[List[float]] = None
#     irf: Optional[List[float]] = None
#     irf_scaled: Optional[List[float]] = None
