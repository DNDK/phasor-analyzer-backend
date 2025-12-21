from pydantic import BaseModel, ConfigDict

from .curve_set import CurveSet


class AnalysisResultCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curve_set_id: int

    # Results
    dw_real: list[float | None]
    dw_imag: list[float | None]

    coeff_v: float | None
    coeff_u: float | None

    tau1: float | None
    tau2: float | None

    a1_coeffs: list[float | None]
    a2_coeffs: list[float | None]

    omega: float | None


class AnalysisResult(AnalysisResultCreate):
    id: int


class AnalysisResultPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curve_set_id: int | None = None

    dw_real: list[float | None] | None = None
    dw_imag: list[float | None] | None = None

    coeff_v: float | None = None
    coeff_u: float | None = None

    tau1: float | None = None
    tau2: float | None = None

    a1_coeffs: list[float | None] | None = None
    a2_coeffs: list[float | None] | None = None

    omega: float | None = None
