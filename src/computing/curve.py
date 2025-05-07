import numpy as np

from schemas.curve import CurveCreate
from .irf_function import IRF
from .convolution import convolution
from scipy.signal import fftconvolve

from schemas.generation_config import CurveConfig
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
