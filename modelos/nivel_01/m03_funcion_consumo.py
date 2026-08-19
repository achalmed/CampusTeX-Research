# m03_funcion_consumo.py — función de consumo keynesiana (nivel 1).
#
#   C = C0 + c·Yd     con 0 < c < 1  ("ley psicológica fundamental")
#   S = Yd − C = −C0 + (1−c)·Yd
# Punto de nivelación (C = Yd, S = 0):  Yd_niv = C0 / (1−c)
#
# Procedencia: Keynes, Teoría General (1936), cap. sobre la propensión a
# consumir — conocimiento macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _curvas(p):
    C0, c = p["C0"], p["c"]
    tope = p["Yd_max"]
    Yd = np.linspace(0, tope, 300)
    C = C0 + c * Yd
    S = Yd - C
    niv = C0 / (1 - c)
    return {"lineas": {"$C = C_0 + c\\,Y_d$": (Yd, C, config.AZUL2),
                       "recta de 45° ($C = Y_d$)": (Yd, Yd, config.GRIS),
                       "$S = Y_d - C$": (Yd, S, config.ROJO)},
            "equilibrio": (niv, niv),
            "puntos": [(niv, 0.0, "$S = 0$")],
            "anotacion": (f"nivelación: $Y_d = C_0/(1-c) = {niv:,.1f}$\n"
                          f"$PMC = {c:.2f}$,  $PMS = {1 - c:.2f}$")}


def _resultados(p):
    C0, c = p["C0"], p["c"]
    niv = C0 / (1 - c)
    yd = 0.8 * p["Yd_max"]                      # punto de evaluación ilustrativo
    C = C0 + c * yd
    return {"PMC (propensión marginal a consumir)": c,
            "PMS (propensión marginal a ahorrar)": 1 - c,
            "Yd de nivelación (S=0)": niv,
            f"C en Yd={yd:,.0f}": C,
            f"S en Yd={yd:,.0f}": yd - C,
            f"PMeC en Yd={yd:,.0f}": C / yd}


def _ecuaciones_calibradas(p):
    niv = p["C0"] / (1 - p["c"])
    return [f"$C = {p['C0']:.0f} + {p['c']:.2f}\\,Y_d$",
            f"$S = -{p['C0']:.0f} + {1 - p['c']:.2f}\\,Y_d$",
            f"$Y_d^{{niv}} = {p['C0']:.0f}/(1-{p['c']:.2f}) = {niv:,.1f}$"]


_P0 = {"C0": 100.0, "c": 0.8, "Yd_max": 1000.0}


def _v_pendiente():
    f = lambda yd: _P0["C0"] + _P0["c"] * yd
    pend = (f(600.0) - f(400.0)) / 200.0
    return abs(pend - _P0["c"]) < 1e-12, f"pendiente numérica = PMC = {pend:.4f}"


def _v_ordenada():
    return abs((_P0["C0"] + _P0["c"] * 0) - _P0["C0"]) < 1e-12, "C(0) = C0 (consumo autónomo)"


def _v_identidad():
    Yd = np.linspace(0, 1000, 101)
    C = _P0["C0"] + _P0["c"] * Yd
    S = Yd - C
    return bool(np.all(np.abs(C + S - Yd) < 1e-9)), "C + S = Yd en toda la malla (identidad)"


def _v_pmec_decreciente():
    Yd = np.linspace(100, 1000, 50)
    pmec = (_P0["C0"] + _P0["c"] * Yd) / Yd
    return bool(np.all(np.diff(pmec) < 0)), ("la propensión MEDIA decrece con Yd (C0>0): "
                                             "predicción clave, luego cuestionada por Kuznets")


def _v_nivelacion():
    niv = _P0["C0"] / (1 - _P0["c"])
    C = _P0["C0"] + _P0["c"] * niv
    return abs(C - niv) < 1e-9, f"en Yd={niv:,.1f} el consumo iguala a la renta (S=0)"


