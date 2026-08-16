# islm.py — modelo IS-LM (Hicks) para demostración de política macro.
#
# Mercado de bienes (IS):  Y = C + I + G,  C = c0 + c1(Y−T),  I = I0 − b·r
#   → r_IS(Y) = [c0 − c1·T + I0 + G − (1−c1)·Y] / b
# Mercado de dinero (LM):  M/P = k·Y − h·r
#   → r_LM(Y) = (k·Y − M/P) / h
# Equilibrio: intersección. Política fiscal mueve G/T (IS); monetaria mueve M/P (LM).
#
# Referencia teórica: modelo IS-LM estándar (Hicks 1937; cualquier manual de
# macro intermedia). Procedencia: conocimiento macroeconómico general.

import numpy as np

from base import Modelo, Parametro


def _curvas(p):
    Y = np.linspace(0, 1000, 400)
    c0, c1, I0, b, G, T, k, h, MP = (p["c0"], p["c1"], p["I0"], p["b"], p["G"],
                                     p["T"], p["k"], p["h"], p["MP"])
    r_is = (c0 - c1 * T + I0 + G - (1 - c1) * Y) / b
    r_lm = (k * Y - MP) / h
    # equilibrio: (1−c1)Y = c0 − c1T + I0 + G − b·r ; y r=(kY−MP)/h
    # sustituir → resolver Y*
    A = (1 - c1) + b * k / h
    Bc = c0 - c1 * T + I0 + G + b * MP / h
    Y_eq = Bc / A
    r_eq = (k * Y_eq - MP) / h
    return {"lineas": {"IS (bienes)": (Y, r_is, "#2E5496"),
                       "LM (dinero)": (Y, r_lm, "#9E2A2B")},
            "equilibrio": (Y_eq, r_eq)}


MODELO = Modelo(
    nombre="Modelo IS-LM",
    parametros=[
        Parametro("G", 200, 0, 500, 10, "Gasto público G (fiscal)"),
        Parametro("MP", 300, 100, 600, 10, "Oferta real de dinero M/P (monetaria)"),
        Parametro("T", 100, 0, 400, 10, "Impuestos T"),
        Parametro("c1", 0.6, 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("b", 20, 5, 50, 1, "Sensibilidad inversión a r (b)"),
        Parametro("k", 0.5, 0.1, 1.0, 0.05, "Demanda dinero por Y (k)"),
        Parametro("h", 10, 2, 30, 1, "Demanda dinero por r (h)"),
        Parametro("c0", 100, 0, 300, 10, "Consumo autónomo c0"),
        Parametro("I0", 150, 0, 400, 10, "Inversión autónoma I0"),
    ],
    curvas=_curvas,
    notas="Expansión fiscal (↑G) desplaza IS→derecha (↑Y, ↑r). Expansión "
          "monetaria (↑M/P) desplaza LM→derecha (↑Y, ↓r).",
)
