# m07_curva_is.py — curva IS: todos los equilibrios del mercado de bienes (nivel 2).
#
# Recoge los pares (Y, r) donde el mercado de bienes (m06) está en equilibrio:
#   r_IS(Y) = [c0 − c1·T + I0 + G − (1−c1)·Y] / b        (pendiente −(1−c1)/b)
# Se grafican DOS curvas IS: la base (G, T, I0) y una alternativa desplazada por
# (dG, dT, dI0) — así se VE cuánto y hacia dónde mueve la IS cada shock:
#   ΔY|_r = k·dG ,  −c1·k·dT ,  k·dI0   con  k = 1/(1−c1)
#
# Procedencia: Hicks (1937) y manuales de macro intermedia — conocimiento
# macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _r_is(Y, G, T, I0, p):
    return (p["c0"] - p["c1"] * T + I0 + G - (1 - p["c1"]) * Y) / p["b"]


def _curvas(p):
    Y = np.linspace(200, 1200, 300)
    base = _r_is(Y, p["G"], p["T"], p["I0"], p)
    alt = _r_is(Y, p["G"] + p["dG"], p["T"] + p["dT"], p["I0"] + p["dI0"], p)
    k = 1 / (1 - p["c1"])
    dY = k * p["dG"] - p["c1"] * k * p["dT"] + k * p["dI0"]
    return {"lineas": {"IS base": (Y, base, config.AZUL2),
                       "IS con shock ($dG,\\,dT,\\,dI_0$)": (Y, alt, config.ROJO)},
            "anotacion": (f"pendiente $= -(1-c_1)/b = {-(1 - p['c1']) / p['b']:.3f}$\n"
                          f"desplazamiento horizontal $= {dY:,.1f}$\n"
                          "sin LM no hay equilibrio: la IS es un lugar geométrico")}


def _resultados(p):
    k = 1 / (1 - p["c1"])
    y_en = lambda r, G, T, I0: (p["c0"] - p["c1"] * T + I0 - p["b"] * r + G) / (1 - p["c1"])
    return {"pendiente dr/dY": -(1 - p["c1"]) / p["b"],
            "dY por unidad de G (k)": k,
            "dY por unidad de T (−c1·k)": -p["c1"] * k,
            "dY por unidad de I0 (k)": k,
            "Y sobre IS base en r=5": y_en(5, p["G"], p["T"], p["I0"]),
            "Y sobre IS con shock en r=5": y_en(5, p["G"] + p["dG"], p["T"] + p["dT"],
                                                p["I0"] + p["dI0"])}


_P0 = {"c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "G": 200.0, "T": 100.0,
       "dG": 50.0, "dT": 0.0, "dI0": 0.0}


def _v_desplazamiento_g():
    r = _resultados(_P0)
    obs = r["Y sobre IS con shock en r=5"] - r["Y sobre IS base en r=5"]
    teo = _P0["dG"] / (1 - _P0["c1"])
    return abs(obs - teo) < 1e-9, f"con dG=50 la IS se corre {teo:,.1f} a la derecha (= k·dG)"


def _v_desplazamiento_t():
    p = dict(_P0, dG=0.0, dT=100.0)
    r = _resultados(p)
    obs = r["Y sobre IS con shock en r=5"] - r["Y sobre IS base en r=5"]
    teo = -p["c1"] * 100.0 / (1 - p["c1"])
    return abs(obs - teo) < 1e-9, (f"con dT=100 la IS se corre {teo:,.1f} (los impuestos "
                                   "mueven menos que el gasto: solo c1 de cada sol se gastaba)")


def _v_pendiente():
    Y = np.array([400.0, 600.0])
    r = _r_is(Y, _P0["G"], _P0["T"], _P0["I0"], _P0)
    pend = (r[1] - r[0]) / (Y[1] - Y[0])
    return abs(pend + (1 - _P0["c1"]) / _P0["b"]) < 1e-12, f"pendiente negativa = {pend:.4f}"


def _v_es_equilibrio():
    r5 = 4.0
    Y5 = (_P0["c0"] - _P0["c1"] * _P0["T"] + _P0["I0"] - _P0["b"] * r5 + _P0["G"]) / (1 - _P0["c1"])
    DA = _P0["c0"] + _P0["c1"] * (Y5 - _P0["T"]) + _P0["I0"] - _P0["b"] * r5 + _P0["G"]
    return abs(DA - Y5) < 1e-9, "cada punto de la IS es un equilibrio del mercado de bienes (m06)"


