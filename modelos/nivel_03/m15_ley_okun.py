# m15_ley_okun.py — ley de Okun: crecimiento y desempleo (nivel 3).
#
#   Δu = −β (g − g*)     β: coeficiente de Okun; g*: crecimiento "de equilibrio"
# Regla EMPÍRICA (no ley estructural): traduce crecimiento en empleo. Cierra el
# triángulo del nivel 3: demanda → producto (niveles 1-2), producto → desempleo
# (Okun), desempleo → inflación (Phillips).
#
# Procedencia: Okun (1962, "Potential GNP", mención histórica); coeficiente y
# g* de la calibración: decisión de diseño didáctica — el β peruano se estimará
# con datos reales (ENAHO/BCRP) en el nivel 12.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _du(g, p):
    return -p["beta"] * (g - p["g_pot"])


def _curvas(p):
    g = np.linspace(-4, 8, 200)
    du = _du(g, p)
    return {"lineas": {"$\\Delta u = -\\beta\\,(g - g^*)$": (g, du, config.AZUL2),
                       "$\\Delta u = 0$": (g, np.zeros_like(g), config.GRIS)},
            "puntos": [(p["g_pot"], 0.0, f"$g^* = {p['g_pot']:.1f}\\%$"),
                       (p["g_actual"], _du(p["g_actual"], p), "situación elegida")],
            "anotacion": (f"con $g = {p['g_actual']:.1f}\\%$: $\\Delta u = "
                          f"{_du(p['g_actual'], p):+.2f}$ pp/año\n"
                          f"$u$ pasaría de ${p['u0']:.1f}\\%$ a "
                          f"${p['u0'] + p['anios'] * _du(p['g_actual'], p):.1f}\\%$ "
                          f"en {p['anios']:.0f} años")}


def _resultados(p):
    du = _du(p["g_actual"], p)
    return {"Δu por año (pp)": du,
            "u inicial (%)": p["u0"],
            f"u tras {p['anios']:.0f} años (%)": p["u0"] + p["anios"] * du,
            "g que mantiene u constante (%)": p["g_pot"],
            "g para bajar u 1 pp/año (%)": p["g_pot"] + 1 / p["beta"]}


_P0 = {"beta": 0.4, "g_pot": 3.5, "g_actual": 1.0, "u0": 6.0, "anios": 5.0}


def _v_neutral():
    return abs(_du(_P0["g_pot"], _P0)) < 1e-12, "crecer exactamente a g* deja el desempleo quieto"


def _v_pendiente():
    pend = (_du(5.0, _P0) - _du(3.0, _P0)) / 2.0
    return abs(pend + _P0["beta"]) < 1e-12, f"pendiente = −β = {pend:.2f}"


def _v_proyeccion():
    r = _resultados(_P0)
    a_mano = _P0["u0"] + _P0["anios"] * (-_P0["beta"] * (_P0["g_actual"] - _P0["g_pot"]))
    return abs(r[f"u tras {_P0['anios']:.0f} años (%)"] - a_mano) < 1e-12, \
        f"proyección lineal exacta: u llega a {a_mano:.1f}%"


