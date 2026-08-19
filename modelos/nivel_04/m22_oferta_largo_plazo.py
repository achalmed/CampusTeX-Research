# m22_oferta_largo_plazo.py — oferta agregada de largo plazo (LRAS) — nivel 4.
#
# El producto potencial sale de la TECNOLOGÍA y los FACTORES, no de la demanda:
#   Y* = A · K^α · L^(1−α)     (Cobb-Douglas; con K=L la base didáctica da Y*=A·K)
# La LRAS es vertical en Y*. Frente a ella, la AD (m20) solo elige el nivel de
# precios: P_LR = (b/h)·M / (Ac·Y* − F). De ahí la NEUTRALIDAD del dinero:
# duplicar M duplica P y no toca Y* (verificable exacto).
#
# Procedencia: dicotomía clásica y función Cobb-Douglas — conocimiento general;
# calibración: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _ystar(p):
    return p["A"] * p["K"] ** p["alpha"] * p["L"] ** (1 - p["alpha"])


def _p_lr(p, M=None):
    return _adas.precio_largo_plazo(p["F"], p["bh"], p["Ac"], M if M is not None else p["M"], _ystar(p))


def _curvas(p):
    Ys = _ystar(p)
    P = np.linspace(1.0, 4.0, 200)
    ad0 = (p["F"] + p["bh"] * p["M"] / P) / p["Ac"]
    ad1 = (p["F"] + p["bh"] * (p["M"] + p["dM"]) / P) / p["Ac"]
    p0, p1 = _p_lr(p), _p_lr(p, p["M"] + p["dM"])
    return {"lineas": {"LRAS: $Y = Y^*$": (np.full(2, Ys), np.linspace(1.0, 4.0, 2), config.GRIS),
                       "AD con $M$": (ad0, P, config.AZUL2),
                       "AD con $M + dM$": (ad1, P, config.ROJO)},
            "puntos": [(Ys, p0, f"$P = {p0:.2f}$"), (Ys, p1, f"$P' = {p1:.2f}$")],
            "anotacion": (f"$Y^* = A\\,K^{{\\alpha}}L^{{1-\\alpha}} = {Ys:,.1f}$\n"
                          f"neutralidad: $P'/P = {p1 / p0:.3f}$ = $(M{{+}}dM)/M = "
                          f"{(p['M'] + p['dM']) / p['M']:.3f}$\n"
                          "el dinero mueve precios, no producto")}


def _resultados(p):
    Ys = _ystar(p)
    return {"Y* (producto potencial)": Ys,
            "P de largo plazo con M": _p_lr(p),
            "P de largo plazo con M+dM": _p_lr(p, p["M"] + p["dM"]),
            "M/P de largo plazo (constante)": p["M"] / _p_lr(p),
            "participación del capital α": p["alpha"]}


_P0 = {"A": 0.7, "K": 1000.0, "L": 1000.0, "alpha": 0.33,
       "M": 590.0, "dM": 118.0, "F": 390.0, "bh": 2.0, "Ac": 1.4}


def _v_neutralidad():
    razon_p = _p_lr(_P0, _P0["M"] + _P0["dM"]) / _p_lr(_P0)
    razon_m = (_P0["M"] + _P0["dM"]) / _P0["M"]
    return abs(razon_p - razon_m) < 1e-12, (f"P escala exactamente con M ({razon_p:.3f}): "
                                            "+20% de dinero = +20% de precios, Y* intacto")


def _v_saldos_constantes():
    mp0 = _P0["M"] / _p_lr(_P0)
    mp1 = (_P0["M"] + _P0["dM"]) / _p_lr(_P0, _P0["M"] + _P0["dM"])
    return abs(mp0 - mp1) < 1e-9, (f"los saldos reales de largo plazo son un ancla: M/P = {mp0:,.1f} "
                                   "con cualquier M (los fija la economía real)")


def _v_elasticidad_capital():
    y0, y1 = _ystar(_P0), _ystar(dict(_P0, K=_P0["K"] * 1.01))
    elast = np.log(y1 / y0) / np.log(1.01)
    return abs(elast - _P0["alpha"]) < 1e-6, (f"elasticidad de Y* respecto a K = α = {elast:.3f}: "
                                              "la puerta al modelo de Solow (m26)")


def _v_tecnologia():
    y0, y1 = _ystar(_P0), _ystar(dict(_P0, A=_P0["A"] * 1.1))
    return abs(y1 / y0 - 1.1) < 1e-12, "+10% de tecnología = +10% de Y*: solo A mueve el potencial uno a uno"


