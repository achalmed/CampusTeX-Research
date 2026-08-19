# m48_uip.py — paridad descubierta de intereses (UIP) — nivel 7.
#
# Arbitraje entre depósitos en soles y en dólares SIN cobertura:
#   (1+i) = (1+i* + ρ) · E^e/E      (ρ: prima de riesgo país)
#   →  E = E^e · (1+i* + ρ)/(1+i)
# El tipo de cambio DE HOY lo fijan la tasa local, la externa, el riesgo y la
# expectativa de mañana. De aquí salen los reflejos cambiarios modernos:
# subir la tasa aprecia HOY; si la FED sube, el sol se deprecia HOY (m111);
# si sube el riesgo país, se deprecia con TODO lo demás constante.
#
# Procedencia: condición de arbitraje estándar (manuales de economía
# internacional) — conocimiento general; falla empírica (forward premium
# puzzle, Fama 1984): mención.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _E(p, i=None):
    i = p["i"] if i is None else i
    return p["Ee"] * (1 + (p["i_star"] + p["prima"]) / 100) / (1 + i / 100)


def _curvas(p):
    i = np.linspace(1, 9, 200)
    base = p["Ee"] * (1 + (p["i_star"]) / 100) / (1 + i / 100)
    con_prima = p["Ee"] * (1 + (p["i_star"] + p["prima"]) / 100) / (1 + i / 100)
    lineas = {"$E(i)$ sin prima de riesgo": (i, base, config.GRIS),
              f"$E(i)$ con prima $\\rho={p['prima']:.1f}$": (i, con_prima, config.AZUL2)}
    return {"lineas": lineas,
            "equilibrio": (p["i"], float(_E(p))),
            "anotacion": (f"$E = {p['Ee']:.2f} \\times \\frac{{1+{(p['i_star'] + p['prima']) / 100:.3f}}}"
                          f"{{1+{p['i'] / 100:.3f}}} = {float(_E(p)):.3f}$\n"
                          f"depreciación esperada: {100 * (p['Ee'] / float(_E(p)) - 1):.2f}%\n"
                          "subir la tasa aprecia HOY; el riesgo deprecia HOY")}


def _resultados(p):
    E = float(_E(p))
    return {"E hoy (PEN/USD)": E,
            "depreciación esperada (Ee/E − 1, %)": 100 * (p["Ee"] / E - 1),
            "retorno en soles (1+i)": 1 + p["i"] / 100,
            "retorno en dólares llevado a soles": (1 + (p["i_star"] + p["prima"]) / 100) * p["Ee"] / E,
            "dE/di (numérica)": (float(_E(p, i=p["i"] + 0.5)) - float(_E(p, i=p["i"] - 0.5)))}


def _ecuaciones_calibradas(p):
    return [f"$(1+{p['i'] / 100:.3f}) = (1+{(p['i_star'] + p['prima']) / 100:.3f}) \\times "
            f"{p['Ee']:.2f}/{float(_E(p)):.3f}$",
            f"$E = {float(_E(p)):.3f}$"]


_P0 = {"i": 5.0, "i_star": 3.0, "Ee": 3.60, "prima": 0.0}


def _v_arbitraje():
    r = _resultados(_P0)
    dif = abs(r["retorno en soles (1+i)"] - r["retorno en dólares llevado a soles"])
    return dif < 1e-12, ("los dos depósitos rinden EXACTAMENTE lo mismo en soles: "
                         f"UIP como arbitraje sin billete gratis (dif={dif:.1e})")


def _v_tasa_aprecia():
    e0, e1 = float(_E(_P0)), float(_E(_P0, i=7.0))
    return e1 < e0, (f"subir la tasa local (5%→7%) aprecia HOY (E {e0:.3f}→{e1:.3f}): "
                     "el premio en soles exige menos depreciación futura esperada")


def _v_fed_deprecia():
    e0 = float(_E(_P0))
    e1 = float(_E(dict(_P0, i_star=5.5)))
    return e1 > e0, (f"si la FED sube (3%→5.5%), el sol se deprecia HOY (E {e0:.3f}→{e1:.3f}) "
                     "sin que el Perú haya hecho nada: el canal de m111")


