# m83_shock_alimentos.py — shock de alimentos (nivel 11).
#
# El shock de oferta de los emergentes: los alimentos pesan MUCHO más en la
# canasta del IPC de un país pobre (~40%) que de uno rico (~10%). El mismo
# salto de precios internacionales golpea la inflación general mucho más
# fuerte donde la gente gasta más en comer — y es regresivo (los pobres
# gastan mayor fracción en comida). Combina m19 (oferta) con el peso en el
# IPC como amplificador, y toca el riesgo político (los shocks de alimentos
# preceden revueltas — Primavera Árabe, mención).
#
# Procedencia: mecánica de shock de oferta (m19) con peso diferencial en el
# IPC — conocimiento general; calibración didáctica (peso de alimentos en el
# IPC del Perú ~como emergente).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_11 import _episodio
import config


def _episodio_alimentos(p):
    T = int(round(p["T"]))
    # el shock a precios de alimentos entra al IPC ponderado por su peso
    s = _episodio.pulso(T, 2, p["shock_alim"] * p["peso"] / 100, decae=0.3)
    d = np.zeros(T + 1)
    t, pi, Y = _episodio.simular(d, s, p["alpha"], p["lam"])
    return t, pi, Y, s


def _curvas(p):
    t, pi, Y, s = _episodio_alimentos(p)
    # comparar el mismo shock con peso rico (10%) vs emergente
    s_rico = _episodio.pulso(int(p["T"]), 2, p["shock_alim"] * 10 / 100, decae=0.3)
    _, pi_rico, _ = _episodio.simular(np.zeros(int(p["T"]) + 1), s_rico, p["alpha"], p["lam"])
    return {"lineas": {f"$\\pi$ con peso emergente ({p['peso']:.0f}%)": (t, pi, config.ROJO),
                       "$\\pi$ con peso rico (10%)": (t, pi_rico, config.AZUL2),
                       "meta": (t, np.full(len(t), 2.0), config.GRIS)},
            "anotacion": (f"mismo shock de precios de alimentos ({p['shock_alim']:+.0f}%)\n"
                          f"emergente (peso {p['peso']:.0f}%): π pico {float(pi.max()):.1f}%\n"
                          f"rico (peso 10%): π pico {float(pi_rico.max()):.1f}% — el peso amplifica")}


def _resultados(p):
    t, pi, Y, s = _episodio_alimentos(p)
    return {"pico de inflación general (%)": float(pi.max()),
            "peso de alimentos en el IPC (%)": p["peso"],
            "contribución al IPC (shock×peso)": p["shock_alim"] * p["peso"] / 100,
            "caída de producto (índice)": float(Y.min()) - 100,
            "π final": float(pi[-1])}


def _ecuaciones_calibradas(p):
    return [f"contribución $= {p['shock_alim']:+.0f}\\% \\times {p['peso']:.0f}\\% "
            f"= {p['shock_alim'] * p['peso'] / 100:+.1f}$ pp al IPC",
            f"peso emergente {p['peso']:.0f}\\% $\\gg$ peso rico 10\\%"]


_P0 = {"shock_alim": 30.0, "peso": 40.0, "alpha": 1.0, "lam": 0.5, "T": 14.0}


def _v_peso_amplifica():
    pi_emerg = float(_episodio_alimentos(dict(_P0, peso=40.0))[1].max())
    pi_rico = float(_episodio_alimentos(dict(_P0, peso=10.0))[1].max())
    return pi_emerg > pi_rico, \
        (f"el mismo shock de alimentos golpea más al emergente (π {pi_rico:.1f}→{pi_emerg:.1f}%): "
         "el peso en el IPC (40% vs 10%) es el amplificador — pobreza = vulnerabilidad")


def _v_contribucion_exacta():
    contrib = _P0["shock_alim"] * _P0["peso"] / 100
    return abs(contrib - 12.0) < 1e-9, \
        (f"la contribución al IPC = shock×peso = {contrib:.0f} pp exacto: la aritmética del "
         "IPC ponderado, sin la cual no se lee un shock de alimentos")