MODELO = Modelo(
    id="m22", nivel=4,
    nombre="Oferta agregada de largo plazo (LRAS)",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dM", _P0["dM"], 0, 400, 10, "Emisión dM (para ver la neutralidad)"),
        Parametro("A", _P0["A"], 0.3, 1.2, 0.05, "Productividad total A"),
        Parametro("K", _P0["K"], 400, 2000, 50, "Stock de capital K"),
        Parametro("L", _P0["L"], 400, 2000, 50, "Trabajo L"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α"),
        Parametro("M", _P0["M"], 300, 900, 10, "Dinero nominal M"),
        Parametro("F", _P0["F"], 200, 600, 10, "Gasto autónomo F (de la AD)"),
        Parametro("bh", _P0["bh"], 0.5, 5.0, 0.25, "Empuje monetario b/h (de la AD)"),
        Parametro("Ac", _P0["Ac"], 0.8, 2.5, 0.05, "Denominador IS-LM Ac (de la AD)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("La otra mitad de la síntesis: a largo plazo, cuando todos los "
                  "contratos se renegociaron y no quedan sorpresas, el producto lo "
                  "determina la CAPACIDAD — tecnología, capital, trabajo — y la "
                  "demanda solo elige a qué precios se compra ese producto. Es la "
                  "dicotomía clásica (variables reales por un lado, nominales por "
                  "otro) que Hume ya intuía y que la evidencia de largo plazo respalda: "
                  "países que emiten mucho tienen más inflación, no más PIB."),
        autores=("Dicotomía clásica (Hume, mención); función Cobb-Douglas (1928, "
                 "mención); la lectura moderna del potencial es la de la contabilidad "
                 "del crecimiento (Solow, m26-m29)."),
        supuestos=[
            "Precios y salarios totalmente flexibles: es el estado FINAL del ajuste, no una descripción del período corriente.",
            "Pleno empleo de los factores: L es la fuerza laboral en su tasa natural (m14).",
            "Cobb-Douglas con rendimientos constantes a escala; α estable (≈1/3 en las cuentas nacionales, mención).",
        ],
        ecuaciones=[
            Ecuacion("Y^* = A\\,K^{\\alpha}\\,L^{1-\\alpha}", "función de producción agregada",
                     "A recoge tecnología e instituciones; α es la participación del capital en el "
                     "ingreso. Es la primera aparición de la función que gobierna el nivel 5."),
            Ecuacion("P_{LR} = \\frac{(b/h)\\,M}{A_c\\,Y^* - F}", "precios de largo plazo",
                     "la AD evaluada en Y*: dado el potencial, el nivel de precios es proporcional a M."),
            Ecuacion("\\frac{P'}{P} = \\frac{M'}{M}, \\quad Y^* \\text{ fijo}", "neutralidad del dinero",
                     "emitir escala lo nominal y no toca lo real: los saldos reales M/P quedan "
                     "anclados por la economía real (verificado exacto)."),
        ],
        intuicion=("A largo plazo la causalidad se invierte: en el corto plazo la "
                   "demanda arrastraba al producto (niveles 1-3); aquí el producto está "
                   "clavado y la demanda solo empuja precios. Toda la macro de corto "
                   "plazo vive en el TRÁNSITO entre un punto y otro — que es "
                   "exactamente lo que m23-m25 modelan."),
        equilibrio=("(Y*, P_LR): Y* del lado real, P_LR del nominal. Es el punto de "
                    "reposo al que el aparato completo converge cuando las "
                    "expectativas terminan de ajustarse (m25)."),
        limitaciones=[
            "¿Cuánto tarda 'el largo plazo'? La LRAS no lo dice — la velocidad es todo el contenido de m25 y del debate de política.",
            "Histéresis: recesiones largas pueden dañar K y L y mover la propia LRAS (la dicotomía no es perfecta).",
            "La neutralidad exige expectativas ajustadas; con inflación alta el señoreaje y sus distorsiones la rompen (m36).",
        ],
        evolucion=("La LRAS abre dos caminos: hacia atrás, cierra el aparato AD-AS "
                   "(m23) como ancla del ajuste; hacia adelante, su interior — qué "
                   "mueve A, K y L — es el nivel 5 completo (Solow m26-m29, "
                   "convergencia m30, crecimiento endógeno m32)."),
    ),
    escenarios=[
        Escenario("emision_20pct", "el banco central emite +20% (dM = 118)",
                  {"dM": 118.0},
                  "P sube exactamente 20% y Y* ni se entera: la neutralidad como "
                  "identidad de largo plazo — contrástese con m23, donde el MISMO dM "
                  "sí mueve Y a corto plazo."),
        Escenario("progreso_tecnico", "la productividad A sube 10%",
                  {"A": 0.77},
                  "el potencial sube 10% y (con M fija) los precios de largo plazo "
                  "BAJAN: el crecimiento es deflacionario si el dinero no acompaña."),
        Escenario("acumulacion_capital", "el stock de capital sube 20%",
                  {"K": 1200.0},
                  "Y* sube solo ~6% (elasticidad α=0.33): acumular factores rinde "
                  "menos que mejorar tecnología — el presagio de Solow (m26)."),
    ],
    verificaciones=[
        Verificacion("neutralidad exacta: P escala con M", _v_neutralidad),
        Verificacion("saldos reales de largo plazo constantes", _v_saldos_constantes),
        Verificacion("elasticidad de Y* respecto a K = α", _v_elasticidad_capital),
        Verificacion("Y* escala uno a uno con la tecnología", _v_tecnologia),
    ],
    notas="El dinero es un velo — pero solo a largo plazo: el corto plazo es m23.",
)
