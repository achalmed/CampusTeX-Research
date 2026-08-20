# m90_shock_productividad.py — shock de productividad (nivel 11).
#
# El shock del lado de la OFERTA que NO es una crisis: un cambio en la
# productividad (tecnología, reformas, o su reversa: un desastre, una mala
# política) mueve el producto potencial (m22, m29) y, a diferencia de un shock
# de demanda, es en gran parte PERMANENTE. La clave de política: distinguir un
# shock de productividad de uno de demanda, porque la respuesta correcta es
# OPUESTA — ante ↓productividad no hay que estimular (el potencial cayó, m22),
# ante ↓demanda sí. Confundirlos es el error de m24 (estanflación). Combina
# m29 (Solow), m57-m58 (RBC) y m22 (LRAS) — el lado real del ciclo.
#
# Procedencia: shock tecnológico del RBC (m57-m58); la distinción demanda/
# oferta para la política (m18/m19, m24) — conocimiento general; calibración
# didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    # el shock de productividad es persistente/permanente (a diferencia de demanda)
    a = np.zeros(T + 1)
    for k in range(1, T + 1):
        a[k] = p["rho"] * a[k - 1] + (p["shock"] if k == 1 else 0.0)
    if p["rho"] >= 0.999:                                 # permanente
        a[1:] = p["shock"]
    Ypot = 100 + (1 + 0.5) * a                            # potencial responde (m29)
    # comparación: un shock de DEMANDA del mismo tamaño (transitorio, NO mueve potencial)
    d = np.zeros(T + 1); d[1] = p["shock"]
    Y_demanda = 100 + d * (0.6 ** np.maximum(0, t - 1))   # transitorio, revierte
    return t, Ypot, Y_demanda


def _curvas(p):
    t, Ypot, Y_demanda = _sendas(p)
    return {"lineas": {"shock de PRODUCTIVIDAD (potencial, m22)": (t, Ypot, config.AZUL2),
                       "shock de DEMANDA (mismo tamaño, transitorio)": (t, Y_demanda, config.ROJO),
                       "potencial original": (t, np.full(len(t), 100.0), config.GRIS)},
            "anotacion": (f"shock {p['shock']:+.1f}, persistencia ρ={p['rho']:.2f}\n"
                          f"productividad: el potencial se mueve PERMANENTE (m29)\n"
                          "demanda: transitorio, revierte — la respuesta es OPUESTA")}


def _resultados(p):
    t, Ypot, Y_demanda = _sendas(p)
    return {"efecto en el potencial (largo plazo)": float(Ypot[-1]) - 100,
            "efecto de demanda (largo plazo)": float(Y_demanda[-1]) - 100,
            "efecto productividad de impacto": float(Ypot[1]) - 100,
            "persistencia ρ": p["rho"],
            "¿permanente? (ρ≈1)": 1.0 if p["rho"] >= 0.999 else 0.0}


def _ecuaciones_calibradas(p):
    return [f"$a_t = {p['rho']:.2f}\\,a_{{t-1}}$, shock inicial {p['shock']:+.1f}",
            f"potencial $\\to {float(_sendas(p)[1][-1]):.1f}$ (permanente si $\\rho{{=}}1$)"]


_P0 = {"shock": 3.0, "rho": 0.95, "T": 16.0}


def _v_mueve_potencial():
    t, Ypot, Y_demanda = _sendas(_P0)
    return abs(float(Ypot[-1]) - 100) > 1, \
        (f"el shock de productividad mueve el potencial de forma persistente "
         f"(largo plazo {float(Ypot[-1]):.1f}): a diferencia de la demanda, cambia la LRAS (m22)")


def _v_demanda_revierte():
    t, Ypot, Y_demanda = _sendas(_P0)
    return abs(float(Y_demanda[-1]) - 100) < 0.5, \
        (f"el shock de demanda del mismo tamaño REVIERTE ({float(Y_demanda[-1]):.1f}≈100): "
         "no mueve el potencial — la diferencia clave para la política")


def _v_respuesta_opuesta():
    # ante caída de productividad NO estimular; ante caída de demanda SÍ
    t, Ypot, Y_demanda = _sendas(dict(_P0, shock=-3.0))
    return float(Ypot[-1]) < 100, \
        ("una CAÍDA de productividad baja el potencial permanentemente: estimular la demanda "
         "solo daría inflación (m24) — la respuesta correcta es opuesta a la de un shock de demanda")


