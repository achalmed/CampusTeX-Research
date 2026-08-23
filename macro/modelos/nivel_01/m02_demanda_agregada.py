# m02_demanda_agregada.py — PIB y componentes de la demanda agregada (nivel 1).
#
# Identidad del gasto:  Y = C + I + G + X − M
# Es CONTABILIDAD (ex post), no comportamiento: un cambio de un componente
# "mueve" Y uno a uno por definición, sin multiplicador ni expulsión — esa es
# exactamente la lección que separa este modelo de m04 y m10.
#
# Calibración base: proporciones que EVOCAN la estructura del gasto peruano
# (C≈65%, I≈22%, G≈13%, X≈25%, M≈25% del PIB). Aproximación didáctica, NO dato
# oficial — las series reales entran por el conector BCRP en el nivel 12.
#
# Procedencia: identidad de cuentas nacionales, conocimiento general
# (Kuznets 1934; SCN de Naciones Unidas). Calibración: decisión de diseño.

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _y(p):
    return p["C"] + p["I"] + p["G"] + p["X"] - p["M"]


def _curvas(p):
    Y = _y(p)
    cats = ["$C$", "$I$", "$G$", "$X$", "$-M$", "PIB"]
    vals = [p["C"], p["I"], p["G"], p["X"], -p["M"], Y]
    cols = [config.AZUL2] * 4 + [config.ROJO, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$Y = C+I+G+X-M = {Y:,.1f}$\n"
                          f"$XN = X - M = {p['X'] - p['M']:,.1f}$")}


def _resultados(p):
    Y = _y(p)
    return {"PIB (Y)": Y,
            "exportaciones netas XN": p["X"] - p["M"],
            "participación C/Y (%)": 100 * p["C"] / Y,
            "participación I/Y (%)": 100 * p["I"] / Y,
            "participación G/Y (%)": 100 * p["G"] / Y,
            "participación XN/Y (%)": 100 * (p["X"] - p["M"]) / Y}


_P0 = {"C": 650.0, "I": 220.0, "G": 130.0, "X": 250.0, "M": 250.0}


def _v_identidad():
    Y = _y(_P0)
    return abs(Y - (650 + 220 + 130 + 250 - 250)) < 1e-12, f"Y = {Y:,.1f} por identidad exacta"


def _v_participaciones():
    r = _resultados(_P0)
    suma = (r["participación C/Y (%)"] + r["participación I/Y (%)"]
            + r["participación G/Y (%)"] + r["participación XN/Y (%)"])
    return abs(suma - 100) < 1e-9, f"las participaciones suman {suma:.6f}%"


def _v_sin_multiplicador():
    dY = _y(dict(_P0, G=_P0["G"] + 50)) - _y(_P0)
    return abs(dY - 50) < 1e-12, ("ΔY = ΔG exactamente (uno a uno): en la identidad contable "
                                  "NO hay multiplicador — compárese con m04")


