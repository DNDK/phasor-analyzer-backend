from typing import Optional, Union, List
from pydantic import BaseModel, ConfigDict

class CurveCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    time_axis: List[float]

    raw: List[float]  # Значения интенсивности [I1, I2, ...]
    raw_scaled: List[float]

    convolved: List[float]
    noisy: Optional[List[float]] = None

    irf: Optional[List[float]] = None # Импульсный отклик (опционально)
    irf_scaled: Optional[List[float]] = None

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