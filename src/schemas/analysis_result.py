from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AnalysisResultCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curve_set_id: int
    processing_time: Optional[float] = None

    # Results
    dw_real: list[Optional[float]]
    dw_imag: list[Optional[float]]

    coeff_v: Optional[float]
    coeff_u: Optional[float]

    tau1: Optional[float]
    tau2: Optional[float]

    a1_coeffs: list[Optional[float]]
    a2_coeffs: list[Optional[float]]

    omega: Optional[float]


class AnalysisResult(AnalysisResultCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AnalysisResultPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dw_real: Optional[list[Optional[float]]] = None
    dw_imag: Optional[list[Optional[float]]] = None

    coeff_v: Optional[float] = None
    coeff_u: Optional[float] = None

    tau1: Optional[float] = None
    tau2: Optional[float] = None

    a1_coeffs: Optional[list[Optional[float]]] = None
    a2_coeffs: Optional[list[Optional[float]]] = None

    omega: Optional[float] = None
    processing_time: Optional[float] = None
