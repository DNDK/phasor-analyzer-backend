import numpy as np

import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
from scipy.integrate import trapezoid, simpson
from typing import TypedDict

def IRF(t, m, sigma):
    return (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-((t - m) ** 2) / (2 * sigma ** 2))

"""
    Класс Curve генерирует кривую затухания. Добавление IRF и Шума в кривую управляется параметрами в конструкторе
"""
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
            Ig = fftconvolve(self.scaled_raw, self.scaled_IRF, mode='full')[:len(self.scaled_raw)] * self.dt
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

class PhasorAnalyzer:
    def __init__(self, curves_set: list[dict[str, np.ndarray]]):
        """
            Анализатор принимает набор кривых. U и V в классе сейчас вообще не используются, хочу дописать это в дальнейшем
        """
        self.curves_set = curves_set
        self.dws = None
        self.u = None
        self.v = None
        self.taus = (None, None)
        self.omega = 2 * np.pi / (curves_set[0]['time_axis'][-1])
        self.tau1 = None
        self.tau2 = None
        self.a = None
        self.a1 = None
        self.a2 = None

    def calc_D(self):
        """
            Для каждой кривой вычисляет преобразование фурье, убирает IRF из кривой. 
            Пока что преобразование фурье считается просто через интегралы методом симпсона, однако можно использовать np.fft.fft
        
            returns array in format of [ [Di] ] for each curve in the set
        """
        dws = []
        for cr in self.curves_set:
            # data = cr
            d = None
            needs_deconvolution = True

            if cr['noisy'] is not None:
                d = cr['noisy']
            elif cr['convolved']:
                d = cr['convolved']
            else:
                needs_deconvolution = False
                d = cr['scaled_raw']

            if d is None:
                raise ValueError('intensity values ended up to be None. Analysis cannot be performed')

            t = cr['time_axis']

            # omega = 2*np.pi / (t[-1]-t[0]) # вот так потом буду считать омега
            
            numr = simpson((d*np.exp(1j*self.omega*t)), t)
            denr = simpson(d, t)

            dw = numr/denr

            # irf_y = (1 / (np.sqrt(2 * np.pi) * 0.08)) * np.exp(-((t - 2) ** 2) / (2 * 0.08 ** 2))
            if cr['irf'] is not None and needs_deconvolution:
                irfN = simpson((cr['irf'] * np.exp(1j*self.omega*cr['time_axis'])), t)
                irfD = simpson(cr['irf'], t)
                # irf_y = irf_y / irf_y.sum() * 5000
                # irfN = simpson(irf_y*np.exp(1j*omega*t), t)
                # irfD = simpson(irf_y, t)
                irf_FOURIER = irfN/irfD
                dw/=irf_FOURIER

            dws.append(dw)
        self.dws = dws
        return dws
    

    def approx_fourier(self) -> tuple[float, float]:
        """ returns (v, u) coefficents and saves them as class properties"""
        if self.dws is None:
            raise ValueError('approx_fourier should be called after calc_D')
        
        # approx Dws
        x = [dw.real for dw in self.dws]
        y = [dw.imag for dw in self.dws]

        A = np.vstack([x, np.ones(len(x))]).T
        v, u = np.linalg.lstsq(A, y, rcond=None)[0]
        
        self.v, self.u = v, u

        return v, u
    
    def calc_taus(self):
        if self.u is None or self.v is None:
            raise ValueError('calc_taus should be called after approx_fourier')
        root = np.sqrt(1-4*self.u*(self.u+self.v))

        tau1 = (1-root) / (2*self.omega*self.u)
        tau2 = (1+root) / (2*self.omega*self.u)

        self.tau1, self.tau2 = tau1, tau2
        return tau1, tau2
    
    def calc_a_coeffs(self) -> tuple[list[float], list[float]]:
        if self.tau1 is None or self.tau2 is None:
            raise ValueError('calc_a should be called after calc_taus')
        
        ak1s = []
        ak2s = []

        for i, curve in enumerate(self.curves_set):
            ak = ( len(self.curves_set) * self.omega * (self.tau2 + self.tau1) * self.dws[i].real + (np.pow(self.omega, 2) * self.tau1 * self.tau2 - 1)*self.dws[i].imag - self.omega*self.tau2 ) / (self.omega * (self.tau1 - self.tau2))
            ak2 = (self.tau1 * ak) / (self.tau1*ak + self.tau2*(1-ak))
            ak1 = 1 - ak2
            ak1s.append(ak1)
            ak2s.append(ak2)
        return ak1s, ak2s    
        
""" Демонстрация """


# пример кривой
crv = Curve(a1=0.1, add_noise=False, apply_convolution=False)
data = crv.get_data()
plt.plot(data['time_axis'], data['scaled_raw'])
plt.show()

# инициализация массива a1 для каждой кривой в наборе.
CURVE_NUM = 100 # кол-во кривых
a1s = np.linspace(0.01, 0.99, CURVE_NUM)
curves = [Curve(a1=a1, apply_convolution=False, add_noise=False).get_data() for a1 in a1s]
# [plt.plot(cr.get_data()['time_axis'], cr.get_data()['noisy']) for cr in curves]

# инициализация анализатора и получение массива коэффициентов фурье
analyzer = PhasorAnalyzer(curves_set=curves)
dws = analyzer.calc_D()

# подготовка данных для отрисовки на графике
x = [dw.real for dw in dws]
y = [dw.imag for dw in dws]

# линейная аппроксимация 
# y = Ap, 
           
# где A = ( x ), p = (m  c)
#         ( 1 )

A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y)[0]

appr_x = np.linspace(0, 20, 40)

# отрисовка данных 
plt.figure(figsize=(8, 8))
plt.xlim(-0.5, 1.5)
plt.ylim(0, 0.75)
plt.scatter(x, y)
plt.plot(appr_x, m*appr_x+c)
center_x, center_y = 0.5, 0
radius = 0.5

# Углы от 0 до π для верхней полуокружности
theta = np.linspace(0, np.pi, 100)

# Вычисление координат
ax = center_x + radius * np.cos(theta)
ay = center_y + radius * np.sin(theta)

# Построение графика
plt.plot(ax, ay)
plt.gca().set_aspect('equal')  # Сохраняем пропорции
plt.grid(True)
plt.title('Полуокружность (верхняя)')
plt.show()



# грубый подсчёт, который нужно заменить
analyzer.approx_fourier()
tau1, tau2 = analyzer.calc_taus()
ak1s, ak2s = analyzer.calc_a_coeffs()

print(f'tau1: {tau1}; tau2: {tau2}')
print(f'a11: {ak1s[0]}; a21: {ak2s[0]}')

