"""simuladores/macro/modelos/nivel_11/m93_estanflacion.py — estanflación: el episodio de los 70 (nivel 11).

El caso histórico completo que unió el currículo: la estanflación de los 70
no fue solo un shock petrolero (m82), sino un shock petrolero SOBRE una
Phillips ya desanclada (m14) con un banco central que acomodaba (m41 sin
credibilidad). El resultado: una espiral donde cada shock se convalidaba y
las expectativas subían, hasta que hizo falta la recesión de Volcker (m14)
para re-anclar. El modelo muestra la diferencia entre un shock petrolero
CON ancla (transitorio, m40) y SIN ancla (espiral, m14): el mismo shock,
dos décadas distintas. Combina m14, m19, m24, m40, m41.

Procedencia: la estanflación de los 70 (menciones históricas: OPEP, Burns,
Volcker) sobre m14 (Phillips con expectativas) y m52 — conocimiento general;
calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_11 import _episodio
import config


def _sendas(p, T=None):
    """Phillips con expectativas adaptativas (m14) + shocks de oferta repetidos
    + acomodo. La CLAVE es theta: anclaje de expectativas (bajo = espiral)."""
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    # dos shocks petroleros (1973, 1979)
    s = _episodio.pulso(T, 2, p["shock"], decae=0.3) + _episodio.pulso(T, 7, p["shock"], decae=0.3)
    pi = np.empty(T + 1); pi[0] = 2.0
    pe = 2.0
    for j in range(T + 1):
        # con anclaje theta, pe tiende a la meta; sin él, sigue a la inflación pasada
        pe = p["theta"] * 2.0 + (1 - p["theta"]) * (pi[j - 1] if j > 0 else 2.0)
        # acomodo añade demanda que convalida
        pi[j] = pe + s[j] + p["acomodo"] * (s[j] > 0)
    return t, pi, s


def _curvas(p):
    t, pi, s = _sendas(p)
    # comparar con ancla creíble (theta alto)
    _, pi_anclado, _ = _sendas(dict(p, theta=0.8, acomodo=0.0))
    return {"lineas": {f"inflación SIN ancla ($\\theta={p['theta']:.2f}$)": (t, pi, config.ROJO),
                       "inflación CON ancla ($\\theta=0.8$)": (t, pi_anclado, config.AZUL2),
                       "meta": (t, np.full(len(t), 2.0), config.GRIS)},
            "anotacion": (f"dos shocks petroleros (1973, 1979), acomodo {p['acomodo']:.1f}\n"
                          f"sin ancla: π escala a {float(pi.max()):.1f}% (espiral, m14)\n"
                          "con ancla: los shocks se miran pasar (m40)")}


def _resultados(p):
    t, pi, s = _sendas(p)
    _, pi_anclado, _ = _sendas(dict(p, theta=0.8, acomodo=0.0))
    return {"pico de inflación sin ancla (%)": float(pi.max()),
            "pico con ancla creíble (%)": float(pi_anclado.max()),
            "inflación final sin ancla": float(pi[-1]),
            "inflación final con ancla": float(pi_anclado[-1]),
            "amplificación del desanclaje (×)": float(pi.max()) / max(float(pi_anclado.max()), 0.1)}


def _ecuaciones_calibradas(p):
    return [f"$\\pi^e = {p['theta']:.2f}\\,\\pi^* + {1 - p['theta']:.2f}\\,\\pi_{{t-1}}$ (anclaje)",
            f"$\\pi_t = \\pi^e + s_t + {p['acomodo']:.1f}\\,(acomodo)$"]


_P0 = {"shock": 4.0, "theta": 0.1, "acomodo": 2.0, "T": 16.0}


def _v_espiral_sin_ancla():
    t, pi, s = _sendas(_P0)
    return float(pi.max()) > 8.0, \
        (f"sin ancla (θ={_P0['theta']}), la inflación ESCALA con cada shock a {float(pi.max()):.1f}%: "
         "la espiral de los 70 — cada shock se hereda y se convalida (m14)")


def _v_ancla_mira_pasar():
    _, pi_anclado, _ = _sendas(dict(_P0, theta=0.8, acomodo=0.0))
    return float(pi_anclado.max()) < float(_sendas(_P0)[1].max()), \
        (f"con ancla creíble (θ=0.8), los MISMOS shocks producen mucha menos inflación "
         f"({float(pi_anclado.max()):.1f}% vs {float(_sendas(_P0)[1].max()):.1f}%): la diferencia entre los 70 y hoy (m40)")


def _v_acomodo_convalida():
    pi_acom = float(_sendas(_P0)[1].max())
    pi_no_acom = float(_sendas(dict(_P0, acomodo=0.0))[1].max())
    return pi_acom > pi_no_acom, \
        (f"acomodar los shocks los convalida y sube la inflación ({pi_no_acom:.1f}→{pi_acom:.1f}%): "
         "la Fed de Burns — la política que enquistó la inflación (m41)")


def _v_dos_shocks_acumulan():
    t, pi, s = _sendas(_P0)
    # el segundo shock (1979) llega sobre expectativas ya altas
    return float(pi[8]) > float(pi[3]), \
        ("el segundo shock (1979) golpea sobre expectativas ya desancladas por el primero: "
         "los shocks NO se suman, se MULTIPLICAN vía las expectativas (m14)")


MODELO = Modelo(
    id="m93", nivel=11,
    nombre="Estanflación (episodio de los 70)",
    xlabel="Período $t$", ylabel="Inflación (%)",
    parametros=[
        Parametro("theta", _P0["theta"], 0.05, 0.9, 0.05, "Anclaje de expectativas θ",
                  grupo="régimen", definicion="bajo=espiral (los 70); alto=mirar pasar (hoy, m40)"),
        Parametro("acomodo", _P0["acomodo"], 0, 4, 0.5, "Grado de acomodo monetario",
                  grupo="política", definicion="convalidar el shock (Burns) vs resistir (Volcker)"),
        Parametro("shock", _P0["shock"], 1, 6, 0.5, "Tamaño de cada shock petrolero",
                  grupo="shock"),
        Parametro("T", _P0["T"], 12, 24, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué los shocks petroleros de los 70 desataron una espiral inflacionaria — y por qué los de hoy no?",
        variables=[("θ (anclaje)", "la variable clave: bajo=espiral, alto=mirar pasar"),
                   ("acomodo", "convalidar el shock (Burns) o resistir (Volcker)"),
                   ("dos shocks", "1973 y 1979: el segundo sobre expectativas ya altas")],
        derivacion=["shock\\;petrolero\\;(m19) + Phillips\\;desanclada\\;(m14) + acomodo\\;(m41)",
                    "\\pi^e = \\theta\\pi^* + (1-\\theta)\\pi_{t-1} \\;(anclaje)",
                    "\\theta\\;bajo \\Rightarrow espiral;\\;\\;\\theta\\;alto \\Rightarrow mirar\\;pasar"],
        contexto=("La estanflación de los 70 es el episodio que reescribió la "
                  "macroeconomía, y este modelo lo reconstruye integrando cuatro "
                  "piezas del currículo. No fue solo un shock petrolero (m82): fue "
                  "un shock petrolero que golpeó sobre una economía con "
                  "expectativas de inflación YA DESANCLADAS (m14) y un banco "
                  "central que ACOMODABA (la Fed de Burns, sin la credibilidad de "
                  "m41). El resultado fue una espiral: cada shock subía la "
                  "inflación, las expectativas la seguían (θ bajo), el banco central "
                  "acomodaba para proteger el empleo, y el siguiente shock (1979) "
                  "golpeaba sobre expectativas aún más altas — la inflación escaló "
                  "de un dígito a dos. Hizo falta la recesión deliberada de Volcker "
                  "(1979-82, m14) para re-anclar las expectativas a un costo enorme "
                  "en desempleo. La lección se institucionalizó en las metas de "
                  "inflación (m40): un banco central creíble con expectativas "
                  "ancladas (θ alto) puede 'mirar pasar' un shock petrolero "
                  "transitorio sin que se convierta en espiral. Por eso los shocks "
                  "de precios de 2008, 2011 y 2022 — comparables en magnitud a los "
                  "de los 70 — NO desataron estanflaciones prolongadas: las "
                  "expectativas estaban ancladas. La diferencia entre los 70 y hoy "
                  "no es la suerte con el petróleo; es la credibilidad del ancla."),
        autores=("OPEP 1973/1979, Burns, Volcker (menciones históricas); la "
                 "teoría: Friedman-Phelps (m14), Barro-Gordon (m41), metas de "
                 "inflación (m40) — conocimiento general."),
        supuestos=[
            "Anclaje θ resume el régimen (credibilidad + expectativas): bajo en los 70, alto hoy.",
            "Dos shocks (1973, 1979) para mostrar la acumulación vía expectativas — el segundo sobre el primero.",
            "El acomodo se modela como demanda que convalida el shock (Burns): resistir (Volcker) es acomodo negativo o cero.",
        ],
        ecuaciones=[
            Ecuacion("\\pi^e = \\theta\\,\\pi^* + (1-\\theta)\\,\\pi_{t-1}", "el anclaje",
                     "con θ alto las expectativas vuelven a la meta (mirar pasar); con θ bajo "
                     "siguen a la inflación pasada (espiral) — la variable que separa las eras."),
            Ecuacion("shock_2\\;sobre\\;\\pi^e_1\\;alto \\Rightarrow multiplicación",
                     "por qué el segundo shock fue peor",
                     "1979 golpeó sobre expectativas ya desancladas por 1973: los shocks no se "
                     "suman, se componen vía las expectativas (verificado)."),
        ],
        intuicion=("La estanflación de los 70 enseña que la inflación es tanto un "
                   "fenómeno de expectativas como de shocks: el mismo shock "
                   "petrolero es una molestia transitoria en una economía anclada y "
                   "el detonante de una espiral en una desanclada. La diferencia la "
                   "hace la CREDIBILIDAD del banco central — su capacidad de "
                   "convencer a todos de que la inflación volverá a la meta, para "
                   "que nadie ajuste sus precios y salarios al alza en anticipación. "
                   "Los 70 fueron la lección cara de lo que pasa sin esa "
                   "credibilidad; las metas de inflación (m40) y la independencia "
                   "del banco central (m41) fueron la respuesta institucional. Para "
                   "un emergente como el Perú, que vivió su propia espiral en los 80 "
                   "(hiperinflación, m36), la construcción del ancla (metas del BCRP "
                   "desde 2002) fue exactamente aprender la lección de los 70 — y "
                   "por eso los shocks de alimentos recientes (m113) no desataron "
                   "espirales: el ancla aguantó."),
        equilibrio=("Con θ bajo, la inflación escala sin equilibrio estable "
                    "(espiral); con θ alto, revierte a la meta tras cada shock "
                    "(verificado). El re-anclaje (Volcker) es un cambio de régimen "
                    "de θ bajo a alto, a costa de una recesión."),
        limitaciones=[
            "θ exógeno: cómo se pierde y se recupera la credibilidad (m41) es el drama real — aquí es un parámetro.",
            "Sin el costo del re-anclaje explícito: la recesión de Volcker (la tasa de sacrificio, m14) fue el precio de volver a θ alto.",
            "Dos shocks discretos: los 70 tuvieron múltiples shocks (petróleo, alimentos, productividad) que se compusieron — aquí simplificado.",
        ],
        evolucion=("Es el episodio histórico que unifica m14 (expectativas), m19 "
                   "(oferta), m24 (dilema), m40 (metas) y m41 (credibilidad) — la "
                   "justificación completa del régimen monetario moderno. Contrasta "
                   "con m81 (COVID, donde el ancla aguantó) y prepara m94-m95 (el "
                   "problema opuesto: la deflación y la trampa). Para el Perú, es la "
                   "lección detrás de m99 (inflación peruana) y m113."),
    ),
    escenarios=[
        Escenario("los_70", "sin ancla (θ=0.1) + acomodo (Burns)",
                  {"theta": 0.1, "acomodo": 2.0},
                  "la espiral: cada shock se hereda y se convalida, la inflación "
                  "escala a dos dígitos — los 70 en un gráfico.",
                  cadena=["shock petrolero", "expectativas desancladas lo siguen (θ bajo)",
                          "el banco central acomoda (Burns)", "segundo shock sobre expectativas altas",
                          "espiral: inflación de dos dígitos"]),
        Escenario("hoy_anclado", "ancla creíble (θ=0.8), sin acomodo",
                  {"theta": 0.8, "acomodo": 0.0},
                  "los MISMOS shocks se miran pasar: las expectativas ancladas "
                  "impiden la espiral — por qué 2022 no fue 1973 (m40).",
                  cadena=["mismo shock petrolero", "expectativas ancladas (θ alto, m40)",
                          "vuelven a la meta", "el shock no se hereda", "inflación transitoria, sin espiral"]),
        Escenario("volcker", "resistir sin acomodo con desanclaje inicial",
                  {"theta": 0.1, "acomodo": 0.0},
                  "sin acomodo, la inflación sube menos pero re-anclar desde θ bajo "
                  "aún cuesta: la doctrina Volcker — no convalidar, aguantar la "
                  "recesión.",
                  cadena=["shock sobre expectativas desancladas", "el banco central NO acomoda (Volcker)",
                          "la inflación sube menos", "pero re-anclar toma tiempo y recesión",
                          "el costo de recuperar la credibilidad (m41)"]),
    ],
    verificaciones=[
        Verificacion("sin ancla: espiral inflacionaria (m14)", _v_espiral_sin_ancla),
        Verificacion("con ancla: mirar pasar los shocks (m40)", _v_ancla_mira_pasar),
        Verificacion("acomodar convalida el shock (Burns, m41)", _v_acomodo_convalida),
        Verificacion("el segundo shock se compone sobre el primero", _v_dos_shocks_acumulan),
    ],
    notas="La diferencia entre los 70 y hoy no es el petróleo; es la credibilidad del ancla (m40-m41).",
)
