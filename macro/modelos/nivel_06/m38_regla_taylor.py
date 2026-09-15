"""simuladores/macro/modelos/nivel_06/m38_regla_taylor.py — la regla de Taylor (nivel 6, ancla).

  i = r* + π + φ_π(π − π*) + φ_y·brecha
La política monetaria como FUNCIÓN DE REACCIÓN: ante inflación alta o
sobrecalentamiento, la tasa nominal sube MÁS que uno a uno con π (principio
de Taylor: 1+φ_π > 1), de modo que la tasa REAL se endurece y estabiliza.
El nivel 12 (m100) estimará esta regla con la tasa de referencia del BCRP.

Procedencia: Taylor (1993, "Discretion versus policy rules in practice" —
mención): describía a la Fed 1987-92 con φ_π=φ_y=0.5 y se volvió normativa.
Conocimiento general; calibración: la original de Taylor.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _i(p, pi=None, brecha=None):
    pi = p["pi"] if pi is None else pi
    brecha = p["brecha"] if brecha is None else brecha
    return p["r_nat"] + pi + p["phi_pi"] * (pi - p["pi_meta"]) + p["phi_y"] * brecha


def _curvas(p):
    pi = np.linspace(-1, 10, 200)
    regla = _i(p, pi=pi)
    neutral = p["r_nat"] + pi
    return {"lineas": {"regla: $i(\\pi)$ con tu brecha": (pi, regla, config.AZUL2),
                       "postura neutral: $i = r^* + \\pi$": (pi, neutral, config.GRIS)},
            "equilibrio": (p["pi"], float(_i(p))),
            "puntos": [(p["pi_meta"], p["r_nat"] + p["pi_meta"],
                        f"meta: $(\\pi^*, r^*{{+}}\\pi^*)$")],
            "anotacion": (f"$i = {float(_i(p)):.2f}\\%$ → tasa real $= {float(_i(p)) - p['pi']:.2f}\\%$\n"
                          f"pendiente $= 1+\\phi_\\pi = {1 + p['phi_pi']:.2f} > 1$: "
                          "principio de Taylor\n"
                          "sobre la línea gris = apretar; debajo = estimular")}


def _resultados(p):
    i = float(_i(p))
    return {"tasa recomendada i (%)": i,
            "tasa real implícita i−π (%)": i - p["pi"],
            "postura vs neutral (pp)": i - (p["r_nat"] + p["pi"]),
            "respuesta a +1pp de π (di/dπ)": 1 + p["phi_pi"],
            "respuesta a +1pp de brecha": p["phi_y"]}


def _ecuaciones_calibradas(p):
    return [f"$i = {p['r_nat']:.1f} + {p['pi']:.1f} + {p['phi_pi']:.2f}\\,({p['pi']:.1f}-{p['pi_meta']:.1f}) "
            f"+ {p['phi_y']:.2f} \\times {p['brecha']:.1f}$",
            f"$i = {float(_i(p)):.2f}\\%, \\quad i-\\pi = {float(_i(p)) - p['pi']:.2f}\\%$"]


_P0 = {"pi": 4.0, "brecha": 0.0, "pi_meta": 2.0, "r_nat": 2.0,
       "phi_pi": 0.5, "phi_y": 0.5}


def _v_principio_taylor():
    d = float(_i(_P0, pi=5.0) - _i(_P0, pi=4.0))
    return abs(d - (1 + _P0["phi_pi"])) < 1e-12 and d > 1, \
        (f"di/dπ = {d:.2f} > 1: ante más inflación la tasa REAL sube — sin este "
         "principio la regla desestabiliza (valida la espiral de m14)")


def _v_neutral_en_meta():
    i = float(_i(_P0, pi=_P0["pi_meta"], brecha=0.0))
    return abs(i - (_P0["r_nat"] + _P0["pi_meta"])) < 1e-12, \
        f"en (π=π*, brecha=0) la regla da exactamente la tasa neutral r*+π* = {i:.1f}%"


def _v_zlb():
    i = float(_i(_P0, pi=0.5, brecha=-5.0))
    return i < 1.0, (f"recesión profunda con π baja pide i = {i:.2f}%: la regla choca con el "
                     "piso de m12 — el ZLB es el límite operativo de Taylor")


def _v_real_endurece():
    reales = [float(_i(_P0, pi=x)) - x for x in (2.0, 4.0, 6.0)]
    return reales[0] < reales[1] < reales[2], \
        (f"la tasa real sube con π ({reales[0]:.1f} → {reales[1]:.1f} → {reales[2]:.1f}%): "
         "apretar de verdad, no solo nominalmente")


MODELO = Modelo(
    id="m38", nivel=6,
    nombre="Regla de Taylor",
    xlabel="Inflación $\\pi$ (%)", ylabel="Tasa de política $i$ (%)",
    parametros=[
        Parametro("pi", _P0["pi"], -1, 10, 0.5, "Inflación observada π (%)", grupo="situación",
                  definicion="lo que el banco central ve al decidir"),
        Parametro("brecha", _P0["brecha"], -6, 6, 0.5, "Brecha del producto (%)", grupo="situación",
                  definicion="la de m16 — con toda su incertidumbre de medición"),
        Parametro("phi_pi", _P0["phi_pi"], 0.0, 1.5, 0.05, "Respuesta a inflación φ_π", grupo="preferencias",
                  definicion="cuánto extra (sobre 1:1) responde la tasa a π"),
        Parametro("phi_y", _P0["phi_y"], 0.0, 1.5, 0.05, "Respuesta a la brecha φ_y", grupo="preferencias",
                  definicion="cuánto pesa estabilizar actividad"),
        Parametro("pi_meta", _P0["pi_meta"], 0, 5, 0.5, "Meta de inflación π* (%)", grupo="régimen",
                  definicion="el ancla del régimen (m40)"),
        Parametro("r_nat", _P0["r_nat"], 0, 4, 0.25, "Tasa natural r* (%)", grupo="régimen",
                  definicion="la real de equilibrio — NO observable"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo decide un banco central su tasa — y qué lo separa de repetir los años 70?",
        variables=[("i", "tasa de política nominal — el instrumento (m39)"),
                   ("π, brecha", "el estado de la economía — los insumos"),
                   ("φ_π, φ_y", "las preferencias del banco central — su 'personalidad'"),
                   ("r*, π*", "los anclajes del régimen — inciertos el primero, público el segundo")],
        derivacion=["i = r^* + \\pi + \\phi_\\pi(\\pi - \\pi^*) + \\phi_y\\,\\tilde{y}",
                    "\\frac{di}{d\\pi} = 1 + \\phi_\\pi > 1 \\;\\;(principio\\;de\\;Taylor)",
                    "\\Rightarrow \\frac{d(i-\\pi)}{d\\pi} = \\phi_\\pi > 0: \\;la\\;REAL\\;endurece"],
        contexto=("En 1993 John Taylor mostró que la Fed de Greenspan — supuestamente "
                  "discrecional — se comportaba como una fórmula simple con φ_π=φ_y=0.5. "
                  "La descripción se volvió receta: la regla resume medio siglo de "
                  "lecciones (los 70: responder MENOS que 1:1 a la inflación deja caer "
                  "la tasa real y alimenta la espiral de m14; Volcker: responder de "
                  "más, cuesta recesiones). Hoy es la vara con que se evalúa a todo "
                  "banco central — incluido el BCRP, cuya regla estimaremos con datos "
                  "reales en m100."),
        autores=("Taylor (1993, mención); el 'principio de Taylor' como condición de "
                 "estabilidad viene del análisis posterior (Woodford, mención); "
                 "crítica de medición en tiempo real: Orphanides (mención)."),
        supuestos=[
            "r* y la brecha son observables al decidir — FALSO en tiempo real: es la crítica empírica central (Orphanides).",
            "Respuesta lineal y simétrica (subidas y bajadas iguales; sin ZLB dentro de la regla).",
            "El instrumento es la tasa nominal de corto plazo y su transmisión funciona (m39, m10).",
        ],
        ecuaciones=[
            Ecuacion("i = r^* + \\pi + \\phi_\\pi(\\pi-\\pi^*) + \\phi_y\\,\\tilde{y}",
                     "la función de reacción",
                     "los dos primeros términos mantienen la real neutral; los dos últimos son la "
                     "medicina: extra de tasa por inflación desviada y por brecha."),
            Ecuacion("1 + \\phi_\\pi > 1", "el principio de Taylor",
                     "la frontera entre estabilizar y desestabilizar: con φ_π<0 la real CAE cuando "
                     "π sube — el banco central acomodaticio de los 70 en una desigualdad."),
        ],
        intuicion=("La regla es un termostato con dos sensores: si la casa se "
                   "calienta (π sobre la meta, brecha positiva), enfría MÁS que "
                   "proporcionalmente; el gráfico lo muestra como la brecha creciente "
                   "entre la regla y la línea neutral. Su valor no es la precisión "
                   "decimal sino la DISCIPLINA: hace predecible al banco central, y "
                   "esa predictibilidad ancla expectativas (m40-m41) — la mitad del "
                   "trabajo la hace la regla sin mover la tasa."),
        equilibrio=("En (π*, 0) la regla se posa en la neutral r*+π* (verificado "
                    "exacto): el régimen descansa donde su meta se cumple. La "
                    "estabilidad dinámica que el principio garantiza se demuestra en "
                    "el modelo completo (m56)."),
        limitaciones=[
            "r* y brecha se miden con años de retraso: reglas en tiempo real cometen errores sistemáticos (los 70 se re-leen como brechas mal medidas — Orphanides, mención).",
            "El ZLB la rompe por abajo (verificado: recesión honda pide i<1%): allí mandan m12 y las políticas no convencionales.",
            "No ve estabilidad financiera ni tipo de cambio — para economías como la peruana, la regla real del BCRP incluye más argumentos (m100 lo contrastará).",
        ],
        evolucion=("La regla es el puente al régimen completo: m39 muestra el "
                   "instrumento que la implementa (corredor), m40 el ancla que la "
                   "rodea (metas), m41 por qué ATARSE a una regla vence a la "
                   "discreción, y m56 la mete dentro del modelo nuevo keynesiano de "
                   "3 ecuaciones. En el nivel 12, m100-m101 la estiman para el BCRP."),
    ),
    escenarios=[
        Escenario("brote_inflacionario", "π salta de 4% a 6% con brecha cero",
                  {"pi": 6.0},
                  "la regla pide i=10%: +2pp de π → +3pp de tasa — la real sube 1pp; "
                  "eso es 1+φ_π>1 trabajando.",
                  cadena=["↑π", "π−π* se abre", "i sube MÁS que π (1+φ_π)",
                          "↑ tasa real", "↓DA (m10/m23)", "π cede hacia la meta"]),
        Escenario("recesion_con_deflacion", "brecha −4% y π en 0.5%",
                  {"pi": 0.5, "brecha": -4.0},
                  "la regla pide i=0.75%: al borde del piso — la frontera con la "
                  "trampa (m12) donde Taylor deja de bastar.",
                  cadena=["brecha ≪ 0 y π ≈ 0", "la regla pide tasa mínima",
                          "i roza el ZLB", "si pide i<0: territorio m12",
                          "entran las políticas no convencionales"]),
        Escenario("sobrecalentamiento", "brecha +3% con π = 5%",
                  {"pi": 5.0, "brecha": 3.0},
                  "i=10%: los dos sensores suman — la respuesta dura que evita "
                  "convalidar el recalentamiento (m24, escenario Burns, en reversa).",
                  cadena=["π y brecha altos a la vez", "ambos términos suman",
                          "i muy sobre la neutral", "frenazo deliberado de la DA"]),
        Escenario("banco_acomodaticio", "φ_π = 0: la Fed de los 70",
                  {"phi_pi": 0.0},
                  "di/dπ = 1: la real NUNCA sube con π — el termostato roto que "
                  "convalidó la espiral de m14; el principio de Taylor existe por esto.",
                  cadena=["φ_π = 0", "i sube solo 1:1 con π", "tasa real constante",
                          "la inflación no encuentra freno", "espiral de m14 convalidada"]),
    ],
    verificaciones=[
        Verificacion("principio de Taylor: di/dπ = 1+φ_π > 1", _v_principio_taylor),
        Verificacion("en la meta, la regla da la tasa neutral exacta", _v_neutral_en_meta),
        Verificacion("recesión profunda empuja al ZLB (frontera con m12)", _v_zlb),
        Verificacion("la tasa REAL endurece con la inflación", _v_real_endurece),
    ],
    notas="El termostato de la macro moderna: 1+φ_π>1 separa a Volcker de Burns. m100 lo estimará para el BCRP.",
)