MODELO = Modelo(
    id="m07", nivel=2,
    nombre="Curva IS",
    xlabel="Producto ($Y$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("dG", _P0["dG"], -150, 150, 10, "Shock de gasto dG (desplaza IS)"),
        Parametro("dT", _P0["dT"], -150, 150, 10, "Shock de impuestos dT"),
        Parametro("dI0", _P0["dI0"], -100, 100, 10, "Shock de inversión autónoma dI0"),
        Parametro("G", _P0["G"], 0, 500, 10, "Gasto público base G"),
        Parametro("T", _P0["T"], 0, 400, 10, "Impuestos base T"),
        Parametro("c1", _P0["c1"], 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 5, 50, 1, "Sensibilidad de I a r (b)"),
        Parametro("c0", _P0["c0"], 0, 300, 10, "Consumo autónomo c0"),
        Parametro("I0", _P0["I0"], 0, 400, 10, "Inversión autónoma I0"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("Hicks bautizó la curva 'IS' por Investment-Saving: sobre ella, la "
                  "inversión deseada iguala al ahorro deseado. Es la mitad 'real' del "
                  "aparato con el que la síntesis neoclásica ordenó el debate keynesiano: "
                  "en vez de UN equilibrio del mercado de bienes, TODOS los posibles, uno "
                  "por cada tasa de interés."),
        autores=("Hicks (1937), 'Mr. Keynes and the Classics'; notación y uso canónico en "
                 "los manuales de la síntesis (Hansen, Samuelson)."),
        supuestos=[
            "Los mismos de m06 (la IS es m06 barrido sobre r).",
            "Cada punto es un equilibrio de FLUJO del período: no hay dinámica sobre la curva.",
            "G, T, I0, c0, c1, b constantes a lo largo de la curva: cambiarlos DESPLAZA la curva, no mueve sobre ella.",
        ],
        ecuaciones=[
            Ecuacion("r_{IS}(Y) = \\frac{c_0 - c_1 T + I_0 + G - (1-c_1)Y}{b}", "curva IS",
                     "despeje de DA=Y para r: qué tasa haría de cada Y un equilibrio de bienes."),
            Ecuacion("\\frac{dr}{dY}\\Big|_{IS} = -\\frac{1-c_1}{b}", "pendiente",
                     "empinada si la inversión responde poco a r (b chico) o si el multiplicador es "
                     "débil (c1 baja); plana en el caso contrario — de esa pendiente dependerá la "
                     "eficacia relativa de las políticas (m10-m12)."),
            Ecuacion("\\Delta Y\\big|_{r} = k\\,dG - c_1 k\\,dT + k\\,dI_0", "desplazamientos",
                     "a tasa constante, la IS se corre según el multiplicador del nivel 1; los "
                     "impuestos mueven menos que el gasto porque solo la fracción c1 se gastaba."),
        ],
        intuicion=("Distinguir MOVERSE SOBRE la curva (cambia r, el mercado de bienes "
                   "re-equilibra vía inversión y multiplicador) de DESPLAZAR la curva "
                   "(cambia el gasto autónomo a cada tasa). Todo el análisis fiscal de "
                   "IS-LM es geometría de desplazamientos de IS; la política monetaria "
                   "nunca toca esta curva — trabaja sobre la LM (m09)."),
        equilibrio=("La IS sola NO determina nada: es un lugar geométrico con una "
                    "incógnita de más (r). Cerrar el sistema exige la otra mitad — el "
                    "mercado de dinero."),
        limitaciones=[
            "Sin la LM queda indeterminada: es una herramienta intermedia, no un modelo completo.",
            "Hereda las limitaciones de m06 (linealidad, sin expectativas, precios fijos).",
            "El desplazamiento fiscal supone que el gasto no altera c1 ni I0 (sin efectos de confianza ni ricardianos, m67).",
        ],
        evolucion=("m08-m09 construyen la curva gemela del dinero (LM) y m10 las cruza. "
                   "La versión moderna reemplaza LM por una regla de política del banco "
                   "central (IS-MP, m51) — pero la IS sobrevive casi intacta hasta el "
                   "modelo nuevo keynesiano (m54, en versión dinámica con expectativas)."),
    ),
    escenarios=[
        Escenario("expansion_fiscal", "shock de gasto dG = +100",
                  {"dG": 100.0, "dT": 0.0, "dI0": 0.0},
                  "la IS se corre 250 a la derecha (k·dG): a CUALQUIER tasa, el mercado "
                  "de bienes ahora equilibra con más producto."),
        Escenario("alza_de_impuestos", "shock impositivo dT = +100 (sin tocar G)",
                  {"dG": 0.0, "dT": 100.0, "dI0": 0.0},
                  "la IS se corre 150 a la IZQUIERDA (−c1·k·dT): menos que un recorte de "
                  "gasto igual — base del multiplicador del presupuesto equilibrado."),
        Escenario("pesimismo_inversion", "colapso del ánimo inversor dI0 = −50",
                  {"dG": 0.0, "dT": 0.0, "dI0": -50.0},
                  "un shock privado desplaza la IS exactamente como uno fiscal del mismo "
                  "monto: la demanda agregada no distingue de quién viene el gasto."),
    ],
    verificaciones=[
        Verificacion("desplazamiento por dG = k·dG", _v_desplazamiento_g),
        Verificacion("desplazamiento por dT = −c1·k·dT", _v_desplazamiento_t),
        Verificacion("pendiente = −(1−c1)/b < 0", _v_pendiente),
        Verificacion("todo punto de la IS equilibra el mercado de bienes", _v_es_equilibrio),
    ],
    notas="La IS es un lugar geométrico, no un equilibrio: falta el mercado de dinero (m08-m09).",
)
