"""simuladores/macro/modelos/nivel_07/m46_tipo_cambio_real.py — tipo de cambio real: la competitividad (nivel 7).

  RER = E·P*/P     (índices; base 100)
Cuántas canastas locales cuesta una canasta extranjera: el precio relativo
que decide exportaciones e importaciones. En variaciones (exacto):
  RER'/RER = (1+dE)(1+dP*)/(1+dP)   ≈   dRER ≈ dE + dP* − dP
La lección amarga de las inflaciones altas: depreciar el E nominal NO
devalúa en términos reales si la inflación local se lo come (dE = dP ⇒
RER intacto) — el hámster cambiario de los años 80.

Procedencia: definición estándar (conocimiento general); calibración
didáctica en índices.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _rer(p):
    return 100.0 * (1 + p["dE"] / 100) * (1 + p["dPstar"] / 100) / (1 + p["dP"] / 100)


def _curvas(p):
    rer = _rer(p)
    aprox = p["dE"] + p["dPstar"] - p["dP"]
    cats = ["$dE$\n(nominal)", "$dP^*$\n(inflación ext.)", "$-dP$\n(inflación local)",
            "$\\Delta RER$\n(exacto)"]
    vals = [p["dE"], p["dPstar"], -p["dP"], rer - 100.0]
    cols = [config.AZUL2, config.VERDE, config.ROJO, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$RER = 100\\,\\frac{{(1+{p['dE'] / 100:.2f})(1+{p['dPstar'] / 100:.2f})}}"
                          f"{{1+{p['dP'] / 100:.2f}}} = {rer:.1f}$\n"
                          f"aproximación: $dE+dP^*-dP = {aprox:+.1f}$\n"
                          "RER↓ = apreciación real = pérdida de competitividad")}


def _resultados(p):
    rer = _rer(p)
    return {"RER (índice, base 100)": rer,
            "variación real exacta (%)": rer - 100.0,
            "aproximación dE+dP*−dP (%)": p["dE"] + p["dPstar"] - p["dP"],
            "dirección": 1.0 if rer > 100 else (-1.0 if rer < 100 else 0.0)}


def _ecuaciones_calibradas(p):
    return [f"$RER = E\\,P^*/P$",
            f"$RER = 100 \\times {1 + p['dE'] / 100:.3f} \\times {1 + p['dPstar'] / 100:.3f} "
            f"/ {1 + p['dP'] / 100:.3f} = {_rer(p):.1f}$"]


_P0 = {"dE": 5.0, "dPstar": 2.0, "dP": 3.0}


def _v_exacto():
    rer = _rer(_P0)
    a_mano = 100 * 1.05 * 1.02 / 1.03
    return abs(rer - a_mano) < 1e-9, f"RER multiplicativo exacto = {rer:.2f}"


def _v_aproximacion():
    exact = _rer(_P0) - 100
    aprox = _P0["dE"] + _P0["dPstar"] - _P0["dP"]
    return abs(exact - aprox) < 0.5, (f"con tasas moderadas la suma dE+dP*−dP ({aprox:+.1f}) "
                                      f"aproxima al exacto ({exact:+.2f}) con error < 0.5 pp")


def _v_hamster():
    rer = _rer({"dE": 40.0, "dPstar": 0.0, "dP": 40.0})
    return abs(rer - 100.0) < 1e-9, ("depreciar 40% con inflación local del 40% deja el RER "
                                     "EXACTAMENTE en 100: el hámster cambiario de los 80 — "
                                     "correr para quedarse en el sitio")


def _v_inflacion_aprecia():
    rer = _rer({"dE": 0.0, "dPstar": 0.0, "dP": 10.0})
    return rer < 100, (f"con E quieto, 10% de inflación local aprecia el RER a {rer:.1f}: "
                       "se pierde competitividad sin que el dólar se mueva")


MODELO = Modelo(
    id="m46", nivel=7,
    nombre="Tipo de cambio real",
    xlabel="", ylabel="Contribuciones (%)",
    parametros=[
        Parametro("dE", _P0["dE"], -20, 60, 1, "Depreciación nominal dE (%)", grupo="nominal",
                  definicion="cuánto sube el PEN/USD (m45)"),
        Parametro("dP", _P0["dP"], 0, 60, 1, "Inflación local dP (%)", grupo="precios",
                  definicion="la que erosiona la depreciación (m34-m40)"),
        Parametro("dPstar", _P0["dPstar"], 0, 15, 0.5, "Inflación externa dP* (%)", grupo="precios"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuándo una devaluación es real y cuándo es solo correr en la rueda del hámster?",
        variables=[("RER", "canastas locales por canasta extranjera — la competitividad"),
                   ("E", "el nominal de m45 — solo un tercio de la historia"),
                   ("P, P*", "los niveles de precios — los otros dos tercios")],
        derivacion=["RER = \\frac{E\\,P^*}{P}",
                    "\\frac{RER'}{RER} = \\frac{(1+dE)(1+dP^*)}{1+dP}",
                    "dRER \\approx dE + dP^* - dP"],
        contexto=("Un exportador no compite con el tipo de cambio del periódico sino "
                  "con el REAL: cuántos costos locales caben en un precio en dólares. "
                  "Por eso las devaluaciones de los años 80 fracasaban en cadena: "
                  "cada salto del dólar pasaba a precios (indexación mediante) y el "
                  "RER volvía al punto de partida — devaluar era correr en la rueda. "
                  "Y por eso la apreciación real silenciosa (inflación local con E "
                  "quieto) mata transables sin que nadie vea moverse el dólar: la "
                  "mecánica de la enfermedad holandesa (m88)."),
        autores=("Definición estándar de economía internacional (conocimiento "
                 "general); el vínculo con competitividad y enfermedad holandesa: "
                 "literatura de los 80 (menciones)."),
        supuestos=["Canastas comparables entre países (índices de precios agregados).",
                   "Un solo RER bilateral: el multilateral pondera socios (mención; el del BCRP en m102).",
                   "El passthrough dE→dP queda EXÓGENO aquí: es la perilla dP (su endogeneidad es m85/m113)."],
        ecuaciones=[
            Ecuacion("RER = \\frac{E\\,P^*}{P}", "el precio relativo de las canastas",
                     "numerador: lo extranjero puesto en soles; denominador: lo local. RER alto = "
                     "país barato = transables felices."),
            Ecuacion("dRER \\approx dE + dP^* - dP", "la aritmética de la competitividad",
                     "tres perillas y una resta: la depreciación nominal solo gana lo que la "
                     "inflación local no se coma."),
        ],
        intuicion=("El RER es el marcador del partido; el E nominal, solo el nombre "
                   "del estadio. Depreciar con inflación igual es empate 0-0 "
                   "(verificado exacto); inflación local con E fijo es autogol; y la "
                   "combinación ganadora — depreciación nominal CON ancla de "
                   "inflación (m40) — es exactamente lo que un régimen de metas "
                   "permite y las economías indexadas de los 80 no podían."),
        equilibrio=("Identidad de medición, no equilibrio. Su nivel 'de equilibrio' "
                    "es la pregunta del PPP (m47: ¿RER constante a largo plazo?) y "
                    "de los fundamentos (términos de intercambio, m105)."),
        limitaciones=[
            "Índices agregados esconden composición: el RER del cobre no es el del textil (transables vs no transables — mención Balassa-Samuelson).",
            "Bilateral: el efectivo/multilateral pondera por socios comerciales (m102 usará el del BCRP).",
            "dP exógena: en la realidad el passthrough conecta dE→dP y muerde la ganancia real (m85, m113).",
        ],
        evolucion=("Con el precio relativo definido, m47 pregunta si tiene ancla "
                   "(PPP: ¿el RER vuelve?), m48 le pone motor financiero (UIP) y "
                   "m49 lo integra a la demanda (XN(E) del Mundell-Fleming). Los "
                   "datos peruanos — RER multilateral del BCRP — llegan en m102."),
    ),
    escenarios=[
        Escenario("devaluacion_real", "dE=15% con inflación anclada (dP=3%)",
                  {"dE": 15.0, "dP": 3.0},
                  "el RER gana ~13.6%: la devaluación QUE SÍ funciona — posible "
                  "solo porque el ancla de m40 impide el passthrough total.",
                  cadena=["↑E nominal", "el ancla contiene dP", "RER ≈ dE−dP > 0",
                          "transables más competitivos", "XN mejora (m49)"]),
        Escenario("rueda_del_hamster", "dE=40% y dP=40% (indexación total)",
                  {"dE": 40.0, "dP": 40.0},
                  "RER = 100.0 exacto: cuarenta puntos de devaluación para quedarse "
                  "en el mismo lugar — los 80 en una barra dorada de altura cero.",
                  cadena=["devaluación", "indexación: precios la siguen 1:1",
                          "dE = dP", "RER intacto", "otra vuelta a la rueda"]),
        Escenario("apreciacion_silenciosa", "E quieto, inflación local 10%",
                  {"dE": 0.0, "dP": 10.0},
                  "el RER cae 9.1% sin que el dólar se mueva: la pérdida de "
                  "competitividad que nadie ve en el titular cambiario.",
                  cadena=["dP > dP* con E fijo", "los costos locales suben en dólares",
                          "RER↓ (apreciación real)", "transables no mineros sufren (m88)"]),
    ],
    verificaciones=[
        Verificacion("RER multiplicativo exacto", _v_exacto),
        Verificacion("aproximación dE+dP*−dP acotada", _v_aproximacion),
        Verificacion("hámster: dE=dP deja RER exacto en 100", _v_hamster),
        Verificacion("inflación local con E fijo aprecia el RER", _v_inflacion_aprecia),
    ],
    notas="El RER es el marcador del partido; el E nominal, solo el nombre del estadio.",
)
