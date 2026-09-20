"""simuladores/macro/modelos/nivel_11/m92_recesion_inflacion.py — recesión con inflación (nivel 11).

El diagnóstico diferencial: una recesión CON inflación alta puede venir de
dos fuentes muy distintas, y la respuesta correcta es opuesta:
  (A) shock de OFERTA (m19): π↑ y Y↓ a la vez → dilema (m24), respuesta ambigua
  (B) DEMANDA que se enfría tarde: inflación heredada (inercia, m14) mientras
      la brecha ya se abrió → la desinflación llega con rezago
El caso (A) es estanflación genuina (m93); el (B) es el final de un ciclo
inflacionario. Distinguirlos exige mirar la BRECHA vs la inflación: si la
inflación sube CON la brecha negativa, es oferta; si la inflación cae "tarde"
tras la brecha, es demanda con inercia. Combina m14 (inercia), m19 (oferta)
y m16 (brecha) sobre el motor de m52.

Procedencia: diagnóstico oferta/demanda (m18/m19/m24), inercia inflacionaria
(m14) — conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_11 import _episodio
import config


def _episodio_rec(p):
    T = int(round(p["T"]))
    # componente de oferta (persistente) y de demanda (colapso tardío)
    s = _episodio.pulso(T, 2, p["oferta"], decae=0.2)
    d = _episodio.pulso(T, 3, -p["enfriamiento"], decae=0.15)
    t, pi, Y = _episodio.simular(d, s, p["alpha"], p["lam"])
    return t, pi, Y


def _curvas(p):
    t, pi, Y = _episodio_rec(p)
    return {"lineas": {"producto $Y_t$ (índice)": (t, Y, config.AZUL2),
                       "inflación $\\pi_t$ (%)": (t, pi, config.ROJO),
                       "potencial / meta": (t, np.full(len(t), 100.0), config.GRIS)},
            "anotacion": (f"oferta {p['oferta']:+.1f}, enfriamiento {p['enfriamiento']:.1f}\n"
                          f"π pico {float(pi.max()):.1f}% con Y mín {float(Y.min()):.1f}\n"
                          "recesión CON inflación: ¿oferta o demanda con inercia?")}


def _resultados(p):
    t, pi, Y = _episodio_rec(p)
    return {"pico de inflación (%)": float(pi.max()),
            "caída de producto (índice)": float(Y.min()) - 100,
            "inflación al final": float(pi[-1]),
            "¿inflación baja tarde? (demanda)": float(pi[-1]) - float(pi.max()),
            "coincidencia recesión-inflación": float(pi.max() * abs(Y.min() - 100))}


def _ecuaciones_calibradas(p):
    return [f"oferta $s_t = {p['oferta']:+.1f}$ persistente",
            f"enfriamiento $d_t = {-p['enfriamiento']:+.1f}$ tardío"]


_P0 = {"oferta": 2.0, "enfriamiento": 4.0, "alpha": 1.0, "lam": 0.5, "T": 16.0}


def _v_recesion_con_inflacion():
    t, pi, Y = _episodio_rec(_P0)
    return float(pi.max()) > 2.0 and float(Y.min()) < 100, \
        (f"recesión ({float(Y.min()):.1f}) CON inflación ({float(pi.max()):.1f}%): la "
         "combinación que exige diagnóstico — no toda inflación con recesión es igual")


def _v_oferta_pura_estanflacion():
    t, pi, Y = _episodio_rec(dict(_P0, oferta=3.0, enfriamiento=0.0))
    return float(pi.max()) > 2.0 and float(Y.min()) < 100, \
        ("oferta pura (sin enfriamiento) da estanflación genuina (m24): π↑ y Y↓ por el "
         "MISMO shock — el caso donde no estimular")


def _v_demanda_desinfla_tarde():
    t, pi, Y = _episodio_rec(dict(_P0, oferta=0.0, enfriamiento=6.0))
    return float(pi[-1]) < float(pi.max()), \
        (f"con enfriamiento de demanda, la inflación baja TARDE (de {float(pi.max()):.1f} a "
         f"{float(pi[-1]):.1f}): inercia (m14) — la desinflación llega con rezago")


def _v_inercia_persiste():
    t, pi, Y = _episodio_rec(dict(_P0, lam=0.2))
    t2, pi2, Y2 = _episodio_rec(dict(_P0, lam=0.9))
    return float(pi.sum()) > float(pi2.sum()), \
        ("con Phillips plana (λ bajo, más inercia), la inflación tarda más en ceder: "
         "la persistencia (m14) alarga el período de recesión-con-inflación")


MODELO = Modelo(
    id="m92", nivel=11,
    nombre="Recesión con inflación",
    xlabel="Período $t$ (trimestres)", ylabel="Índices y tasas",
    parametros=[
        Parametro("oferta", _P0["oferta"], 0, 4, 0.5, "Componente de oferta", grupo="diagnóstico",
                  definicion="shock de costos (m19): estanflación genuina si domina"),
        Parametro("enfriamiento", _P0["enfriamiento"], 0, 8, 0.5, "Enfriamiento de demanda",
                  grupo="diagnóstico", definicion="fin de ciclo: inflación heredada + brecha (m14)"),
        Parametro("alpha", _P0["alpha"], 0.3, 2, 0.1, "Dureza de la regla α", grupo="estructura"),
        Parametro("lam", _P0["lam"], 0.2, 1, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("T", _P0["T"], 10, 24, 1, "Trimestres simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Una recesión con inflación alta, ¿es un shock de oferta o el final de un ciclo de demanda? La respuesta cambia todo.",
        variables=[("oferta", "shock de costos: estanflación genuina (m19/m24)"),
                   ("demanda con inercia", "inflación heredada + brecha que se abre (m14)"),
                   ("brecha vs π", "el diagnóstico: cómo se mueven juntas")],
        derivacion=["oferta: \\;s>0 \\Rightarrow \\pi\\uparrow\\;y\\;Y\\downarrow\\;juntos\\;(m19)",
                    "demanda: \\;\\pi\\;heredada\\;(m14) + brecha\\;que\\;se\\;abre\\;(m16)",
                    "diagnóstico: \\;\\pi\\uparrow\\;con\\;brecha\\;\\to\\;oferta;\\;\\pi\\downarrow\\;tarde\\;\\to\\;demanda"],
        contexto=("'Recesión con inflación' es un síntoma, no un diagnóstico — y "
                  "confundir sus dos causas posibles lleva a errores de política "
                  "opuestos. La primera causa es un shock de OFERTA (m19): el "
                  "petróleo o los alimentos suben, la inflación y el desempleo "
                  "crecen juntos, y es la estanflación genuina donde la política "
                  "enfrenta el dilema de m24. La segunda es el FINAL de un ciclo de "
                  "demanda: la economía se sobrecalentó, la inflación subió por "
                  "exceso de demanda, y ahora que la brecha se cierra (o se vuelve "
                  "negativa) la inflación todavía no ha bajado porque tiene INERCIA "
                  "(m14) — la desinflación llega con rezago. La distinción es "
                  "crucial: ante oferta, estimular da más inflación (m24); ante "
                  "demanda con inercia, hay que MANTENER el apretón y esperar a que "
                  "la inflación ceda (el 'último kilómetro' de la desinflación). El "
                  "diagnóstico se hace mirando cómo se mueven la brecha y la "
                  "inflación: si la inflación SUBE mientras la brecha se abre, es "
                  "oferta; si la inflación CAE con rezago tras la brecha, es demanda "
                  "con inercia. El error de 2021-22 fue en parte diagnóstico: "
                  "¿inflación de oferta transitoria (no responder) o de demanda "
                  "persistente (apretar)? — resultó ser más de lo segundo de lo que "
                  "se creyó."),
        autores=("Diagnóstico oferta/demanda: m18/m19/m24; inercia inflacionaria: "
                 "m14; el 'último kilómetro' de la desinflación (menciones) — "
                 "conocimiento general."),
        supuestos=[
            "Dos componentes separables (oferta y demanda con inercia): la realidad los mezcla, y separarlos es el problema.",
            "La inercia vive en λ y las expectativas adaptativas (m14): con expectativas racionales ancladas (m42), la desinflación es más rápida.",
            "Sin observar el shock directamente: el diagnóstico se hace por la CO-MOVIMIENTO de brecha e inflación (la información disponible).",
        ],
        ecuaciones=[
            Ecuacion("oferta: \\;\\pi\\uparrow \\land brecha < 0 \\;(juntos)", "la firma de oferta",
                     "inflación y recesión del MISMO shock: estanflación genuina (m24) — no "
                     "estimular."),
            Ecuacion("demanda: \\;\\pi\\downarrow\\;con\\;rezago\\;tras\\;brecha < 0", "la firma de demanda",
                     "la inflación es herencia (m14) que cede tarde: mantener el apretón y esperar "
                     "— el diagnóstico opuesto (verificado)."),
        ],
        intuicion=("La recesión con inflación es el caso donde el diagnóstico "
                   "económico se parece a la medicina: el mismo síntoma (fiebre + "
                   "dolor) puede ser una infección (tratar con antibiótico) o una "
                   "reacción alérgica (suspender el alérgeno) — y el tratamiento "
                   "equivocado empeora. En macro, la 'fiebre' es la inflación y el "
                   "'dolor' la recesión; la infección es el shock de oferta "
                   "(dilema, m24) y la alergia es el ciclo de demanda con inercia "
                   "(mantener el apretón). La herramienta diagnóstica es la brecha "
                   "del producto (m16) y su relación con la inflación en el tiempo. "
                   "El costo de equivocarse es alto en ambas direcciones: tratar "
                   "una inflación de demanda como de oferta (no apretar) la deja "
                   "enquistarse (los 70); tratar una de oferta como de demanda "
                   "(apretar de más) profundiza una recesión innecesaria. El buen "
                   "banco central es, ante todo, un buen diagnosticador."),
        equilibrio=("La combinación recesión-inflación revierte según su causa: la "
                    "de oferta al disiparse el shock, la de demanda al ceder la "
                    "inercia (verificado). El diagnóstico se lee en el rezago de la "
                    "desinflación respecto a la brecha."),
        limitaciones=[
            "Los componentes se mezclan en la realidad: 2021-22 fue oferta Y demanda, y separarlos EN TIEMPO REAL fue el debate.",
            "La inercia depende del régimen: anclada (m40) la desinflación es rápida; desanclada (m14), lenta — el mismo síntoma, distinta dinámica.",
            "Sin datos: el diagnóstico real usa múltiples indicadores (núcleo, expectativas, salarios) que el modelo resume en dos componentes.",
        ],
        evolucion=("Es el diagnóstico diferencial que m93 (estanflación de los 70) "
                   "y m81 (COVID) ilustran con casos. Combina m14 (inercia), m19 "
                   "(oferta) y m16 (brecha) en la pregunta práctica de todo banco "
                   "central. Para el Perú, distinguir inflación de alimentos "
                   "importados (oferta, m113) de recalentamiento (demanda) es este "
                   "modelo aplicado."),
    ),
    escenarios=[
        Escenario("estanflacion_oferta", "shock de oferta puro (3, sin enfriamiento)",
                  {"oferta": 3.0, "enfriamiento": 0.0},
                  "π y Y del mismo shock: estanflación genuina (m24) — el dilema "
                  "donde estimular da más inflación.",
                  cadena=["shock de costos (m19)", "π↑ y Y↓ juntos", "estanflación genuina",
                          "diagnóstico: oferta", "no estimular (m24)"]),
        Escenario("fin_de_ciclo", "enfriamiento de demanda fuerte (6), sin oferta",
                  {"oferta": 0.0, "enfriamiento": 6.0},
                  "la inflación heredada baja tarde tras abrirse la brecha: inercia "
                  "(m14) — mantener el apretón y esperar el 'último kilómetro'.",
                  cadena=["fin de ciclo: brecha se abre", "inflación heredada persiste (m14)",
                          "desinflación con rezago", "diagnóstico: demanda con inercia",
                          "mantener el apretón, esperar"]),
        Escenario("mezcla_2022", "ambos: oferta 2 + enfriamiento 4",
                  {"oferta": 2.0, "enfriamiento": 4.0},
                  "el caso real y difícil: oferta y demanda mezcladas — el "
                  "diagnóstico de 2021-22 que dividió a los economistas.",
                  cadena=["oferta (cuellos de botella) + demanda (estímulo)",
                          "inflación de ambas fuentes", "diagnóstico ambiguo",
                          "el debate transitorio vs persistente", "resultó más demanda de lo creído"]),
    ],
    verificaciones=[
        Verificacion("recesión con inflación (el síntoma)", _v_recesion_con_inflacion),
        Verificacion("oferta pura ⇒ estanflación genuina (m24)", _v_oferta_pura_estanflacion),
        Verificacion("demanda con inercia ⇒ desinfla tarde (m14)", _v_demanda_desinfla_tarde),
        Verificacion("más inercia alarga el episodio", _v_inercia_persiste),
    ],
    notas="Un síntoma, no un diagnóstico: oferta o demanda con inercia. El tratamiento equivocado empeora.",
)
