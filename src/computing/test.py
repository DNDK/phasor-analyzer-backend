import numpy as np
import matplotlib.pyplot as plt

# Зафиксируем seed для воспроизводимости
np.random.seed(42)

# =======================================
# Класс для симуляции кривых затухания с учетом IRF и пуассоновского шума
# =======================================
class DecaySimulator:
    def __init__(self, 
                 N=512, 
                 delta_t=0.05, 
                 true_tau1=1.0, 
                 true_tau2=3.0, 
                 a1_values=None,
                 IRF_m=2.0, 
                 IRF_sigma=0.08,
                 Strg_curve=5000,   # Увеличиваем для лучшего SNR
                 Strg_IRF=5000):
        """
        N           - число отсчётов (карманов)
        delta_t     - шаг по времени (нс)
        true_tau1   - истинное τ₁ (нс)
        true_tau2   - истинное τ₂ (нс)
        a1_values   - массив значений a₁ (если None, np.linspace(0.1,0.9,9))
        IRF_m       - задержка IRF (m) (нс)
        IRF_sigma   - стандартное отклонение IRF (σ)
        Strg_curve  - суммарное значение для нормировки кривых
        Strg_IRF    - суммарное значение для нормировки IRF
        """
        self.N = N
        self.delta_t = delta_t
        self.T_total = N * delta_t
        self.t = np.arange(0, self.T_total, delta_t)
        self.true_tau1 = true_tau1
        self.true_tau2 = true_tau2
        self.a1_values = np.linspace(0.1, 0.9, 9) if a1_values is None else a1_values
        self.IRF_m = IRF_m
        self.IRF_sigma = IRF_sigma
        self.Strg_curve = Strg_curve
        self.Strg_IRF = Strg_IRF
        self.curves = None  # зашумленные кривые с учетом свертки
        self.IRF = None     # функция отклика

    def simulate_IRF(self):
        """
        IRF: g(t) = (1/(√(2π)*σ)) * exp( - (t - m)²/(2σ²) )
        Нормируем так, чтобы сумма значений равнялась Strg_IRF.
        """
        g = (1/(np.sqrt(2*np.pi)*self.IRF_sigma)) * np.exp(-((self.t - self.IRF_m)**2) / (2*self.IRF_sigma**2))
        g_norm = g / np.sum(g) * self.Strg_IRF
        self.IRF = g_norm
        return self.IRF

    def simulate_curves(self):
        """
        Генерирует кривые I(t) = a1*exp(-t/τ1) + (1-a1)*exp(-t/τ2).
        Затем сворачивает с IRF, нормирует и добавляет пуассоновский шум.
        """
        if self.IRF is None:
            self.simulate_IRF()

        def simulate_decay(a1, tau1, tau2, t):
            return a1 * np.exp(-t/tau1) + (1 - a1) * np.exp(-t/tau2)

        curves_clean = [simulate_decay(a, self.true_tau1, self.true_tau2, self.t) 
                        for a in self.a1_values]
        curves_conv = []
        for curve in curves_clean:
            # Свертка (обрезаем до длины исходного массива)
            f_full = np.convolve(curve, self.IRF, mode='full')
            f = f_full[:len(curve)]
            # Нормировка
            f_norm = f / np.sum(f) * self.Strg_curve
            # Пуассоновский шум
            f_noisy = np.random.poisson(f_norm)
            curves_conv.append(f_noisy.astype(float))
        self.curves = curves_conv
        return self.curves

    def get_time_axis(self):
        return self.t

