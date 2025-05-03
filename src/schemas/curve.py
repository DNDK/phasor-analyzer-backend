from pydantic import BaseModel, ConfigDict
from typing import Union

class CurveCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    time_axis: list[float]
    
    raw: list[float]  # Значения интенсивности [I1, I2, ...]
    raw_scaled: list[float]

    convolved: list[float] 
    noisy: Union[list[float], None]

    irf: Union[list[float], None] # Импульсный отклик (опционально)
    irf_scaled: Union[list[float], None]

class Curve(CurveCreate):
    """
    stores information about a single curve
    """
    id: int