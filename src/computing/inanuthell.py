import numpy as np
from scipy.signal import convolve
import matplotlib.pyplot as plt

# Параметры
dt = 0.05
j = np.arange(0, 512)  # индексы от 0 до 511
t = j * dt  # массив времени

# 1. Генерация исходной кривой I(j)
a1 = 0.1
I = a1 * np.exp(-t / 1) + (1 - a1) * np.exp(-t / 3)

# 2. Генерация функции отклика g(x)
m = 2.0
sigma = 0.08
g = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-(t - m)**2 / (2 * sigma**2))
# g = g / g.sum()  # Нормировка

# 3. Свёртка (x учитывается автоматически!)
convolved = convolve(I, g, mode='same')

print(convolved)

plt.plot(t, convolved)
plt.show()

# Теперь convolved содержит результат f(t) для всех t = j*dt