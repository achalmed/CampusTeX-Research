# m06_mercado_bienes.py — mercado de bienes con inversión sensible a r (nivel 2).
#
# Cruz keynesiana del nivel 1 + la novedad decisiva: I = I0 − b·r.
#   DA = c0 + c1(Y−T) + I0 − b·r + G  ;  equilibrio DA = Y
#   → Y*(r) = [c0 − c1·T + I0 − b·r + G] / (1−c1)
# La tasa de interés r es aquí un PARÁMETRO (exógeno): mover el slider r y ver
# moverse Y* es, literalmente, recorrer la futura curva IS (m07).
#
# Procedencia: síntesis keynesiana de manuales (Hicks-Hansen) — conocimiento
# macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _y_eq(p):
    return (p["c0"] - p["c1"] * p["T"] + p["I0"] - p["b"] * p["r"] + p["G"]) / (1 - p["c1"])


def _curvas(p):
    Y = np.linspace(0, 1200, 300)
    DA = p["c0"] + p["c1"] * (Y - p["T"]) + p["I0"] - p["b"] * p["r"] + p["G"]
    Ye = _y_eq(p)
    return {"lineas": {"DA(Y; r dado)": (Y, DA, config.AZUL2),
                       "recta de 45° (DA = Y)": (Y, Y, config.GRIS)},
            "equilibrio": (Ye, Ye),
            "anotacion": (f"r = {p['r']:.1f}% → I = {p['I0'] - p['b'] * p['r']:,.1f}\n"
                          f"Y*(r) = {Ye:,.1f}")}


def _resultados(p):
    Ye = _y_eq(p)
    I = p["I0"] - p["b"] * p["r"]
    C = p["c0"] + p["c1"] * (Ye - p["T"])
    return {"Y* (dado r)": Ye, "inversión I(r)": I, "consumo C*": C,
            "multiplicador 1/(1−c1)": 1 / (1 - p["c1"]),
            "dY*/dr (sensibilidad a la tasa)": -p["b"] / (1 - p["c1"]),
            "comprobación C+I+G": C + I + p["G"]}


