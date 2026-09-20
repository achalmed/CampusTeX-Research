"""simuladores/macro/modelos/nivel_11/m81_covid.py — COVID-19 como shock macroeconómico (nivel 11).

El experimento natural más limpio de la macro moderna: un shock SIMULTÁNEO
de oferta (confinamiento cierra fábricas: s>0) y de demanda (miedo + cierre
hunde el gasto: d<0), seguido de una respuesta fiscal-monetaria masiva
(d>0 tardío). La lección: el efecto sobre la INFLACIÓN depende de qué shock
domina — 2020 fue desinflacionario (dominó la demanda), 2021-22
inflacionario (dominó la oferta + estímulo). Combina m19 (oferta), m18
(demanda), m52 (dinámica) y m60/m70 (respuesta fiscal).

Procedencia: lectura estándar del episodio COVID (Guerrieri et al. sobre
"Keynesian supply shocks" — mención) sobre el motor AD-AS de m52 —
conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_11 import _episodio
import config


def _episodio_covid(p):
    T = int(round(p["T"]))
    # oferta: confinamiento sube costos desde t=1, decae al reabrir
    s = _episodio.pulso(T, 1, p["shock_oferta"], decae=0.35)
    # demanda: colapso brutal en t=1-2, luego estímulo (rebote) desde t=4
    d = (_episodio.pulso(T, 1, p["shock_demanda"], dur=2)
         + _episodio.pulso(T, 4, p["estimulo"], decae=0.25))
    t, pi, Y = _episodio.simular(d, s, p["alpha"], p["lam"])
    return t, pi, Y, d, s


def _curvas(p):
    t, pi, Y, d, s = _episodio_covid(p)
    u = _episodio.okun(Y)
    return {"lineas": {"producto $Y_t$ (índice)": (t, Y, config.AZUL2),
                       "inflación $\\pi_t$ (%)": (t, pi, config.ROJO),
                       "desempleo $\\Delta u$ (Okun)": (t, 100 + u, config.DORADO),
                       "potencial / meta": (t, np.full(len(t), 100.0), config.GRIS)},
            "anotacion": (f"$t=1$: oferta {p['shock_oferta']:+.1f} Y demanda "
                          f"{p['shock_demanda']:+.1f} A LA VEZ\n"
                          f"caída de $Y$: {float(Y.min()) - 100:+.1f} · pico de $\\pi$: "
                          f"{float(pi.max()):.1f}%\n"
                          "el efecto sobre π depende de QUÉ shock domina")}


def _resultados(p):
    t, pi, Y, d, s = _episodio_covid(p)
    return {"caída máxima de Y (índice)": float(Y.min()) - 100,
            "pico de inflación (%)": float(pi.max()),
            "inflación mínima (desinflación 2020)": float(pi.min()),
            "desempleo máximo (Δu Okun)": float(_episodio.okun(Y).max()),
            "Y final (recuperación)": float(Y[-1]),
            "π final": float(pi[-1])}


def _ecuaciones_calibradas(p):
    return [f"$s_t$ (oferta) $= {p['shock_oferta']:+.1f}$ decayente desde $t{{=}}1$",
            f"$d_t$ (demanda) $= {p['shock_demanda']:+.1f}$ en $t{{=}}1,2$ + estímulo "
            f"{p['estimulo']:+.1f}$ desde $t{{=}}4$"]


_P0 = {"shock_oferta": 2.5, "shock_demanda": -8.0, "estimulo": 6.0,
       "alpha": 1.0, "lam": 0.5, "T": 16.0}


def _v_recesion_profunda():
    t, pi, Y, d, s = _episodio_covid(_P0)
    return float(Y.min()) < 95, \
        (f"el producto se hunde a {float(Y.min()):.1f} (índice 100): recesión brutal por "
         "el DOBLE shock — la caída de 2020 no tuvo precedente en velocidad")


def _v_demanda_domina_desinfla():
    # con demanda muy negativa y oferta moderada, 2020 fue DESINFLACIONARIO
    t, pi, Y, d, s = _episodio_covid(dict(_P0, shock_demanda=-10.0, shock_oferta=1.5))
    return float(pi.min()) < _P0["alpha"] * 0 + 2.0, \
        (f"con la demanda dominando, la inflación CAE (mín {float(pi.min()):.1f}%<meta): "
         "2020 fue desinflacionario pese al shock de oferta — el efecto neto es ambiguo")


def _v_oferta_estimulo_inflan():
    # oferta persistente + estímulo grande = inflación 2021-22
    t, pi, Y, d, s = _episodio_covid(dict(_P0, shock_oferta=3.5, estimulo=9.0))
    return float(pi.max()) > 4.0, \
        (f"con oferta persistente + estímulo fuerte, π se dispara (pico {float(pi.max()):.1f}%): "
         "2021-22 invirtió el signo — cuellos de botella + demanda estimulada")


def _v_recuperacion():
    t, pi, Y, d, s = _episodio_covid(_P0)
    return abs(float(Y[-1]) - 100) < 3, \
        (f"al disiparse los shocks, Y vuelve cerca del potencial ({float(Y[-1]):.1f}): "
         "la recuperación en V que el estímulo aceleró")


MODELO = Modelo(
    id="m81", nivel=11,
    nombre="COVID-19 como shock macroeconómico",
    xlabel="Período $t$ (trimestres)", ylabel="Índices y tasas",
    parametros=[
        Parametro("shock_oferta", _P0["shock_oferta"], 0, 5, 0.5, "Shock de oferta (confinamiento)",
                  grupo="shocks", definicion="cierre de fábricas y cuellos de botella (m19)"),
        Parametro("shock_demanda", _P0["shock_demanda"], -12, 0, 1, "Shock de demanda (miedo+cierre)",
                  grupo="shocks", definicion="colapso del gasto (m18): el que dominó en 2020"),
        Parametro("estimulo", _P0["estimulo"], 0, 12, 1, "Estímulo fiscal-monetario",
                  grupo="respuesta", definicion="la respuesta masiva (m60): rebote e inflación 2021"),
        Parametro("alpha", _P0["alpha"], 0.3, 2, 0.1, "Dureza de la regla α", grupo="política"),
        Parametro("lam", _P0["lam"], 0.2, 1, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("T", _P0["T"], 10, 24, 1, "Trimestres simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué la pandemia PRIMERO bajó la inflación (2020) y DESPUÉS la disparó (2021-22)?",
        variables=[("s_t, d_t", "shocks de oferta y demanda — SIMULTÁNEOS, es lo raro"),
                   ("Y, π, Δu", "producto, inflación y empleo — el tablero completo (m24)"),
                   ("estímulo", "la respuesta fiscal-monetaria — que cambió el signo de π")],
        derivacion=["COVID = shock\\;de\\;oferta\\;(s>0) + shock\\;de\\;demanda\\;(d<0)\\;A\\;LA\\;VEZ",
                    "\\pi_t = \\frac{\\pi_{t-1} + \\lambda\\alpha\\pi^* + \\lambda d_t + s_t}{1+\\lambda\\alpha} \\;(m52)",
                    "signo\\;de\\;\\pi: \\;depende\\;de\\;|d|\\;vs\\;s"],
        contexto=("La pandemia fue el laboratorio macroeconómico de una generación: "
                  "un shock que golpeó oferta y demanda A LA VEZ, algo que los "
                  "modelos de un solo shock (m18, m19) no pueden capturar por "
                  "separado. En 2020 dominó el colapso de demanda (miedo, "
                  "confinamiento, ahorro precautorio) y el resultado fue "
                  "DESINFLACIONARIO pese al cierre de fábricas — desconcertando a "
                  "quienes esperaban inflación por la disrupción. En 2021-22 la "
                  "combinación se invirtió: la demanda rebotó con el estímulo "
                  "masivo mientras la oferta seguía trabada (cuellos de botella, "
                  "contenedores, chips) y llegó la mayor inflación en 40 años. "
                  "Guerrieri et al. (mención) formalizaron los 'Keynesian supply "
                  "shocks': shocks de oferta que, vía demanda, se amplifican. El "
                  "episodio es la síntesis perfecta del currículo — m18+m19+m52+m60 "
                  "en un solo gráfico."),
        autores=("Lectura del episodio: Guerrieri, Lorenzoni, Straub, Werning "
                 "('Keynesian supply shocks', mención); del rebote inflacionario: "
                 "el debate Summers-Blanchard vs 'transitory' (mención)."),
        supuestos=[
            "Oferta y demanda modelados como secuencias exógenas de shocks (el confinamiento es genuinamente exógeno — de ahí su valor como experimento natural).",
            "Passthrough y sector externo resumidos en el shock de oferta (el detalle importado es m85).",
            "Sin ZLB explícito: la política monetaria acompañó al estímulo fiscal (la trampa de liquidez que rondó es m95).",
        ],
        ecuaciones=[
            Ecuacion("COVID: \\;s_t > 0 \\;\\land\\; d_t < 0 \\;(simultáneos)", "el doble shock",
                     "lo que hace único al episodio: no es demanda (m18) NI oferta (m19), es AMBOS — "
                     "y su efecto neto sobre π es la resta, no una firma limpia."),
            Ecuacion("signo(\\pi) = signo(s_t - |\\lambda\\,d_t|)", "la ambigüedad inflacionaria",
                     "2020: |d| grande ⇒ desinflación; 2021: estímulo revierte d y s persiste ⇒ "
                     "inflación. El MISMO modelo explica los dos años opuestos (verificado)."),
        ],
        intuicion=("COVID enseñó que 'shock de oferta' y 'shock de demanda' no son "
                   "cajones excluyentes: una pandemia es los dos, y cuál domina "
                   "decide si hay inflación o deflación. La política tuvo que "
                   "navegar a ciegas — estimular demanda cuando la oferta estaba "
                   "trabada corría el riesgo de inflar (y lo hizo en 2021), pero no "
                   "estimular arriesgaba una depresión (el fantasma de 2020). El "
                   "veredicto histórico sigue en disputa: ¿el estímulo fue "
                   "excesivo (Summers) o proporcional al abismo (Blanchard "
                   "matizado)? El laboratorio deja al usuario mover las perillas y "
                   "revivir el dilema."),
        equilibrio=("No hay equilibrio estático: es una trayectoria de doble shock "
                    "con respuesta de política. La economía vuelve al potencial al "
                    "disiparse los shocks (recuperación en V verificada), pero el "
                    "camino — desinflación luego inflación — es el contenido."),
        limitaciones=[
            "Un solo país cerrado: la dimensión global (cadenas de suministro internacionales, m85) fue central y aquí se resume en el shock de oferta.",
            "Sin heterogeneidad: COVID golpeó desigualmente por sector (servicios vs bienes) e ingreso — clave para el rebote de bienes durables.",
            "El estímulo es exógeno: su tamaño ÓPTIMO (el debate real) exigiría el trade-off de m56/m60 endógeno.",
        ],
        evolucion=("Abre el nivel de escenarios mostrando la síntesis en su forma "
                   "más pura. Los siguientes aíslan cada canal: m82-m83 los shocks "
                   "de oferta puros (petróleo, alimentos), m85 la dimensión "
                   "importada, m91 el estímulo fiscal. Para el Perú, el COVID fue "
                   "además un shock externo y de términos de intercambio (m110)."),
    ),
    escenarios=[
        Escenario("2020_desinflacion", "domina la demanda: colapso −10, oferta 1.5",
                  {"shock_demanda": -10.0, "shock_oferta": 1.5},
                  "recesión profunda CON inflación cayendo: el 2020 real, donde el "
                  "miedo pesó más que los cuellos de botella.",
                  cadena=["confinamiento", "miedo + cierre hunden la demanda (domina)",
                          "fábricas cierran (oferta, menor)", "Y colapsa", "π CAE: desinflación",
                          "el shock de demanda ganó"]),
        Escenario("2021_inflacion", "oferta persistente 3.5 + estímulo fuerte 9",
                  {"shock_oferta": 3.5, "estimulo": 9.0},
                  "el signo se invierte: demanda estimulada contra oferta trabada = "
                  "la mayor inflación en 40 años.",
                  cadena=["estímulo masivo revierte la demanda", "cuellos de botella persisten (oferta)",
                          "demanda alta + oferta trabada", "π se dispara",
                          "Keynesian supply shock: la oferta amplificada por demanda"]),
        Escenario("sin_estimulo", "el contrafactual: estímulo = 0",
                  {"estimulo": 0.0},
                  "recuperación mucho más lenta y sin repunte inflacionario: lo que "
                  "habría pasado sin la respuesta fiscal — depresión evitada, pero "
                  "¿a qué costo de inflación?",
                  cadena=["doble shock sin respuesta", "la demanda no rebota",
                          "recuperación lenta (sin V)", "sin repunte de π",
                          "el dilema: rebote con inflación vs estancamiento sin ella"]),
    ],
    verificaciones=[
        Verificacion("el doble shock hunde el producto", _v_recesion_profunda),
        Verificacion("demanda dominante ⇒ desinflación (2020)", _v_demanda_domina_desinfla),
        Verificacion("oferta+estímulo ⇒ inflación (2021-22)", _v_oferta_estimulo_inflan),
        Verificacion("recuperación en V al disiparse los shocks", _v_recuperacion),
    ],
    notas="El experimento natural de una generación: oferta y demanda a la vez. El MISMO modelo explica 2020 y 2021.",
)
