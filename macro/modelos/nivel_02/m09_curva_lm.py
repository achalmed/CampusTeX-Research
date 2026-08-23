# m09_curva_lm.py — curva LM: todos los equilibrios del mercado de dinero (nivel 2).
#
# Recoge los pares (Y, r) donde el mercado monetario (m08) está en equilibrio:
#   r_LM(Y) = (k·Y − M/P) / h        (pendiente k/h > 0)
# Se grafican DOS curvas LM: la base (M/P) y una alternativa con M/P + dMP:
#   desplazamiento horizontal = dMP / k   (a r constante)
#
# Procedencia: Hicks (1937) y manuales de macro intermedia — conocimiento
# macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _r_lm(Y, MP, p):
    return (p["k"] * Y - MP) / p["h"]


def _curvas(p):
    Y = np.linspace(200, 1200, 300)
    return {"lineas": {"LM base": (Y, _r_lm(Y, p["MP"], p), config.ROJO),
                       "LM con dinero extra ($dMP$)": (Y, _r_lm(Y, p["MP"] + p["dMP"], p), config.VERDE)},
            "anotacion": (f"pendiente $= k/h = {p['k'] / p['h']:.3f}$\n"
                          f"desplazamiento horizontal $= dMP/k = {p['dMP'] / p['k']:,.1f}$\n"
                          "sin IS no hay equilibrio: la LM es un lugar geométrico")}


def _resultados(p):
    return {"pendiente dr/dY (k/h)": p["k"] / p["h"],
            "desplazamiento por dMP (dMP/k)": p["dMP"] / p["k"],
            "r sobre LM base en Y=700": _r_lm(700.0, p["MP"], p),
            "r sobre LM con dMP en Y=700": _r_lm(700.0, p["MP"] + p["dMP"], p),
            "caída de r a Y fijo (dMP/h)": p["dMP"] / p["h"]}


_P0 = {"k": 0.5, "h": 10.0, "MP": 300.0, "dMP": 50.0}


def _v_pendiente():
    pend = (_r_lm(800.0, _P0["MP"], _P0) - _r_lm(600.0, _P0["MP"], _P0)) / 200.0
    return abs(pend - _P0["k"] / _P0["h"]) < 1e-12, f"pendiente positiva k/h = {pend:.3f}"


def _v_desplazamiento():
    # Y que mantiene r=5 antes y después de la inyección
    y0 = (5 * _P0["h"] + _P0["MP"]) / _P0["k"]
    y1 = (5 * _P0["h"] + _P0["MP"] + _P0["dMP"]) / _P0["k"]
    return abs((y1 - y0) - _P0["dMP"] / _P0["k"]) < 1e-9, (f"a r constante la LM se corre "
                                                           f"{_P0['dMP'] / _P0['k']:,.1f} a la derecha (dMP/k)")


def _v_es_equilibrio():
    Y = 750.0
    r = _r_lm(Y, _P0["MP"], _P0)
    L = _P0["k"] * Y - _P0["h"] * r
    return abs(L - _P0["MP"]) < 1e-9, "cada punto de la LM equilibra el mercado de dinero (m08)"


