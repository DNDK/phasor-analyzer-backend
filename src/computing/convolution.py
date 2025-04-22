from math import pi, sqrt, exp, pow
from scipy.signal import convolve

m=2
sigma=0.08

def g(t):
    val = (1 / ( sqrt(2*pi) * sigma) * exp( -pow(t-m, 2) / (2*pow(sigma, 2))) )

def f(Ivals, gvals):
    return convolve(I, g, mode='same')
