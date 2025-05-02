import numpy as np

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