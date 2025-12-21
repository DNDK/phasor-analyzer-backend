import numpy as np
from scipy.integrate import simpson

from schemas.curve_set import CurveSet

class PhasorAnalyzer:
    def __init__(self, curve_set: CurveSet):
        """
            Анализатор принимает набор кривых. U и V в классе сейчас вообще не используются, хочу дописать это в дальнейшем
        """
        self.curve_set = curve_set
        self.dws = np.empty(1)
        self.u = 0
        self.v = 0
        self.taus = (None, None)
        self.omega = 2 * np.pi / (curve_set.curves[0].time_axis[-1])
        self.tau1 = 0
        self.tau2 = 0
        self.a = np.empty(1)
        self.a1 = np.empty(1)
        self.a2 = np.empty(1)

    def calc_D(self):
        """
            Для каждой кривой вычисляет преобразование фурье, убирает IRF из кривой. 
            Пока что преобразование фурье считается просто через интегралы методом симпсона, однако можно использовать np.fft.fft
        
            returns array in format of [ [Di] ] for each curve in the set
        """
        dws = []
        for cr in self.curve_set.curves:
            # data = cr
            d = None
            # Deconvolve whenever IRF is provided; intensity choice just sets which signal we use
            needs_deconvolution = cr.irf is not None

            if cr.noisy is not None and len(cr.noisy) >= len(cr.time_axis):
                d = np.array(cr.noisy[:len(cr.time_axis)])
            elif cr.convolved is not None and len(cr.convolved) >= len(cr.time_axis):
                d = np.array(cr.convolved[:len(cr.time_axis)])
            elif cr.raw_scaled is not None and len(cr.raw_scaled) >= len(cr.time_axis):
                d = np.array(cr.raw_scaled[:len(cr.time_axis)])
            elif cr.raw is not None and len(cr.raw) >= len(cr.time_axis):
                d = np.array(cr.raw[:len(cr.time_axis)])
            else:
                raise ValueError("No valid intensity data found for curve")

            if d is None:
                raise ValueError('intensity values ended up to be None. Analysis cannot be performed')

            t = np.array(cr.time_axis)

            # omega = 2*np.pi / (t[-1]-t[0]) # вот так потом буду считать омега
            
            print('\n\n')
            print('DLEN', len(d))
            print('TLEN', len(t))
            print('\n\n')

            numr = simpson((d*np.exp(1j*self.omega*t)), t)
            denr = simpson(d, t)

            if denr == 0:
                raise ValueError("Zero integral for intensity; cannot compute phasor")

            dw = numr/denr

            # irf_y = (1 / (np.sqrt(2 * np.pi) * 0.08)) * np.exp(-((t - 2) ** 2) / (2 * 0.08 ** 2))
            if cr.irf is not None and needs_deconvolution:
                np_irf = np.array(cr.irf[:len(t)])
                irfN = simpson((np_irf * np.exp(1j*self.omega*t)), t)
                irfD = simpson(np_irf, t)
                # irf_y = irf_y / irf_y.sum() * 5000
                # irfN = simpson(irf_y*np.exp(1j*omega*t), t)
                # irfD = simpson(irf_y, t)
                if irfD != 0:
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

        tau1: float = (1-root) / (2*self.omega*self.u)
        tau2: float = (1+root) / (2*self.omega*self.u)

        self.tau1, self.tau2 = tau1, tau2
        return tau1, tau2
    
    def calc_a_coeffs(self) -> tuple[list[float], list[float]]:
        if self.tau1 is None or self.tau2 is None:
            raise ValueError('calc_a should be called after calc_taus')
        
        ak1s = []
        ak2s = []

        for i, _ in enumerate(self.curve_set.curves):
            ak = ( self.omega * (self.tau2 + self.tau1) * self.dws[i].real + (np.pow(self.omega, 2) * self.tau1 * self.tau2 - 1)*self.dws[i].imag - self.omega*self.tau2 ) / (self.omega * (self.tau1 - self.tau2))
            ak2 = (self.tau1 * ak) / (self.tau1*ak + self.tau2*(1-ak))
            ak1 = 1 - ak2
            ak1s.append(ak1)
            ak2s.append(ak2)
        return ak1s, ak2s
    
