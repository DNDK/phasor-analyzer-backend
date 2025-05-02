import numpy as np
from .irf_function import IRF
from convolution import convolution
from scipy.signal import fftconvolve


class Curve:
    def __init__(self, a1, tau1=1.0, tau2=3.0, dt=0.05, num_points=512, apply_convolution=True, add_noise=True, m=2.0, sigma=0.08, strg=5000, strg_irf=1000):
        self.a1 = a1
        self.a2 = 1.0 - a1
        self.tau1 = tau1
        self.tau2 = tau2
        self.dt = dt
        self.num_points = num_points
        self.t = np.arange(num_points+1) * dt
        self.apply_convolution = apply_convolution
        self.add_noise = add_noise

        # для IRF
        self.m = m
        self.sigma = sigma

        # Хранение данных на каждом этапе генерации
        self.raw = None
        self.convolved = None
        self.normalized = None
        self.noisy = None
        self.IRF = None
        self.scaled_IRF = None
        self.scaled_raw = None

        # суммы для нормировки
        self.strg = strg
        self.strg_irf = strg_irf

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
        return {
            'time_axis': self.t, 
            'irf': self.IRF,
            'raw': self.raw,
            'convolved': self.convolved,
            'noisy': self.noisy,
            'scaled_raw': self.scaled_raw
        }