MODELO = Modelo(
    id="m09", nivel=2,
    nombre="Curva LM",
    xlabel="Producto ($Y$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("dMP", _P0["dMP"], -150, 150, 10, "Inyección de dinero dMP (desplaza LM)"),
        Parametro("MP", _P0["MP"], 100, 600, 10, "Oferta real de dinero base M/P"),
        Parametro("k", _P0["k"], 0.1, 1.0, 0.05, "Sensibilidad de L a Y (k)"),
        Parametro("h", _P0["h"], 2, 30, 1, "Sensibilidad de L a r (h)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Qué combinaciones de producto y tasa equilibran el mercado de "
                  "dinero — y cómo las mueve la emisión?"),
        contexto=("La otra mitad del aparato de Hicks: LM por Liquidity-Money. Si m08 "
                  "encontraba la tasa que vacía el mercado de dinero para UN ingreso "
                  "dado, la LM repite el ejercicio para todos los ingresos posibles: a "
                  "más actividad, más demanda de liquidez, y con oferta monetaria fija "
                  "la tasa tiene que subir para que las cuentas cuadren."),
        autores=("Hicks (1937); manuales de la síntesis neoclásica (Hansen)."),
        supuestos=[
            "Los mismos de m08 (la LM es m08 barrido sobre Y).",
            "M y P fijos a lo largo de la curva: cambiar M/P DESPLAZA la LM (no se mueve sobre ella).",
            "La demanda de dinero es estable (Friedman construirá su crítica monetarista sobre esa estabilidad).",
        ],
        ecuaciones=[
            Ecuacion("r_{LM}(Y) = \\frac{k\\,Y - M/P}{h}", "curva LM",
                     "despeje del equilibrio monetario para r: qué tasa vacía el mercado de "
                     "dinero en cada nivel de actividad."),
            Ecuacion("\\frac{dr}{dY}\\Big|_{LM} = \\frac{k}{h}", "pendiente",
                     "empinada si la demanda de dinero es sensible a Y (k alto) o insensible a r "
                     "(h chico: caso 'monetarista'); plana si h es enorme (antesala de la trampa "
                     "de liquidez, m12)."),
            Ecuacion("\\Delta Y\\big|_{r} = \\frac{dMP}{k}", "desplazamiento",
                     "a tasa constante, el dinero extra sostiene dMP/k más de transacciones: la "
                     "LM entera se corre a la derecha."),
        ],
        intuicion=("La LM es la restricción de liquidez de la economía: recorrerla hacia "
                   "la derecha es aceptar que crecer con la misma cantidad de dinero "
                   "encarece el crédito. El banco central 'afloja' esa restricción "
                   "desplazándola con emisión — o, en la práctica moderna, fijando "
                   "directamente la tasa y dejando que M se acomode."),
        equilibrio=("Igual que la IS, la LM sola no determina nada: es la segunda "
                    "ecuación del sistema. Su intersección con la IS (m10) resuelve las "
                    "dos incógnitas (Y, r) a la vez."),
        limitaciones=[
            "Supone M exógena y P fijo: con precios flexibles la 'LM' se mueve sola vía M/P (puerta a AD-AS, m20).",
            "Los bancos centrales modernos fijan r, no M: la 'LM' relevante hoy es una regla de política (IS-MP m51, Taylor m38).",
            "La estabilidad empírica de la demanda de dinero se rompió en los 80 (innovación financiera): predicciones con M se volvieron poco fiables.",
        ],
        evolucion=("Con IS (m07) y LM (m09) sobre la mesa, m10 las cruza y produce el "
                   "modelo completo. Los casos límite de su pendiente son m11 (LM "
                   "empinada → expulsión fuerte) y m12 (LM plana → trampa de liquidez); "
                   "su reemplazo moderno por una regla de tasa es m51."),
    ),
    escenarios=[
        Escenario("expansion_monetaria", "inyección dMP = +100",
                  {"dMP": 100.0},
                  "la LM se corre 200 a la derecha (dMP/k): a cada tasa, el dinero extra "
                  "sostiene más transacciones.",
                  cadena=["↑dMP", "sobra liquidez a cada Y", "↓r para cada Y",
                          "LM → derecha en dMP/k"]),
        Escenario("contraccion_monetaria", "retiro de liquidez dMP = −100",
                  {"dMP": -100.0},
                  "la LM a la izquierda: el mismo nivel de actividad exige ahora una tasa "
                  "mayor para racionar la liquidez.",
                  cadena=["↓dMP", "falta liquidez a cada Y", "↑r para cada Y",
                          "LM → izquierda"]),
        Escenario("demanda_muy_sensible", "h sube de 10 a 25 (dinero y bonos casi sustitutos)",
                  {"h": 25.0},
                  "la LM se aplana: cambios de Y casi no mueven r — cuando h→∞ la curva "
                  "es horizontal y la política monetaria pierde tracción (trampa, m12).",
                  cadena=["↑h", "dinero y bonos casi sustitutos", "pendiente k/h cae",
                          "LM se aplana (antesala de m12)"]),
    ],
    verificaciones=[
        Verificacion("pendiente = k/h > 0", _v_pendiente),
        Verificacion("desplazamiento por dMP = dMP/k", _v_desplazamiento),
        Verificacion("todo punto de la LM equilibra el mercado de dinero", _v_es_equilibrio),
    ],
    notas="Gemela de la IS: juntas (m10) resuelven (Y*, r*). Su pendiente decide qué política es potente.",
)