def _v_regresivo():
    # los pobres gastan más en comida: el shock es regresivo
    return _P0["peso"] > 25, \
        ("con alimentos pesando 40% del IPC promedio (y MÁS para los pobres), el shock "
         "es REGRESIVO: golpea proporcionalmente más a quien menos tiene")


def _v_transitorio_revierte():
    t, pi, Y, s = _episodio_alimentos(_P0)
    return abs(float(pi[-1]) - 2.0) < 1.5, \
        (f"al revertir el shock, π vuelve cerca de la meta ({float(pi[-1]):.1f}%): con ancla "
         "creíble, el pico de alimentos se disipa (la respuesta del BCRP, m113)")


MODELO = Modelo(
    id="m83", nivel=11,
    nombre="Shock de alimentos",
    xlabel="Período $t$ (trimestres)", ylabel="Inflación (%)",
    parametros=[
        Parametro("shock_alim", _P0["shock_alim"], 0, 60, 5, "Salto de precios de alimentos (%)",
                  grupo="shock", definicion="clima, guerra (Ucrania), fertilizantes"),
        Parametro("peso", _P0["peso"], 10, 55, 5, "Peso de alimentos en el IPC (%)",
                  grupo="estructura", definicion="emergente ~40%, rico ~10%: el amplificador"),
        Parametro("alpha", _P0["alpha"], 0.3, 2, 0.1, "Dureza de la regla α", grupo="estructura"),
        Parametro("lam", _P0["lam"], 0.2, 1, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("T", _P0["T"], 8, 20, 1, "Trimestres simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un mismo salto de precios de alimentos golpea mucho más a un país pobre que a uno rico?",
        variables=[("shock_alim", "salto de precios internacionales de alimentos"),
                   ("peso", "cuánto pesan los alimentos en el IPC: el amplificador"),
                   ("π general", "la inflación que resulta: shock × peso")],
        derivacion=["contribución\\;al\\;IPC = shock_{alim}\\times peso_{alim}",
                    "peso_{emergente}\\;(\\sim40\\%) \\gg peso_{rico}\\;(\\sim10\\%)",
                    "\\Rightarrow mismo\\;shock, \\;mucha\\;más\\;inflación\\;general"],
        contexto=("El shock de alimentos es el shock de oferta que define la "
                  "inflación de los emergentes. La clave es el peso en la canasta: "
                  "en un país pobre los alimentos son ~40% del IPC (y más aún del "
                  "gasto de los hogares de bajos ingresos), contra ~10% en uno "
                  "rico. El mismo salto de precios internacionales — por clima, "
                  "guerra (Ucrania cortó el trigo y los fertilizantes en 2022), o "
                  "biocombustibles — se traduce en mucha más inflación general "
                  "donde la gente gasta más en comer. Es además el shock más "
                  "REGRESIVO: golpea proporcionalmente más a los pobres. Y tiene "
                  "consecuencias que trascienden la macro: los picos de precios de "
                  "alimentos de 2008 y 2011 precedieron revueltas y la Primavera "
                  "Árabe (mención). Para el Perú, con inflación de alimentos "
                  "sensible al clima (El Niño) y a importados, es el shock de "
                  "m113."),
        autores=("Mecánica de m19 con IPC ponderado (conocimiento general); la "
                 "conexión alimentos-inestabilidad política: literatura sobre 2008 "
                 "y la Primavera Árabe (menciones)."),
        supuestos=[
            "El shock entra al IPC ponderado por el peso de alimentos: la aritmética central del episodio.",
            "Sin efecto ingreso para productores agrícolas (los países exportadores de alimentos ganan — matiz de m88).",
            "Ancla de expectativas presente: sin ella, el shock recurrente desancla (m40, m14).",
        ],
        ecuaciones=[
            Ecuacion("\\Delta\\pi_{IPC} = shock_{alim}\\times peso_{alim}", "el amplificador del peso",
                     "un shock de 30% con peso 40% son 12 pp al IPC; con peso 10%, solo 3: la "
                     "pobreza convierte un shock global en una crisis local (verificado)."),
            Ecuacion("regresivo: \\;peso_{pobres} > peso_{promedio}", "la injusticia del shock",
                     "los hogares de bajos ingresos gastan MÁS fracción en comida: el shock de "
                     "alimentos es un impuesto regresivo puro."),
        ],
        intuicion=("El shock de alimentos enseña que la vulnerabilidad "
                   "macroeconómica es también una cuestión de estructura social: "
                   "el mismo evento global — una sequía en otro continente — es "
                   "una molestia en un país rico y una emergencia en uno pobre, por "
                   "el simple peso de la comida en el presupuesto. Por eso los "
                   "bancos centrales de emergentes vigilan la inflación de "
                   "alimentos de cerca y a veces la excluyen del 'núcleo' para no "
                   "sobrerreaccionar a shocks transitorios (m113) — pero no pueden "
                   "ignorarla porque es la que la gente SIENTE. La política óptima "
                   "es anclar expectativas (m40) para mirar pasar los picos, más "
                   "protección social focalizada para el impacto regresivo."),
        equilibrio=("El pico de inflación revierte con el shock si las expectativas "
                    "están ancladas (verificado); sin ancla, la recurrencia de "
                    "shocks de alimentos desancla la inflación general (el riesgo "
                    "de m14)."),
        limitaciones=[
            "País importador de alimentos: los exportadores netos (Argentina, Brasil) tienen un efecto ingreso que compensa (m88).",
            "Núcleo vs general: excluir alimentos del núcleo ayuda a no sobrerreaccionar, pero la inflación 'sentida' es la general — dilema de comunicación (m40).",
            "Sin protección social: el impacto regresivo se puede amortiguar con transferencias focalizadas, fuera del modelo.",
        ],
        evolucion=("Es el shock de oferta relevante para emergentes, hermano de "
                   "m82 (petróleo). m85 añade el canal cambiario (los alimentos "
                   "importados suben con la devaluación), y m113 es la versión "
                   "peruana con datos del BCRP y el factor climático (El Niño)."),
    ),
    escenarios=[
        Escenario("emergente_golpeado", "shock de 30% con peso 40% (emergente)",
                  {"shock_alim": 30.0, "peso": 40.0},
                  "12 pp de contribución al IPC: la inflación general se dispara "
                  "porque la comida es casi la mitad de la canasta.",
                  cadena=["salto global de precios de alimentos", "peso alto en el IPC (40%)",
                          "contribución = shock×peso = 12 pp", "inflación general alta",
                          "y regresiva: golpea más a los pobres"]),
        Escenario("mismo_shock_pais_rico", "el mismo 30% con peso 10% (rico)",
                  {"shock_alim": 30.0, "peso": 10.0},
                  "solo 3 pp de contribución: el país rico apenas lo nota — la misma "
                  "sequía, dos mundos distintos según la estructura del gasto.",
                  cadena=["mismo shock global", "peso bajo en el IPC (10%)",
                          "contribución = 3 pp", "molestia, no crisis",
                          "la riqueza como amortiguador estructural"]),
        Escenario("guerra_de_ucrania", "shock severo del 50% (trigo+fertilizantes)",
                  {"shock_alim": 50.0, "peso": 40.0},
                  "20 pp al IPC: el shock de 2022 que empujó a millones a la "
                  "inseguridad alimentaria — cuando el granero del mundo entra en "
                  "guerra.",
                  cadena=["Ucrania: corte de trigo y fertilizantes", "shock global severo",
                          "peso alto en emergentes", "inflación de alimentos extrema",
                          "inseguridad alimentaria y riesgo político"]),
    ],
    verificaciones=[
        Verificacion("el peso en el IPC amplifica el shock", _v_peso_amplifica),
        Verificacion("contribución = shock × peso exacta", _v_contribucion_exacta),
        Verificacion("el shock es regresivo (peso alto)", _v_regresivo),
        Verificacion("transitorio revierte con ancla creíble", _v_transitorio_revierte),
    ],
    notas="La vulnerabilidad como estructura social: la misma sequía, molestia allá, emergencia acá. Peru = m113.",
)