MODELO = Modelo(
    id="m03", nivel=1,
    nombre="Función de consumo keynesiana",
    xlabel="Renta disponible ($Y_d$)", ylabel="Consumo / Ahorro",
    parametros=[
        Parametro("C0", _P0["C0"], 0, 300, 10, "Consumo autónomo C0"),
        Parametro("c", _P0["c"], 0.1, 0.95, 0.05, "Propensión marginal a consumir c"),
        Parametro("Yd_max", _P0["Yd_max"], 400, 3000, 100, "Rango de renta graficado"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta=("¿De qué depende el consumo de los hogares y cuánto se re-gasta de "
                  "cada sol adicional de ingreso?"),
        variables=[("Yd", "renta disponible — exógena en este modelo"),
                   ("C", "consumo — endógena"),
                   ("S", "ahorro — endógena (el residuo Yd − C)"),
                   ("C0, c", "conducta de los hogares — parámetros")],
        derivacion=["C = C_0 + c\\,Y_d",
                    "S = Y_d - C = -C_0 + (1-c)\\,Y_d",
                    "C = Y_d \\;\\Rightarrow\\; Y_d^{niv} = \\frac{C_0}{1-c}"],
        contexto=("En plena Gran Depresión, Keynes necesitaba explicar por qué la demanda "
                  "podía quedarse sistemáticamente corta. La pieza central fue una teoría "
                  "del consumo: los hogares gastan una parte estable de cada unidad "
                  "adicional de ingreso ('ley psicológica fundamental'). De esa "
                  "regularidad nacen el multiplicador y la posibilidad de equilibrios "
                  "con desempleo."),
        autores=("Keynes, Teoría General de la Ocupación, el Interés y el Dinero (1936). "
                 "Críticas y reformulaciones: Kuznets (evidencia de series largas), "
                 "Duesenberry (ingreso relativo, 1949), Modigliani-Brumberg (ciclo de "
                 "vida, años 50), Friedman (ingreso permanente, 1957)."),
        supuestos=[
            "El consumo corriente depende del ingreso disponible CORRIENTE (no de la riqueza ni del ingreso futuro esperado).",
            "0 < c < 1: cada unidad adicional de ingreso aumenta el consumo, pero menos que uno a uno.",
            "C0 > 0: existe consumo de subsistencia aun con ingreso nulo (desahorro).",
            "Parámetros estables en el corto plazo (la 'ley psicológica' no cambia con el ciclo).",
        ],
        ecuaciones=[
            Ecuacion("C = C_0 + c\\,Y_d", "función de consumo",
                     "C0 es el consumo autónomo (independiente del ingreso); c es la propensión "
                     "marginal a consumir: cuántos céntimos de cada unidad adicional de Yd se gastan."),
            Ecuacion("S = Y_d - C = -C_0 + (1-c)\\,Y_d", "función de ahorro",
                     "el ahorro es el espejo del consumo: con ingresos bajos es negativo "
                     "(se desahorra para subsistir) y crece con pendiente 1−c (PMS)."),
            Ecuacion("Y_d^{niv} = \\frac{C_0}{1-c}", "punto de nivelación",
                     "renta a la cual C = Yd: por debajo los hogares desahorran, por encima ahorran."),
            Ecuacion("PMeC = \\frac{C}{Y_d} = \\frac{C_0}{Y_d} + c", "propensión media",
                     "con C0 > 0 la PMeC cae al crecer Yd: los hogares ricos consumirían una "
                     "fracción menor de su renta — la predicción que Kuznets pondría en aprietos."),
        ],
        intuicion=("La pendiente c gobierna toda la macro keynesiana de corto plazo: si "
                   "los hogares re-gastan 80 céntimos de cada sol adicional, cualquier "
                   "inyección de gasto se propaga en cadena (m04). La distinción "
                   "marginal/media importa: la marginal es la pendiente; la media, la "
                   "posición relativa de la recta respecto al origen."),
        equilibrio=("No es un modelo de equilibrio del producto (eso llega en m05/m06): "
                    "describe una conducta. Su 'punto notable' es la nivelación S=0."),
        limitaciones=[
            "Kuznets (series largas de EE.UU.) encontró PMeC aproximadamente ESTABLE a largo plazo, no decreciente: la función simple no reconcilia corto y largo plazo.",
            "Ignora riqueza, crédito y expectativas: dos hogares con igual Yd y distinta riqueza consumen igual aquí.",
            "Friedman (ingreso permanente) y Modigliani (ciclo de vida) mostraron que el consumo responde al ingreso PERMANENTE: los shocks transitorios se suavizan.",
            "Agregación: 'el hogar representativo' esconde la distribución del ingreso (la PMC de pobres y ricos difiere).",
        ],
        evolucion=("Con la PMC en mano, m04 construye el multiplicador y m05 la paradoja "
                   "del ahorro. Las críticas empíricas (Kuznets) y teóricas (Friedman, "
                   "Modigliani, Lucas) empujan hacia los modelos intertemporales con "
                   "expectativas del nivel 8 — la función simple sobrevive como "
                   "aproximación de corto plazo y por la existencia de hogares 'mano a boca'."),
        referencias=["Keynes (1936), Teoría General — mención, no verificado contra edición",
                     "Friedman (1957), A Theory of the Consumption Function — mención histórica"],
    ),
    escenarios=[
        Escenario("optimismo_autonomo", "el consumo autónomo sube de 100 a 150",
                  {"C0": 150.0},
                  "la recta se desplaza en paralelo hacia arriba: se consume más a "
                  "CUALQUIER nivel de renta y la nivelación se aleja (750).",
                  cadena=["↑C0", "la recta de consumo sube en paralelo",
                          "más consumo a toda renta", "nivelación S=0 más lejos"]),
        Escenario("prudencia", "la PMC cae de 0.80 a 0.70",
                  {"c": 0.70},
                  "la recta gira: menos pendiente, nivelación más cercana (333) — y en "
                  "m04 significará un multiplicador mucho menor (5 → 3.3).",
                  cadena=["↓c", "la recta gira (menos pendiente)", "↓ re-gasto marginal",
                          "nivelación más cerca", "en m04: ↓k"]),
    ],
    verificaciones=[
        Verificacion("pendiente numérica = PMC", _v_pendiente),
        Verificacion("C(0) = C0", _v_ordenada),
        Verificacion("identidad C + S = Yd", _v_identidad),
        Verificacion("PMeC decreciente en Yd", _v_pmec_decreciente),
        Verificacion("nivelación: C(Yd_niv) = Yd_niv", _v_nivelacion),
    ],
    notas="La PMC (c) es el parámetro más importante del nivel 1: gobierna multiplicador y paradoja.",
)
