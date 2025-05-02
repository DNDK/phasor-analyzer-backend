from pydantic import BaseModel, Field, validator
from typing import Optional

class SignalGenerationParameters(BaseModel):
    a1: float = Field(..., description="Amplitude parameter")
    tau1: float = Field(1.0, gt=0, description="First time constant")
    tau2: float = Field(3.0, gt=0, description="Second time constant")
    dt: float = Field(0.05, gt=0, description="Time step")
    num_points: int = Field(512, gt=0, description="Number of points in the signal")
    apply_convolution: bool = Field(True, description="Whether to apply convolution")
    add_noise: bool = Field(True, description="Whether to add noise")
    m: float = Field(2.0, description="Noise mean")
    sigma: float = Field(0.08, gt=0, description="Noise standard deviation")
    strg: float = Field(5000, gt=0, description="Signal strength parameter")
    strg_irf: float = Field(1000, gt=0, description="IRF strength parameter")

    @validator('tau2')
    def validate_tau2_greater_than_tau1(cls, v, values):
        if 'tau1' in values and v <= values['tau1']:
            raise ValueError('tau2 must be greater than tau1')
        return v

    class Config:
        schema_extra = {
            "example": {
                "a1": 1.0,
                "tau1": 1.0,
                "tau2": 3.0,
                "dt": 0.05,
                "num_points": 512,
                "apply_convolution": True,
                "add_noise": True,
                "m": 2.0,
                "sigma": 0.08,
                "strg": 5000,
                "strg_irf": 1000
            }
        }