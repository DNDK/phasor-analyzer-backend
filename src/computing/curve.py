# import numpy as np

# from schemas.curve import CurveCreate
# from .irf_function import IRF
# from .convolution import convolution
# from scipy.signal import fftconvolve

# from schemas.generation_config import CurveConfig
# class CurveGenerator:
#     # def __init__(self, a1, tau1=1.0, tau2=3.0, dt=0.05, num_points=512, apply_convolution=True, add_noise=True, m=2.0, sigma=0.08, strg=5000, strg_irf=1000):
#     def __init__(self, config: CurveConfig):
#         self.a1 = config.a1
#         self.a2 = 1.0 - config.a1
#         self.tau1 = config.tau1
#         self.tau2 = config.tau2
#         self.dt = config.dt
#         self.num_points = config.num_points
#         self.t = np.arange(config.num_points+1) * config.dt
#         self.apply_convolution = config.apply_convolution
#         self.add_noise = config.add_noise

#         # для IRF
#         if config.apply_convolution and config.irf_config is None:
#             raise ValueError('irf_config should be defined to apply convolution')
#         self.m = config.irf_config.m if config.irf_config is not None else 0.0
#         self.sigma = config.irf_config.sigma if config.irf_config is not None else 0.0

#         # Хранение данных на каждом этапе генерации
#         self.raw = np.empty(1, dtype=float)
#         self.convolved = np.empty(1, dtype=float)
#         self.normalized = np.empty(1, dtype=float)
#         self.noisy = np.empty(1, dtype=float)
#         self.IRF = np.empty(1, dtype=float)
#         self.scaled_IRF = np.empty(1, dtype=float)
#         self.scaled_raw = np.empty(1, dtype=float)

#         # суммы для нормировки
#         self.strg = config.strg
#         self.strg_irf = config.irf_config.strg if config.irf_config is not None else None

#     def generate(self):
#         """
#             Генерирует изначальные данные для кривой. (Без свертки с IRF и без шума)
#         """
#         I = self.a1*np.exp(-self.t/self.tau1) + self.a2*np.exp(-self.t/self.tau2)
#         self.raw = I
#         return self
    
#     def generate_irf(self):
#         """
#             Генерирует значения IRF, чтобы позже их использовать для свертки
#         """
#         g = IRF(self.t, self.m, self.sigma)
#         self.IRF = g
#         return self

#     def scale(self):
#         self.scaled_IRF = (self.IRF / self.IRF.sum()) * self.strg_irf
#         self.scaled_raw = (self.raw / self.raw.sum()) * self.strg
#         return self


#     def convolve_IRF(self):
#         """
#             Свертка кривой с IRF
#         """
#         # irf_to_convolve = self.IRF if not self.add_noise else self.scaled_IRF
#         if self.apply_convolution:
#             Ig = convolution(self.scaled_raw, self.scaled_IRF, self.dt)[:len(self.scaled_raw)]
#             self.convolved = np.clip(Ig, a_min=0, a_max=None)
#         return self
            

#     def noise(self):
#         """
#             Добавления шума
#         """
#         if self.add_noise:
#             # Масштабирование
#             to_noisify = self.convolved if self.convolved is not None else self.scaled_raw

#             self.noisy = np.random.poisson(to_noisify)
#         return self
    
#     def get_data(self):
#         """
#             Просто получение точек (функция-обертка). 
#             В noisy могут находится как шумные данные, так и данные без шума, или даже без свертки (Если это указано в параметрах конструктора)
#         """
#         self.generate().generate_irf().scale().convolve_IRF().noise()
#         return CurveCreate.model_validate({
#             'time_axis': self.t, 
#             'raw': self.raw,
#             'convolved': self.convolved,
#             'noisy': self.noisy,
#             'raw_scaled': self.scaled_raw,
#             'irf': self.IRF,
#             'irf_scaled': self.scaled_IRF
#         })
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
    task_id: int


SIGMA = 0.08
M = 2.0

def IRF(t, m=M, sigma=SIGMA):
    return (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-((t - m) ** 2) / (2 * sigma ** 2))

def convolution(f1, f2, dX):
    """
    Вычисляет свертку двух функций f1 и f2 с шагом dX
    
    Параметры:
    f1, f2 (array_like): Входные массивы для свертки
    dX (float): Шаг интегрирования
    
    Возвращает:
    numpy.ndarray: Массив результата свертки
    """
    n = len(f1)
    f_conv = np.zeros(n)
    
    for i in range(n-1, 0, -1):  # от length(f1) до 2 в MATLAB -> n-1 до 1 в Python
        f_conv[i] = 0.5 * (f2[0] * f1[i] + f2[i] * f1[0])
        for j in range(1, i):    # от 2 до i-1 в MATLAB -> 1 до i-1 в Python
            f_conv[i] += f1[j] * f2[i - j]
        f_conv[i] *= dX
    
    # f_conv[0] остается 0, как в оригинальной MATLAB-функции
    return f_conv


