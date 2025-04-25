import numpy as np

SIGMA = 0.08
M = 2

def IRF(t, m=M, sigma=SIGMA):
    return (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-((t - m) ** 2) / (2 * sigma ** 2))
