from pydantic import BaseModel
from typing import Optional

class IrfConfig(BaseModel):
	m: float = 2.0
	sigma: float = 0.08
	strg: float = 10000 # scaling

class SingleSetShared(BaseModel):
	tau1: float = 1.0
	tau2: float = 3.0
	dt: float = 0.05
	num_points: int = 512
	apply_convolution: bool = True
	add_noise: bool = True
	strg: float = 5000 # scaling, controls noise
	irf_config: Optional[IrfConfig]

class CurveConfig(SingleSetShared):
	a1: float
	# tau1: float = 1.0
	# tau2: float = 3.0
	# dt: float = 0.05
	# num_points: int = 512
	# apply_convolution: bool = True
	# add_noise: bool = True
	# strg: float = 5000 # scaling, controls noise
	# irf_config: Optional[IrfConfig]

class CurveSetConfig(SingleSetShared):
	a1_coeffs: list[float]
	num_curves: float = 10