_P0 = {"c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "r": 5.0, "G": 200.0, "T": 100.0}


def _v_equilibrio():
    Ye = _y_eq(_P0)
    DA = _P0["c0"] + _P0["c1"] * (Ye - _P0["T"]) + _P0["I0"] - _P0["b"] * _P0["r"] + _P0["G"]
    return abs(DA - Ye) < 1e-9, f"DA(Y*) = Y* = {Ye:,.1f} (equilibrio exacto)"


def _v_multiplicador():
    dY = _y_eq(dict(_P0, G=_P0["G"] + 1)) - _y_eq(_P0)
    k = 1 / (1 - _P0["c1"])
    return abs(dY - k) < 1e-9, f"ΔY/ΔG = {k:.2f} (el multiplicador de m04 sigue vivo)"


def _v_sensibilidad_r():
    dY = _y_eq(dict(_P0, r=_P0["r"] + 1)) - _y_eq(_P0)
    teorica = -_P0["b"] / (1 - _P0["c1"])
    return abs(dY - teorica) < 1e-9, f"dY/dr = −b/(1−c1) = {teorica:,.1f}: cada punto de tasa cuesta producto"


def _v_inversion_decreciente():
    I5, I7 = _P0["I0"] - _P0["b"] * 5, _P0["I0"] - _P0["b"] * 7
    return I7 < I5, f"I(r) decrece con la tasa ({I5:,.0f} → {I7:,.0f} al subir r de 5 a 7)"


MODELO = Modelo(
    id="m06", nivel=2,
    nombre="Mercado de bienes (inversión sensible a la tasa)",
    xlabel="Producto (Y)", ylabel="Demanda agregada (DA)",
    parametros=[
        Parametro("r", _P0["r"], 0.0, 7.0, 0.5, "Tasa de interés r (exógena aquí)"),
        Parametro("G", _P0["G"], 0, 500, 10, "Gasto público G"),
        Parametro("T", _P0["T"], 0, 400, 10, "Impuestos T"),
        Parametro("c0", _P0["c0"], 0, 300, 10, "Consumo autónomo c0"),
        Parametro("c1", _P0["c1"], 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("I0", _P0["I0"], 0, 400, 10, "Inversión autónoma I0"),
        Parametro("b", _P0["b"], 5, 50, 1, "Sensibilidad de I a r (b)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("El nivel 1 dejó una promesa pendiente: la inversión 'caía del cielo'. "
                  "El primer paso de la síntesis keynesiana (Hicks, Hansen y los manuales "
                  "de posguerra) fue hacerla depender de la tasa de interés: financiar un "
                  "proyecto cuesta r, así que solo se ejecutan los proyectos cuyo "
                  "rendimiento la supera. Con ello el mercado de bienes queda 'abierto' a "
                  "lo que ocurra en el mercado de dinero."),
        autores=("Síntesis keynesiana (Hicks 1937; Hansen años 40-50); la inversión como "
                 "función decreciente de r viene de la eficiencia marginal del capital "
                 "de Keynes (1936)."),
        supuestos=[
            "r es EXÓGENA: este modelo no explica la tasa, la toma dada (la explicará el mercado de dinero, m08).",
            "I = I0 − b·r lineal: b resume cuán sensibles son los proyectos de inversión al costo del crédito.",
            "Precios fijos y capacidad ociosa (herencia del nivel 1).",
            "Consumo keynesiano simple (m03), sin riqueza ni expectativas.",
        ],
        ecuaciones=[
            Ecuacion("I = I_0 - b\\,r", "función de inversión",
                     "I0 es el 'ánimo empresarial' (expectativas, en la trastienda); b traduce la "
                     "tasa de interés en proyectos descartados: con b grande, medio punto de r "
                     "tumba mucha inversión."),
            Ecuacion("DA = c_0 + c_1(Y-T) + I_0 - b\\,r + G", "demanda agregada",
                     "la cruz keynesiana de m05 con el término nuevo −b·r dentro."),
            Ecuacion("Y^*(r) = \\frac{c_0 - c_1 T + I_0 - b\\,r + G}{1-c_1}", "equilibrio dado r",
                     "para CADA tasa hay un equilibrio del mercado de bienes distinto: Y* ya no es "
                     "un número, es una función de r — la semilla de la curva IS."),
        ],
        intuicion=("Mover el slider de r es la mejor manera de entender la curva IS antes "
                   "de dibujarla: r sube → inversión cae → el multiplicador propaga la "
                   "caída → Y* baja. La relación negativa entre r e Y de equilibrio NO es "
                   "una curva de demanda: es una familia de equilibrios del mercado de "
                   "bienes indexada por la tasa."),
        equilibrio=("Para cada r, el equilibrio DA = Y es único y estable (mismo argumento "
                    "de existencias que m05). La estática comparativa clave: dY*/dr = "
                    "−b/(1−c1) — la sensibilidad del producto a la tasa combina el canal "
                    "de inversión (b) con el multiplicador (1/(1−c1))."),
        limitaciones=[
            "No determina r: el modelo queda 'a medias' hasta juntar el mercado de dinero (m08-m10).",
            "Inversión sin expectativas ni acelerador: en la realidad I responde al ciclo (ventas) tanto como a r.",
            "Con shocks grandes la I(r) lineal puede volverse negativa (artefacto, no economía).",
        ],
        evolucion=("m07 recoge todos los pares (r, Y*(r)) de este modelo y los dibuja como "
                   "curva IS. m08-m09 hacen lo simétrico con el dinero, y m10 cierra el "
                   "sistema. Este archivo es el 'laboratorio de derivación' del IS-LM."),
    ),
    escenarios=[
        Escenario("credito_caro", "la tasa sube de 5% a 7%",
                  {"r": 7.0},
                  "cada punto de tasa cuesta 50 de producto (dY/dr = −50): el crédito caro "
                  "descarta proyectos y el multiplicador propaga la caída."),
        Escenario("credito_barato", "la tasa baja de 5% a 3%",
                  {"r": 3.0},
                  "el abaratamiento del crédito estimula inversión y, vía multiplicador, "
                  "el producto: el canal de transmisión de la futura política monetaria."),
        Escenario("expansion_fiscal", "el gasto sube de 200 a 250 con r fija",
                  {"G": 250.0},
                  "con r CONGELADA el multiplicador es el pleno (2.5): compárese con m10, "
                  "donde la respuesta de r se lo come en parte."),
        Escenario("pesimismo_empresarial", "el ánimo inversor cae (I0: 150→130)",
                  {"I0": 130.0},
                  "los 'animal spirits' de Keynes: una caída autónoma de I se multiplica "
                  "igual que un recorte de gasto público."),
    ],
    verificaciones=[
        Verificacion("equilibrio exacto DA(Y*)=Y*", _v_equilibrio),
        Verificacion("multiplicador fiscal pleno con r fija", _v_multiplicador),
        Verificacion("dY*/dr = −b/(1−c1)", _v_sensibilidad_r),
        Verificacion("I(r) decreciente", _v_inversion_decreciente),
    ],
    notas="Mover r con el slider = recorrer la futura curva IS punto a punto (m07).",
)
