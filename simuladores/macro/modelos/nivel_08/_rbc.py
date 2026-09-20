"""simuladores/macro/modelos/nivel_08/_rbc.py — motor compartido del bloque RBC del nivel 8 (no es un modelo).

RBC log-lineal mínimo: ante productividad a_t, el trabajo responde por
sustitución intertemporal (n = η·a), el producto amplifica
  y = (1 + α_n·η)·a
el consumo suaviza (c = γ·y) y la inversión absorbe el residuo de la
identidad agregada  y = sc·c + si·i:
  i = (y − sc·c)/si   ⇒   σ_i > σ_y > σ_c  (la jerarquía de los hechos)

Procedencia: esqueleto didáctico del RBC (Kydland-Prescott 1982, Long-
Plosser 1983 — menciones) — decisión de diseño sobre conocimiento general.
"""

def sendas(a, eta, alpha_n, gamma, sc, si):
    """Devuelve (y, n, c, i) como respuestas log-lineales a la productividad a."""
    y = (1 + alpha_n * eta) * a
    n = eta * a
    c = gamma * y
    i = (y - sc * c) / si
    return y, n, c, i