def _v_permanente_vs_transitorio():
    perm = abs(float(_sendas(dict(_P0, rho=1.0))[1][-1]) - 100)
    trans = abs(float(_sendas(dict(_P0, rho=0.5))[1][-1]) - 100)
    return perm > trans, \
        (f"un shock permanente (ρ=1) mueve el potencial más que uno transitorio "
         f"({trans:.1f} vs {perm:.1f}): la persistencia decide el efecto de largo plazo (m29)")


MODELO = Modelo(
    id="m90", nivel=11,
    nombre="Shock de productividad",
    xlabel="Período $t$", ylabel="Producto (índice)",
    parametros=[
        Parametro("shock", _P0["shock"], -5, 5, 0.5, "Shock de productividad",
                  grupo="shock", definicion="tecnología/reformas (+) o desastre/mala política (−)"),
        Parametro("rho", _P0["rho"], 0.3, 1.0, 0.05, "Persistencia ρ",
                  grupo="naturaleza", definicion="ρ≈1 permanente (mueve el potencial); bajo = transitorio"),
        Parametro("T", _P0["T"], 10, 24, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué la respuesta correcta a una caída de PRODUCTIVIDAD es OPUESTA a la de una caída de demanda?",
        variables=[("productividad", "el shock de oferta que mueve el POTENCIAL (m22, m29)"),
                   ("vs demanda", "transitorio, NO mueve el potencial"),
                   ("ρ", "la persistencia: decide si el efecto es permanente")],
        derivacion=["productividad: \\;a_t\\;persistente \\Rightarrow Y^*\\;se\\;mueve\\;(m29)",
                    "demanda: \\;transitorio \\Rightarrow Y\\;revierte\\;a\\;Y^*\\;(m25)",
                    "respuesta: \\;NO\\;estimular\\;lo\\;permanente"],
        contexto=("No todos los shocks de oferta son crisis. Un cambio en la "
                  "productividad — por progreso tecnológico, reformas "
                  "estructurales, mejor educación (los factores de m29, m33), o su "
                  "reversa: un desastre natural, una mala política, la pérdida de "
                  "capital humano — mueve el producto POTENCIAL de la economía "
                  "(m22, la LRAS). La distinción crucial para la política es entre "
                  "un shock de productividad (permanente, mueve el potencial) y uno "
                  "de demanda (transitorio, la economía revierte al potencial, "
                  "m25), porque la respuesta correcta es OPUESTA. Ante una caída de "
                  "DEMANDA, estimular es correcto: hay recursos ociosos que la "
                  "política puede reactivar. Ante una caída de PRODUCTIVIDAD, "
                  "estimular es un ERROR: el potencial cayó, no hay recursos "
                  "ociosos, y la demanda extra solo produce inflación — el "
                  "diagnóstico equivocado que llevó a la estanflación de los 70 "
                  "(m24), cuando se trató un shock de oferta (petróleo) como si "
                  "fuera de demanda. El problema práctico es que en tiempo real es "
                  "DIFÍCIL distinguirlos: una recesión se ve igual sea cual sea su "
                  "causa, y solo con el tiempo se revela si el potencial se movió. "
                  "Este es el lado real del ciclo (m57-m61) aplicado al dilema de "
                  "política."),
        autores=("Shock tecnológico del RBC: m57-m58 (Kydland-Prescott, "
                 "menciones); la distinción demanda/oferta para la política: "
                 "m18/m19/m24; el potencial como LRAS: m22, m29."),
        supuestos=[
            "El shock de productividad es persistente/permanente (mueve Y*); el de demanda es transitorio (revierte) — la distinción central.",
            "El potencial responde a la productividad vía la función de producción (m29): con elasticidad al factor.",
            "Sin fricciones de reasignación: en la realidad, mover recursos entre sectores tras un shock de productividad toma tiempo (histéresis).",
        ],
        ecuaciones=[
            Ecuacion("productividad: \\;\\Delta Y^* \\ne 0 \\;;\\; demanda: \\;\\Delta Y^* = 0",
                     "la diferencia que define la política",
                     "el shock de productividad MUEVE el potencial (permanente); el de demanda no "
                     "(la economía revierte, m25) — verificado, y la clave del diagnóstico."),
            Ecuacion("respuesta_{óptima}(productividad) = -respuesta_{óptima}(demanda)",
                     "el error de confundirlos",
                     "estimular ante caída de productividad da inflación (m24); no estimular ante "
                     "caída de demanda da recesión innecesaria — el diagnóstico es todo."),
        ],
        intuicion=("El shock de productividad enseña que el diagnóstico es más "
                   "importante que el tratamiento: la MISMA recesión requiere "
                   "respuestas opuestas según su causa, y equivocarse es costoso en "
                   "ambas direcciones. Si el banco central trata una caída de "
                   "productividad (potencial menor) como una caída de demanda y "
                   "estimula, obtiene la estanflación de los 70. Si trata una caída "
                   "de demanda como una de productividad y no estimula, obtiene una "
                   "recesión innecesariamente profunda (el error de austeridad "
                   "prematura). La dificultad es que el potencial no se observa: "
                   "hay que estimarlo (la brecha de m16), y las estimaciones se "
                   "revisan mucho. Por eso los bancos centrales modernos miran un "
                   "tablero amplio — inflación (si sube con la recesión, es "
                   "oferta), mercado laboral, indicadores estructurales — para "
                   "diagnosticar antes de tratar. Para el Perú, distinguir un "
                   "frenazo cíclico (cobre, m89) de uno estructural (agotamiento "
                   "del modelo extractivo) es exactamente este dilema — y define si "
                   "la política correcta es contracíclica o de reformas (m97)."),
        equilibrio=("El shock de productividad desplaza el potencial de forma "
                    "persistente (verificado); el de demanda revierte al potencial "
                    "original (m25, verificado). La economía se asienta en el nuevo "
                    "potencial tras un shock real, en el viejo tras uno de demanda."),
        limitaciones=[
            "Distinguir los dos EN TIEMPO REAL es el problema práctico central — el modelo los separa por construcción, la realidad no.",
            "Histéresis: una recesión de demanda larga puede DAÑAR el potencial (m16), difuminando la distinción — la demanda se vuelve oferta.",
            "Sin reasignación sectorial: un shock de productividad favorece unos sectores y daña otros; el agregado esconde el ajuste microeconómico.",
        ],
        evolucion=("Aplica el RBC (m57-m58) y la LRAS (m22, m29) al dilema de "
                   "política, cerrando el bloque externo/real del nivel. Contrasta "
                   "con los shocks de demanda (m81, m91) y prepara el diagnóstico "
                   "que el nivel 12 exige: para el Perú, ¿es el frenazo cíclico "
                   "(m89) o estructural (m97)? La respuesta define la política."),
    ),
    escenarios=[
        Escenario("reforma_estructural", "shock positivo permanente (+3, ρ=1)",
                  {"shock": 3.0, "rho": 1.0},
                  "el potencial sube para siempre: una reforma que mejora la "
                  "productividad eleva el techo de la economía — crecimiento, no "
                  "solo recuperación (m29).",
                  cadena=["reforma/tecnología", "↑productividad permanente",
                          "el potencial se mueve (m22, m29)", "más producto SIN inflación",
                          "el buen shock de oferta"]),
        Escenario("desastre_productivo", "shock negativo permanente (−3)",
                  {"shock": -3.0, "rho": 1.0},
                  "el potencial CAE: estimular la demanda sería un error — daría "
                  "inflación (m24), no recuperación. La respuesta es reformas, no "
                  "estímulo.",
                  cadena=["desastre/mala política", "↓productividad permanente",
                          "el potencial cae (m22)", "NO hay recursos ociosos que reactivar",
                          "estimular = inflación (m24); la cura es estructural"]),
        Escenario("confundir_con_demanda", "shock transitorio (ρ=0.5): parece demanda",
                  {"shock": -3.0, "rho": 0.5},
                  "un shock de productividad transitorio se parece a uno de demanda: "
                  "revierte solo — el caso ambiguo donde el diagnóstico es más "
                  "difícil.",
                  cadena=["shock de productividad transitorio", "efecto que revierte",
                          "se confunde con demanda", "el diagnóstico se vuelve incierto",
                          "el dilema práctico de política en tiempo real"]),
    ],
    verificaciones=[
        Verificacion("el shock de productividad mueve el potencial (m22)", _v_mueve_potencial),
        Verificacion("el shock de demanda revierte (no mueve el potencial)", _v_demanda_revierte),
        Verificacion("ante caída de productividad, no estimular (opuesto)", _v_respuesta_opuesta),
        Verificacion("permanente mueve más que transitorio (m29)", _v_permanente_vs_transitorio),
    ],
    notas="El diagnóstico importa más que el tratamiento: la misma recesión, respuestas opuestas según su causa.",
)