# =======================================
# Класс для глобального анализа методом фазовых векторов с учетом IRF
# =======================================
class PhasorAnalyzer:
    def __init__(self, curves, delta_t, N, IRF_m, IRF_sigma):
        """
        curves     - список зашумленных кривых (numpy массивы)
        delta_t    - шаг по времени (нс)
        N          - число отсчётов
        IRF_m      - задержка IRF (m) (нс)
        IRF_sigma  - стандартное отклонение IRF (σ)
        """
        self.curves = curves
        self.N = N
        self.delta_t = delta_t
        self.T_total = N * delta_t
        self.omega = 2 * np.pi / self.T_total  # ω = 2π/T_total
        self.IRF_m = IRF_m
        self.IRF_sigma = IRF_sigma

    def compute_phasors(self):
        """
        Классический phasor в частотной области:
          G = (1/∑I) * ∑ I(k) cos(ω·k·dt)
          S = (1/∑I) * ∑ I(k) sin(ω·k·dt)
        Коррекция IRF: делим (G + iS) на E1 = exp(-ω²σ²/2)*exp(jωm).
        Возвращаем G, S (оба положительные при «стандартной» экспоненте).
        """
        def compute_phasor(signal):
            t_idx = np.arange(self.N)
            # Вычисляем "непрерывный" phasor
            I_sum = np.sum(signal)
            G_ = np.sum(signal * np.cos(self.omega * t_idx * self.delta_t)) / I_sum
            S_ = np.sum(signal * np.sin(self.omega * t_idx * self.delta_t)) / I_sum
            return (G_ + 1j*S_)

        phasors = np.array([compute_phasor(curve) for curve in self.curves])
        # Коррекция IRF
        E1 = np.exp(- (self.omega**2 * self.IRF_sigma**2)/2) * np.exp(1j * self.omega * self.IRF_m)
        phasors_corr = phasors / E1
        # Здесь S = Im(phasors_corr) может получиться > 0, что соответствует классической форме
        G = np.real(phasors_corr)
        S = np.imag(phasors_corr)
        return G, S, phasors_corr

    def global_analysis(self):
        """
        1) Вычисляем phasors (G,S).
        2) Линейная регрессия: S = mG + c.
        3) Пересечение с полуокружностью (G-0.5)² + S² = 0.25.
        4) τ = S_int / (ω·G_int).
        5) Для каждой кривой: α = [ ω(τ1+τ2)*G + (ω²τ1τ2 - 1)*S - ωτ2 ] / [ ω(τ1 - τ2) ].
        Если дискриминант < 0, берём альтернативный метод (τᵢ = Sᵢ/(ω·Gᵢ)).
        """
        G, S, _ = self.compute_phasors()
        # Линейная регрессия
        m, c = np.polyfit(G, S, 1)

        A_coef = 1 + m**2
        B_coef = 2*m*c - 1
        C_coef = c**2
        disc = B_coef**2 - 4*A_coef*C_coef

        if disc < 0:
            print("Warning: отрицательный дискриминант, используем альтернативный метод.")
            tau_candidates = S / (self.omega * G)
            recovered_tau1 = np.nanmin(tau_candidates)
            recovered_tau2 = np.nanmax(tau_candidates)
        else:
            sqrt_disc = np.sqrt(disc)
            G_int1 = (-B_coef + sqrt_disc) / (2*A_coef)
            G_int2 = (-B_coef - sqrt_disc) / (2*A_coef)
            S_int1 = m*G_int1 + c
            S_int2 = m*G_int2 + c
            tau_est1 = S_int1 / (self.omega * G_int1) if G_int1 != 0 else np.nan
            tau_est2 = S_int2 / (self.omega * G_int2) if G_int2 != 0 else np.nan
            # Берём меньшую как τ1, большую как τ2
            if tau_est1 < tau_est2:
                recovered_tau1, recovered_tau2 = tau_est1, tau_est2
            else:
                recovered_tau1, recovered_tau2 = tau_est2, tau_est1

        # Для каждой кривой вычисляем α
        fractions = []
        for Gi, Si in zip(G, S):
            alpha_i = (self.omega*(recovered_tau1+recovered_tau2)*Gi 
                       + (self.omega**2*recovered_tau1*recovered_tau2 - 1)*Si 
                       - self.omega*recovered_tau2) \
                      / (self.omega*(recovered_tau1 - recovered_tau2))
            fractions.append(alpha_i)
        fractions = np.array(fractions)
        return recovered_tau1, recovered_tau2, fractions, G, S, m, c

    def analyze(self, plot=True):
        recovered_tau1, recovered_tau2, fractions, G, S, m, c = self.global_analysis()
        print(f"Линейная регрессия: S = {m:.3f} * G + {c:.3f}")
        print(f"Восстановленные времена затухания: τ₁ = {recovered_tau1:.3f} нс, τ₂ = {recovered_tau2:.3f} нс")
        print("Доли компоненты с τ₂ для каждой кривой:")
        for i, alpha in enumerate(fractions):
            print(f"  Кривая {i+1}: α = {alpha:.3f}")
        avg_fraction = np.mean(fractions)
        print(f"Восстановленная средняя доля компоненты с τ₂ (α): {avg_fraction:.3f}")
        
        # Эффективное время затухания для каждой кривой, рассчитанное напрямую через фазор:
        tau_effective_direct = S / (self.omega * G)
        print("Эффективное время затухания для каждой кривой (tau_eff = S/(ω·G)):")
        for i, tau in enumerate(tau_effective_direct):
            print(f"  Кривая {i+1}: τ_eff = {tau:.3f} нс")
        
        # Альтернативно, вычисляем τ_eff как взвешенное среднее глобальных τ:
        tau_eff_mixture = (1 - fractions) * recovered_tau1 + fractions * recovered_tau2
        print("Эффективное время затухания для каждой кривой (τ_eff = (1-α)·τ₁ + α·τ₂):")
        for i, tau in enumerate(tau_eff_mixture):
            print(f"  Кривая {i+1}: τ_eff = {tau:.3f} нс")
        
        if plot:
            plt.figure(figsize=(6,6))
            plt.scatter(G, S, color='blue', label='Измеренные phasors')
            # Отрисовка универсальной полуокружности
            theta = np.linspace(0, np.pi, 200)
            G_circle = 0.5 + 0.5 * np.cos(theta)
            S_circle = 0.5 * np.sin(theta)
            plt.plot(G_circle, S_circle, 'k--', label='Универсальная полуокружность')
            # Линия регрессии
            G_line = np.linspace(min(G) - 0.05, max(G) + 0.05, 100)
            S_line = m * G_line + c
            plt.plot(G_line, S_line, 'r-', label='Линейная регрессия')
            plt.xlabel('G')
            plt.ylabel('S')
            plt.title('Phasor plot и глобальный анализ')
            plt.legend()
            plt.axis('equal')
            plt.show()
        
        # Результаты возвращаются в виде словаря
        return {"τ₁": recovered_tau1, 
                "τ₂": recovered_tau2, 
                "fractions": fractions, 
                "tau_effective_direct": tau_effective_direct,
                "tau_eff_mixture": tau_eff_mixture}



# =======================================
# Демонстрация работы
# =======================================
if __name__ == "__main__":
    simulator = DecaySimulator()
    curves = simulator.simulate_curves()
    t = simulator.get_time_axis()

    # (Опционально) посмотрим на сгенерированные кривые
    plt.figure(figsize=(10,6))
    for i, curve in enumerate(curves):
        plt.plot(t, curve, label=f'Кривая {i+1}')
    plt.xlabel('Время (нс)')
    plt.ylabel('Интенсивность')
    plt.title('Симулированные кривые (IRF + шум)')
    plt.legend()
    plt.show()

    analyzer = PhasorAnalyzer(curves, 
                              delta_t=simulator.delta_t, 
                              N=simulator.N, 
                              IRF_m=simulator.IRF_m, 
                              IRF_sigma=simulator.IRF_sigma)
    results = analyzer.analyze(plot=True)

    print(results)

    # Истинные доли компоненты с τ₂ для каждой кривой (1 - a1)
    true_fractions = 1 - simulator.a1_values
    print("Истинные доли компоненты с tau2 для каждой кривой:")
    for i, frac in enumerate(true_fractions):
        print(f"  Кривая {i+1}: {frac:.3f}")
