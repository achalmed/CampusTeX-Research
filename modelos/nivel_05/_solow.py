# _solow.py — motor compartido del nivel 5 (crecimiento; no es un modelo).
#
# Solow en tiempo discreto, por trabajador (o por trabajador efectivo):
#   k_{t+1} = k_t + s·A·k_t^α − (n+g+δ)·k_t
# Estado estacionario:  k* = (s·A / (n+g+δ))^{1/(1−α)}
# Velocidad de convergencia local:  λ ≈ (1−α)·(n+g+δ)
#
# Procedencia: Solow (1956, mención) en la formulación estándar de manuales
# de crecimiento — conocimiento general, no verificado contra edición.

import numpy as np


def f(k, A, alpha):
    return A * k ** alpha


def k_estrella(s, A, alpha, ngd):
    """k* del estado estacionario; ngd = n + g + δ (filtraciones del capital)."""
    return (s * A / ngd) ** (1 / (1 - alpha))


def trayectoria(k0, s, A, alpha, ngd, T):
    """Serie k_t desde k0 (T períodos) iterando la acumulación de capital."""
    k = np.empty(int(T) + 1)
    k[0] = k0
    for t in range(int(T)):
        k[t + 1] = k[t] + s * f(k[t], A, alpha) - ngd * k[t]
    return k


def velocidad(alpha, ngd):
    """λ de convergencia local (linealización en torno a k*)."""
    return (1 - alpha) * ngd
