import numpy as np
from scipy.integrate import simpson

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
            elif cr['convolved'] is not None:
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
            ak = ( self.omega * (self.tau2 + self.tau1) * self.dws[i].real + (np.pow(self.omega, 2) * self.tau1 * self.tau2 - 1)*self.dws[i].imag - self.omega*self.tau2 ) / (self.omega * (self.tau1 - self.tau2))
            ak2 = (self.tau1 * ak) / (self.tau1*ak + self.tau2*(1-ak))
            ak1 = 1 - ak2
            ak1s.append(ak1)
            ak2s.append(ak2)
        return ak1s, ak2s   