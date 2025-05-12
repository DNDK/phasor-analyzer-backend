from pydantic import BaseModel, ConfigDict

from .curve_set import CurveSet


class AnalysisResultCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curve_set_id: int 
    # curve_set: CurveSet

    # Results
    dw_real: list[float]
    dw_imag: list[float]

    coeff_v: float
    coeff_u: float

    tau1: float
    tau2: float

    a1_coeffs: list[float]
    a2_coeffs: list[float]

    omega: float

class AnalysisResult(AnalysisResultCreate):
    id: int

class AnalysisResultPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curve_set_id: int | None = None
    # curve_set: CurveSet

    # Results
    dw_real: list[float] | None = None
    dw_imag: list[float] | None = None

    coeff_v: float | None = None
    coeff_u: float | None

    tau1: float | None
    tau2: float | None

    a1_coeffs: list[float] | None
    a2_coeffs: list[float] | None

    omega: float | None