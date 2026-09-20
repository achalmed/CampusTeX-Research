"""simuladores/macro/modelos/nivel_11/_episodio.py — motor compartido de los escenarios aplicados (nivel 11).

No es un modelo: es la máquina que reproduce EPISODIOS combinando los
mecanismos de los niveles previos. AD-AS dinámico (m52) de economía abierta,
con secuencias de shocks de demanda y de oferta y una regla de política.

  AD:  Y_t = Y* − α·(π_t − π*) + d_t          (demanda; α = dureza de la regla, m52/m56)
  AS:  π_t = π_{t−1} + λ·(Y_t − Y*) + s_t      (Phillips con inercia, m14/m21)
  reducida:  π_t = [π_{t−1} + λα·π* + λ·d_t + s_t] / (1 + λα)

d_t: shock de demanda por período (COVID, fiscal, salida de capitales…).
s_t: shock de oferta/costos por período (petróleo, alimentos, passthrough…).
Cada modelo del nivel construye sus secuencias d[] y s[] = SU episodio.

Procedencia: AD-AS dinámico de m52 (conocimiento general de manuales
modernos); las calibraciones de cada episodio son didácticas.
"""

import numpy as np


def simular(d, s, alpha, lam, Ystar=100.0, pi_meta=2.0):
    """Devuelve (t, pi, Y) dado el episodio: arrays d[] y s[] de shocks.
    d y s deben tener el mismo largo T+1."""
    T = len(d) - 1
    pi = np.empty(T + 1)
    Y = np.empty(T + 1)
    pe = pi_meta
    for j in range(T + 1):
        pi[j] = (pe + lam * alpha * pi_meta + lam * d[j] + s[j]) / (1 + lam * alpha)
        Y[j] = Ystar - alpha * (pi[j] - pi_meta) + d[j]
        pe = pi[j]
    return np.arange(T + 1), pi, Y


def pulso(T, t0, tamano, dur=1, decae=0.0):
    """Secuencia de shock: `tamano` desde t0 durante `dur` períodos; si
    decae>0, el shock decae geométricamente a razón (1−decae) tras t0."""
    x = np.zeros(int(T) + 1)
    if decae > 0:
        for t in range(int(t0), int(T) + 1):
            x[t] = tamano * (1 - decae) ** (t - t0)
    else:
        x[int(t0):int(t0) + int(dur)] = tamano
    return x


def okun(Y, Ystar=100.0, beta=0.4):
    """Lectura de desempleo vía Okun (m15): Δu ≈ −β·(%ΔY respecto al potencial)."""
    return -beta * (Y - Ystar) / Ystar * 100