MODELO = Modelo(
    id="m02", nivel=1,
    nombre="PIB y componentes de la demanda agregada",
    xlabel="", ylabel="Unidades monetarias",
    parametros=[
        Parametro("C", _P0["C"], 0, 1200, 10, "Consumo privado C"),
        Parametro("I", _P0["I"], 0, 600, 10, "Inversión bruta I"),
        Parametro("G", _P0["G"], 0, 500, 10, "Gasto público G"),
        Parametro("X", _P0["X"], 0, 600, 10, "Exportaciones X"),
        Parametro("M", _P0["M"], 0, 600, 10, "Importaciones M"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Cómo se mide el producto de una economía — y qué NO dice esa "
                  "medición sobre las causas?"),
        contexto=("La Gran Depresión encontró a los gobiernos sin estadísticas agregadas: "
                  "no se sabía cuánto caía la producción. Simon Kuznets desarrolló las "
                  "primeras cuentas de ingreso nacional de EE.UU. (informe al Congreso, "
                  "1934) y Richard Stone lideró después el Sistema de Cuentas Nacionales "
                  "de la ONU. La identidad del gasto es el esqueleto contable sobre el que "
                  "Keynes montó su teoría de la demanda efectiva."),
        autores=("Kuznets (cuentas nacionales de EE.UU., años 30; Nobel 1971); Stone "
                 "(SCN; Nobel 1984); la lectura por el lado del gasto es keynesiana."),
        supuestos=[
            "Identidad ex post: mide lo efectivamente ocurrido en el período; se cumple SIEMPRE, por definición.",
            "Los componentes son independientes entre sí (nada explica C, I, G, X, M: son datos).",
            "Sin precios: se trabaja a precios constantes (la distinción nominal/real llega con el deflactor).",
        ],
        ecuaciones=[
            Ecuacion("Y = C + I + G + X - M", "identidad del gasto",
                     "todo lo producido (Y) fue comprado por alguien: hogares (C), empresas (I, "
                     "incluida la variación de existencias), gobierno (G) o el exterior (X); se "
                     "restan las importaciones M porque C, I y G las incluyen y no son producción interna."),
            Ecuacion("XN = X - M", "exportaciones netas",
                     "la contribución neta del sector externo a la demanda de producción nacional."),
        ],
        intuicion=("La identidad no explica NADA: registra. Su poder es disciplinar el "
                   "análisis — cualquier historia sobre el PIB debe cuadrar con ella. La "
                   "trampa clásica es leerla como causalidad ('si sube G, sube Y uno a "
                   "uno'): eso solo es contabilidad del período; qué pasa con Y cuando el "
                   "gobierno DECIDE gastar más exige un modelo de comportamiento "
                   "(multiplicador m04, expulsión m11)."),
        equilibrio=("No hay equilibrio que encontrar: la identidad se cumple siempre "
                    "(la variación de existencias dentro de I es la partida de ajuste)."),
        limitaciones=[
            "No es un modelo causal: no puede simular políticas, solo descomponer lo ocurrido.",
            "PIB ≠ bienestar: omite trabajo no remunerado, economía informal (crítico en Perú), distribución y medio ambiente.",
            "La calibración base es didáctica; el análisis serio exige las series oficiales (BCRP/INEI).",
        ],
        evolucion=("El paso decisivo es darle comportamiento a los componentes: m03 hace "
                   "C = f(Yd) (Keynes) y con ello m04 genera el multiplicador; m06-m10 "
                   "añaden I(r) y el dinero; el nivel 12 reemplaza esta calibración por "
                   "las cuentas nacionales reales del BCRP vía datafw."),
        procedencia=("identidad de cuentas nacionales — conocimiento general (Kuznets 1934, "
                     "SCN); calibración de proporciones: decisión de diseño didáctica, NO dato oficial"),
        referencias=["Kuznets, National Income 1929-1932 (1934) — mención histórica, no verificado",
                     "Sistema de Cuentas Nacionales (ONU) — marco vigente de medición"],
    ),
    escenarios=[
        Escenario("shock_consumo", "el consumo cae 10% (crisis de confianza)",
                  {"C": 585.0},
                  "contablemente el PIB cae exactamente en ΔC; en un modelo con "
                  "comportamiento (m04) la caída sería MAYOR por las rondas de gasto.",
                  cadena=["↓C", "ΔY = ΔC (identidad ex post)", "sin rondas ni multiplicador",
                          "solo contabilidad — el comportamiento llega en m03-m04"]),
        Escenario("impulso_fiscal", "el gasto público sube 20%",
                  {"G": 156.0},
                  "ΔY = ΔG = 26, uno a uno: la identidad no multiplica ni expulsa; "
                  "comparar con m04 (multiplicador) y m11 (expulsión).",
                  cadena=["↑G", "ΔY = ΔG uno a uno", "la identidad no multiplica ni expulsa"]),
        Escenario("shock_exportador", "las exportaciones caen 20% (menor demanda externa)",
                  {"X": 200.0},
                  "sensibilidad de una economía abierta a sus mercados de destino; para "
                  "Perú el canal real pasa por los términos de intercambio (nivel 12).",
                  cadena=["↓X", "↓XN", "ΔY = ΔX contable", "los canales reales llegan en niveles 2-3"]),
    ],
    verificaciones=[
        Verificacion("identidad exacta Y = C+I+G+X−M", _v_identidad),
        Verificacion("participaciones suman 100%", _v_participaciones),
        Verificacion("sin comportamiento no hay multiplicador (ΔY=ΔG)", _v_sin_multiplicador),
    ],
    notas="Identidad contable, no modelo causal: la diferencia identidad/comportamiento es la lección del nivel 1.",
)
