# _adas.py — solver compartido del aparato AD-AS del nivel 4 (no es un modelo).
#
# AD derivada de IS-LM (m20):   Y = [F + (b/h)·M/P] / Ac
#   con F = c0 − c1·T + I0 + G  (gasto autónomo, incluye shocks fiscales)
#       Ac = (1−c1) + b·k/h    (el denominador del IS-LM, m10)
# SRAS (m21):                   P = Pe_ef + λ·(Y − Y*)
#   con Pe_ef = Pe + ds        (expectativas + shock de costos)
#
# Sustituyendo P(Y) en la AD queda una cuadrática en Y (el término M/P la
# vuelve no lineal). Se toma la raíz positiva.

def equilibrio_corto(F, bh, Ac, M, Pe_ef, lam, Ystar):
    """Equilibrio AD ∩ SRAS: devuelve (Y, P). Exacto (raíz de la cuadrática)."""
    q = Pe_ef - lam * Ystar
    a2 = Ac * lam
    a1 = Ac * q - F * lam
    a0 = -(F * q + bh * M)
    Y = (-a1 + (a1 * a1 - 4 * a2 * a0) ** 0.5) / (2 * a2)
    return Y, Pe_ef + lam * (Y - Ystar)


def precio_largo_plazo(F, bh, Ac, M, Ystar):
    """P que sitúa la AD sobre la LRAS (Y = Y*): Ac·Y* = F + bh·M/P."""
    return bh * M / (Ac * Ystar - F)


def estructura(p):
    """(F, bh, Ac) desde los parámetros estructurales del IS-LM subyacente."""
    F = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"]
    return F, p["b"] / p["h"], (1 - p["c1"]) + p["b"] * p["k"] / p["h"]
