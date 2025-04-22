from pydantic import BaseModel

class CurveData(BaseModel):
    a1: float
    tau1: float = 1.0
    tau2: float = 3.0
    dt: float = 0.05
    num_points: int = 512
    apply_convolution: bool = True
    add_noise: bool = True