def _v_riesgo_deprecia():
    e0 = float(_E(_P0))
    e1 = float(_E(dict(_P0, prima=3.0)))
    return e1 > e0, (f"+3pp de riesgo país deprecian E de {e0:.3f} a {e1:.3f} con tasas "
                     "intactas: el precio del miedo entra directo al cambio")


MODELO = Modelo(
    id="m48", nivel=7,
    nombre="Paridad descubierta de intereses (UIP)",
    xlabel="Tasa de interés local $i$ (%)", ylabel="Tipo de cambio $E$ hoy (PEN/USD)",
    parametros=[
        Parametro("i", _P0["i"], 1, 9, 0.25, "Tasa local i (%)", grupo="tasas",
                  definicion="la de política del BCRP vía m39"),
        Parametro("i_star", _P0["i_star"], 0.5, 7, 0.25, "Tasa externa i* (%)", grupo="tasas",
                  definicion="la FED: exógena para un país pequeño"),
        Parametro("prima", _P0["prima"], 0, 6, 0.25, "Prima de riesgo país ρ (pp)", grupo="riesgo",
                  definicion="lo extra que exige el capital por quedarse"),
        Parametro("Ee", _P0["Ee"], 3.0, 4.5, 0.05, "Tipo de cambio esperado Ee", grupo="expectativas",
                  definicion="a dónde cree el mercado que va E — puede autocumplirse (m74)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué el dólar de HOY se mueve con tasas y miedos de MAÑANA — sin que pase un solo contenedor por la aduana?",
        variables=[("E", "el cambio de hoy — endógeno al arbitraje financiero"),
                   ("i, i*", "las tasas — la local elige (m38); la FED, no"),
                   ("ρ", "la prima — el precio del miedo"),
                   ("Ee", "la expectativa — el ancla (o la mecha, m74)")],
        derivacion=["retorno\\;local: \\;1+i",
                    "retorno\\;externo\\;en\\;soles: \\;(1+i^*+\\rho)\\,\\frac{E^e}{E}",
                    "arbitraje \\Rightarrow E = E^e\\,\\frac{1+i^*+\\rho}{1+i}"],
        contexto=("El mercado cambiario de m45 movía flujos de comercio; el de "
                  "verdad mueve STOCKS de portafolio, y esos se reasignan en "
                  "segundos con una sola pregunta: ¿dónde rinde más mi plata, "
                  "contando la depreciación que espero? La UIP es esa pregunta "
                  "hecha ecuación. Explica los reflejos que el mercado de flujos no "
                  "puede: por qué una subida de la FED golpea al sol el mismo día "
                  "(m86/m111), por qué el riesgo político se cobra en el cambio "
                  "antes que en ninguna otra parte, y por qué los bancos centrales "
                  "defienden la moneda con la TASA."),
        autores=("Condición de arbitraje estándar (manuales de economía "
                 "internacional, conocimiento general); la falla empírica "
                 "sistemática es el forward premium puzzle (Fama 1984, mención); "
                 "con expectativas y precios rígidos produce el overshooting de "
                 "Dornbusch (1976, mención)."),
        supuestos=[
            "Movilidad perfecta de capitales y activos sustitutos (salvo la prima ρ).",
            "SIN cobertura ('descubierta'): el riesgo cambiario se corre — por eso aparece ρ.",
            "Ee exógena aquí: anclarla con PPP (m47) da el largo plazo; dejarla libre permite profecías autocumplidas (m74).",
        ],
        ecuaciones=[
            Ecuacion("E = E^e\\,\\frac{1+i^*+\\rho}{1+i}", "el cambio como precio de activo",
                     "E de hoy = expectativa de mañana descontada por el diferencial de "
                     "retornos: sube i y E baja HOY (apreciación) para 'hacer espacio' a la "
                     "depreciación esperada que compense."),
            Ecuacion("i \\approx i^* + \\rho + \\frac{E^e - E}{E}", "la forma en tasas",
                     "la tasa local se descompone en: tasa mundial + riesgo país + depreciación "
                     "esperada — la aritmética de todo informe cambiario."),
        ],
        intuicion=("El tipo de cambio es un precio de ACTIVO: como una acción, "
                   "cotiza el futuro. De ahí sus dos conductas anti-intuitivas: "
                   "(1) las buenas noticias de tasa local aprecian al instante, "
                   "aunque el comercio tarde meses; (2) la expectativa Ee puede "
                   "fabricar su propia realidad — si todos esperan devaluación, la "
                   "UIP la trae al presente, y solo la tasa o las reservas (m50) la "
                   "contienen."),
        equilibrio=("E único dado (i, i*, ρ, Ee) con retornos exactamente igualados "
                    "(verificado). La dinámica completa exige cerrar Ee: con PPP "
                    "(m47) a largo plazo, con Dornbusch a corto (mención)."),
        limitaciones=[
            "Empíricamente la UIP falla en horizontes cortos (el carry trade GANA en promedio: forward premium puzzle) — la prima ρ variable carga con la culpa.",
            "Ee no es observable: se estima, se ancla o se contagia (m74).",
            "Neutralidad al riesgo: aversión y fricciones de balance quedan en ρ como caja negra.",
        ],
        evolucion=("Con el corto plazo financiero (UIP) y el largo real (PPP), el "
                   "tipo de cambio queda tensado entre dos anclas. m49 mete esta "
                   "lógica en el modelo de política (movilidad perfecta ⇒ r=r*) y "
                   "m50 la convierte en el trilema. El episodio FED→Perú es m86 y "
                   "m111."),
    ),
    escenarios=[
        Escenario("defensa_con_tasa", "el BCRP sube la tasa de 5% a 7%",
                  {"i": 7.0},
                  "E se aprecia de 3.531 a 3.465 al instante: la defensa cambiaria "
                  "moderna no vende dólares — encarece los soles.",
                  cadena=["↑i local", "los depósitos en soles premian",
                          "entra capital de portafolio", "E↓ HOY (apreciación)",
                          "la depreciación esperada restante compensa el diferencial"]),
        Escenario("sube_la_fed", "la tasa externa pasa de 3% a 5.5%",
                  {"i_star": 5.5},
                  "el sol se deprecia a 3.617 sin que el Perú toque nada: el "
                  "endurecimiento global cobra su peaje cambiario — m111 con datos.",
                  cadena=["↑i* (FED)", "el dólar premia", "capital sale de emergentes",
                          "E↑ HOY", "el BCRP decide si responde con i (m38) o deja flotar"]),
        Escenario("panico_riesgo_pais", "ρ salta 3pp (ruido político)",
                  {"prima": 3.0},
                  "depreciación inmediata a 3.634 con tasas quietas: el miedo tiene "
                  "tipo de cambio propio.",
                  cadena=["incertidumbre local", "↑ρ", "el capital exige premio por quedarse",
                          "E↑ con i e i* constantes", "si contamina a Ee: espiral (m74)"]),
        Escenario("expectativa_devaluatoria", "el mercado espera Ee = 3.90",
                  {"Ee": 3.90},
                  "E salta HOY a 3.826: la expectativa se cobra por adelantado — la "
                  "semilla de las crisis autocumplidas de segunda generación (m74).",
                  cadena=["rumor de devaluación", "↑Ee", "la UIP trae el futuro al presente",
                          "E↑ hoy", "el fijo que no es creíble ya cayó (m74)"]),
    ],
    verificaciones=[
        Verificacion("arbitraje exacto: retornos igualados", _v_arbitraje),
        Verificacion("subir la tasa local aprecia HOY", _v_tasa_aprecia),
        Verificacion("la FED deprecia al sol HOY (m111)", _v_fed_deprecia),
        Verificacion("el riesgo país se cobra en el cambio", _v_riesgo_deprecia),
    ],
    notas="El cambio es un precio de activo: cotiza el futuro — y a veces lo fabrica (m74).",
)