MODELO = Modelo(
    id="m15", nivel=3,
    nombre="Ley de Okun",
    xlabel="Crecimiento del PIB $g$ (%)", ylabel="Variación del desempleo $\\Delta u$ (pp/año)",
    parametros=[
        Parametro("g_actual", _P0["g_actual"], -4.0, 8.0, 0.5, "Crecimiento efectivo g"),
        Parametro("beta", _P0["beta"], 0.1, 1.0, 0.05, "Coeficiente de Okun β"),
        Parametro("g_pot", _P0["g_pot"], 1.0, 6.0, 0.25, "Crecimiento que estabiliza u (g*)"),
        Parametro("u0", _P0["u0"], 3.0, 12.0, 0.5, "Desempleo inicial u0"),
        Parametro("anios", _P0["anios"], 1, 10, 1, "Años proyectados"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Cuánto crecimiento hace falta para bajar el desempleo en un punto?",
        contexto=("Arthur Okun (1962), asesor de Kennedy, necesitaba responder una "
                  "pregunta política: ¿cuánto crecimiento hace falta para bajar el "
                  "desempleo? Su regla empírica — cada punto de crecimiento por encima "
                  "del potencial recorta el desempleo en una fracción β — se volvió el "
                  "puente estándar entre las cuentas nacionales y el mercado de trabajo."),
        autores=("Okun (1962, 'Potential GNP: Its Measurement and Significance', "
                 "mención). Es una REGULARIDAD EMPÍRICA, no un modelo estructural: "
                 "cada país y cada época tienen su β."),
        supuestos=[
            "Relación lineal y estable entre crecimiento y Δu en el horizonte analizado.",
            "g* constante: crecer a g* absorbe justo la nueva fuerza laboral y la productividad tendencial.",
            "El empleo se ajusta vía DESEMPLEO ABIERTO — el supuesto más frágil para el Perú (ver limitaciones).",
        ],
        ecuaciones=[
            Ecuacion("\\Delta u = -\\beta\\,(g - g^*)", "ley de Okun (versión en diferencias)",
                     "β < 1 porque el empleo amortigua: ante más demanda las empresas primero "
                     "intensifican horas y productividad, y la participación laboral también responde."),
        ],
        intuicion=("Crecer no basta: hay que crecer MÁS que g*, porque la población "
                   "activa y la productividad ya absorben ese ritmo. La asimetría "
                   "práctica es dolorosa: con β=0.4, un año de recesión de −2% sube el "
                   "desempleo 2.2 pp, y recuperarlos exige varios años creciendo fuerte."),
        equilibrio=("No es un modelo de equilibrio sino una regla de traducción: su "
                    "'punto fijo' es g = g*, donde u se estabiliza en el nivel que "
                    "tenga (la TASA de desempleo estable la determina m14, no Okun)."),
        limitaciones=[
            "β es inestable: varía por país, época y régimen laboral (en EE.UU. ~0.4-0.5; en economías informales, mucho menor).",
            "ADVERTENCIA PERUANA: con alta informalidad el ajuste va por subempleo, informalidad y horas — el desempleo abierto se mueve poco; el β peruano con u abierta es bajo y la lectura debe complementarse con calidad del empleo (ENAHO, nivel 12).",
            "No es causal ni invertible: subir u no 'genera' crecimiento, y estimular g sin oferta acaba en inflación (m18).",
            "g* no es observable y se mueve (demografía, productividad): mismo problema que la brecha (m16).",
        ],
        evolucion=("Cierra el triángulo demanda-producto-empleo-inflación del nivel 3: "
                   "con Okun y Phillips, un shock de demanda (m18) ya se puede leer en "
                   "las tres variables. La versión con datos peruanos (β estimado con "
                   "ENAHO + PBI del BCRP) es parte del nivel 12 (m112)."),
        procedencia=("regla empírica de Okun (1962, mención) — conocimiento general; "
                     "calibración β=0.4, g*=3.5: decisión de diseño didáctica, NO estimación peruana"),
    ),
    escenarios=[
        Escenario("recesion", "la economía cae 2% un año",
                  {"g_actual": -2.0},
                  "Δu = +2.2 pp en un solo año: las recesiones destruyen empleo mucho "
                  "más rápido de lo que las expansiones lo reconstruyen."),
        Escenario("auge", "crecimiento de 6% sostenido",
                  {"g_actual": 6.0},
                  "Δu = −1 pp/año: incluso un boom tarda años en deshacer una recesión — "
                  "la aritmética de la recuperación es lenta."),
        Escenario("empleo_rigido", "economía informal: β = 0.15",
                  {"beta": 0.15},
                  "el desempleo abierto casi no responde al ciclo: la foto peruana — el "
                  "ajuste real está en la informalidad y el subempleo, no en u."),
    ],
    verificaciones=[
        Verificacion("crecer a g* deja u constante", _v_neutral),
        Verificacion("pendiente = −β", _v_pendiente),
        Verificacion("proyección lineal de u exacta", _v_proyeccion),
    ],
    notas="Puente producto↔empleo del nivel 3; el β peruano exige ENAHO (m112, nivel 12).",
)
