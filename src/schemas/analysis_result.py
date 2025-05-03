from pydantic import BaseModel, ConfigDict

from .curve_set import CurveSet


class AnalysisResultCreate(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	curve_set_id: int 
	curve_set: CurveSet

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