import numpy as np

# from schemas.curve import CurveCreate
# from .irf_function import IRF
# from .convolution import convolution
from scipy.signal import fftconvolve
# from schemas.generation_config import IrfConfig

# from schemas.generation_config import CurveConfig
class CurveGenerator:
    # def __init__(self, a1, tau1=1.0, tau2=3.0, dt=0.05, num_points=512, apply_convolution=True, add_noise=True, m=2.0, sigma=0.08, strg=5000, strg_irf=1000):
    def __init__(self, config: CurveConfig):
        self.a1 = config.a1
        self.a2 = 1.0 - config.a1
        self.tau1 = config.tau1
        self.tau2 = config.tau2
        self.dt = config.dt
        self.num_points = config.num_points
        self.t = np.arange(config.num_points+1) * config.dt
        self.apply_convolution = config.apply_convolution
        self.add_noise = config.add_noise

        # для IRF
        if config.apply_convolution and config.irf_config is None:
            raise ValueError('irf_config should be defined to apply convolution')
        self.m = config.irf_config.m if config.irf_config is not None else 0.0
        self.sigma = config.irf_config.sigma if config.irf_config is not None else 0.0

        # Хранение данных на каждом этапе генерации
        self.raw = np.empty(1, dtype=float)
        self.convolved = np.empty(1, dtype=float)
        self.normalized = np.empty(1, dtype=float)
        self.noisy = np.empty(1, dtype=float)
        self.IRF = np.empty(1, dtype=float)
        self.scaled_IRF = np.empty(1, dtype=float)
        self.scaled_raw = np.empty(1, dtype=float)

        # суммы для нормировки
        self.strg = config.strg
        self.strg_irf = config.irf_config.strg if config.irf_config is not None else None

    def generate(self):
        """
            Генерирует изначальные данные для кривой. (Без свертки с IRF и без шума)
        """
        I = self.a1*np.exp(-self.t/self.tau1) + self.a2*np.exp(-self.t/self.tau2)
        self.raw = I
        return self
    
    def generate_irf(self):
        """
            Генерирует значения IRF, чтобы позже их использовать для свертки
        """
        g = IRF(self.t, self.m, self.sigma)
        self.IRF = g
        return self

    def scale(self):
        self.scaled_IRF = (self.IRF / self.IRF.sum()) * self.strg_irf
        self.scaled_raw = (self.raw / self.raw.sum()) * self.strg
        return self


    def convolve_IRF(self):
        """
            Свертка кривой с IRF
        """
        # irf_to_convolve = self.IRF if not self.add_noise else self.scaled_IRF
        if self.apply_convolution:
            Ig = convolution(self.scaled_raw, self.scaled_IRF, self.dt)[:len(self.scaled_raw)]
            self.convolved = np.clip(Ig, a_min=0, a_max=None)
        return self
            

    def noise(self):
        """
            Добавления шума
        """
        if self.add_noise:
            # Масштабирование
            to_noisify = self.convolved if self.convolved is not None else self.scaled_raw

            self.noisy = np.random.poisson(to_noisify)
        return self
    
    def get_data(self):
        """
            Просто получение точек (функция-обертка). 
            В noisy могут находится как шумные данные, так и данные без шума, или даже без свертки (Если это указано в параметрах конструктора)
        """
        self.generate().generate_irf().scale().convolve_IRF().noise()
        return CurveCreate.model_validate({
            'time_axis': self.t, 
            'raw': self.raw,
            'convolved': self.convolved,
            'noisy': self.noisy,
            'raw_scaled': self.scaled_raw,
            'irf': self.IRF,
            'irf_scaled': self.scaled_IRF
        })


# gnr = CurveGenerator(config = CurveConfig(a1=0.1, tau1=1.0, tau2=3.0, dt=0.05, num_points=512, apply_convolution=True, add_noise=True, strg=5000, irf_config= IrfConfig(m=1.8, sigma=0.1, strg=10000)))


aas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
crvs = []

for i in aas:
    gnr = CurveGenerator(config = CurveConfig(a1=i, tau1=1.0, tau2=3.0, dt=0.05, num_points=512, apply_convolution=True, add_noise=True, strg=5000, irf_config= IrfConfig(m=1.8, sigma=0.1, strg=10000)))
    crv = gnr.get_data()
    crvs.append(crv)

time = crvs[0].time_axis
irf = crvs[0].irf_scaled

for (i, _) in enumerate(time):
    with open(f'crvs.txt', 'a') as f:
        f.write(f'{float(time[i])} {float(irf[i])}')
        for crv in crvs:
            f.write(f' {float(crv.noisy[i])}')
        f.write('\n')