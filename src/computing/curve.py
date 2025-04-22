import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve

# from typemodels import CurveData

from irf_function import fIRF

from pydantic import BaseModel
class CurveData(BaseModel):
    a1: float
    tau1: float = 1.0
    tau2: float = 3.0
    dt: float = 0.05
    num_points: int = 512
    apply_convolution: bool = True
    add_noise: bool = True




class Curve:
    def __init__(self, data: CurveData):
        self.dt = data.dt
        self.num_points = data.num_points
        self.j = np.arange(data.num_points)
        self.t = self.j * data.dt
        
        # Данные на разных этапах обработки
        self.original = None
        self.convolved = None
        self.normalized = None
        self.noisy = None
        
        # Параметры модели
        self.a1 = data.a1
        self.a2 = 1 - data.a1
        self.tau1 = data.tau1
        self.tau2 = data.tau2

        self.apply_convolution = data.apply_convolution
        self.add_noise = data.add_noise

    def generate(self):
        self.tau1 = self.tau1
        self.tau2 = self.tau2
        self.original = self.a1 * np.exp(-self.t / self.tau1) + self.a2 * np.exp(-self.t / self.tau2)
        return self

    def convolution(self, response_func=None, m=2.0, sigma=0.08):
        # if self.original is None:
        #     raise ValueError("Сначала сгенерируйте кривую методом .generate()!")
            
        # if response_func is None:
        #     g = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-(self.t - m)**2 / (2 * sigma**2))
        #     g /= g.sum()
        # else:
        #     g = response_func
        g = fIRF(t=self.t, sigma=sigma, m=m)
        g/=g.sum()
        self.convolved = convolve(self.original, g, mode='same')
        return self

    def normalize(self, target_sum=5000):
        if self.convolved is None:
            raise ValueError("Сначала примените свёртку!")
        self.normalized = (self.convolved / self.convolved.sum()) * target_sum
        return self

    def noise(self, noise_type='poisson'):
        if self.normalized is None:
            raise ValueError("Сначала нормализуйте данные!")
            
        if noise_type == 'poisson':
            self.noisy = np.random.poisson(self.normalized)
        else:
            raise NotImplementedError("Данный тип шума не поддерживается")
        return self
    
    def plot(self):
       self.generate().convolution().normalize().noise()
       plot = {
           'x': self.t,
           'y': self.noisy
       }
       return plot
