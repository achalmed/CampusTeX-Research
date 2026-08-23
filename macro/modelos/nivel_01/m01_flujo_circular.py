# m01_flujo_circular.py — flujo circular de la renta (nivel 1).
#
# Hogares ↔ empresas ↔ gobierno ↔ sector externo. Filtraciones (S, T, M) e
# inyecciones (I, G, X) sobre proporciones fijas del ingreso:
#   T = t·Y ;  Yd = (1−t)·Y ;  C = c·Yd ;  S = (1−c)·Yd ;  M = m·Y
# Equilibrio del circuito:  S + T + M = I + G + X
#   → Y* = (I + G + X) / [(1−c)(1−t) + t + m]
#
# Procedencia: conocimiento macroeconómico general (esquema de manuales
# introductorios); antecedente histórico del circuito: Quesnay (1758).

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _flujos(p):
    c, t, m = p["c"], p["t"], p["m"]
    denom = (1 - c) * (1 - t) + t + m
    Y = (p["I"] + p["G"] + p["X"]) / denom
    Yd = (1 - t) * Y
    return {"Y": Y, "Yd": Yd, "C": c * Yd, "S": (1 - c) * Yd,
            "T": t * Y, "M": m * Y, "k": 1 / denom}


def _curvas(p):
    f = _flujos(p)
    cats = ["$S$", "$T$", "$M$", "$I$", "$G$", "$X$"]
    vals = [f["S"], f["T"], f["M"], p["I"], p["G"], p["X"]]
    cols = [config.ROJO] * 3 + [config.VERDE] * 3
    filt = f["S"] + f["T"] + f["M"]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$Y^* = {f['Y']:,.1f}$\n"
                          f"filtraciones $S{{+}}T{{+}}M$ = {filt:,.1f}\n"
                          f"inyecciones $I{{+}}G{{+}}X$ = {p['I'] + p['G'] + p['X']:,.1f}")}


def _resultados(p):
    f = _flujos(p)
    return {"Y* (producto de equilibrio)": f["Y"],
            "Yd (renta disponible)": f["Yd"],
            "C (consumo)": f["C"], "S (ahorro)": f["S"],
            "T (impuestos netos)": f["T"], "M (importaciones)": f["M"],
            "filtraciones S+T+M": f["S"] + f["T"] + f["M"],
            "inyecciones I+G+X": p["I"] + p["G"] + p["X"],
            "multiplicador del circuito": f["k"]}


_P0 = {"I": 200.0, "G": 150.0, "X": 250.0, "c": 0.8, "t": 0.15, "m": 0.20}


def _v_circuito():
    f = _flujos(_P0)
    dif = abs((f["S"] + f["T"] + f["M"]) - (_P0["I"] + _P0["G"] + _P0["X"]))
    return dif < 1e-9, f"en Y* las filtraciones igualan a las inyecciones (dif={dif:.1e})"


def _v_contabilidad():
    f = _flujos(_P0)
    ok = abs(f["C"] + f["S"] - f["Yd"]) < 1e-9 and abs(f["Yd"] + f["T"] - f["Y"]) < 1e-9
    return ok, "C+S=Yd y Yd+T=Y (identidades exactas)"


def _v_linealidad():
    y0, k = _flujos(_P0)["Y"], _flujos(_P0)["k"]
    y1 = _flujos(dict(_P0, I=_P0["I"] + 1))["Y"]
    return abs((y1 - y0) - k) < 1e-9, f"ΔY ante ΔI=1 es exactamente el multiplicador ({k:.3f})"


def _v_frugalidad():
    y0 = _flujos(_P0)["Y"]
    y1 = _flujos(dict(_P0, c=0.7))["Y"]
    return y1 < y0, f"más ahorro deseado (c 0.8→0.7) reduce Y* ({y0:,.1f}→{y1:,.1f}): anticipa m05"


MODELO = Modelo(
    id="m01", nivel=1,
    nombre="Flujo circular de la renta",
    xlabel="", ylabel="Flujo (unidades monetarias)",
    parametros=[
        Parametro("I", _P0["I"], 0, 500, 10, "Inversión I (inyección)"),
        Parametro("G", _P0["G"], 0, 500, 10, "Gasto público G (inyección)"),
        Parametro("X", _P0["X"], 0, 600, 10, "Exportaciones X (inyección)"),
        Parametro("c", _P0["c"], 0.1, 0.95, 0.05, "Propensión a consumir c"),
        Parametro("t", _P0["t"], 0.0, 0.5, 0.05, "Tasa impositiva neta t"),
        Parametro("m", _P0["m"], 0.0, 0.5, 0.05, "Propensión a importar m"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Por qué el gasto de unos es el ingreso de otros, y qué nivel de "
                  "ingreso puede sostener el circuito?"),
        contexto=("Es la imagen fundacional de la macroeconomía: el gasto de un agente "
                  "es el ingreso de otro. El antecedente clásico es el Tableau économique "
                  "de François Quesnay (1758), que representó la economía como circulación "
                  "de flujos entre clases sociales; la versión moderna con hogares, "
                  "empresas, gobierno y sector externo se consolidó en el siglo XX junto "
                  "con la contabilidad nacional, como esquema organizador de los manuales."),
        autores=("Quesnay y los fisiócratas (1758) como precursores; formalización "
                 "contable en la tradición keynesiana y de cuentas nacionales (s. XX)."),
        supuestos=[
            "Proporciones fijas: consumo, impuestos e importaciones son fracciones constantes del ingreso.",
            "Inyecciones exógenas: I, G y X no dependen de Y (no hay tasa de interés ni tipo de cambio).",
            "Sin precios ni dinero explícito: todo se mide en flujos reales por período.",
            "Economía en reposo: se analiza el estado en que el circuito se repite período a período.",
        ],
        ecuaciones=[
            Ecuacion("T = t \\, Y \\;;\\; Y_d = (1-t)\\,Y", "recaudación y renta disponible",
                     "el gobierno retiene la fracción t del ingreso; los hogares disponen del resto."),
            Ecuacion("C = c\\,Y_d \\;;\\; S = (1-c)\\,Y_d", "uso de la renta disponible",
                     "los hogares reparten Yd entre consumo (proporción c) y ahorro (el resto): C+S=Yd por construcción."),
            Ecuacion("M = m\\,Y", "importaciones",
                     "parte del gasto se filtra al exterior en proporción m del ingreso."),
            Ecuacion("S + T + M = I + G + X", "equilibrio del circuito",
                     "el flujo se sostiene si lo que sale del circuito (filtraciones) reingresa como inversión, gasto público y exportaciones."),
            Ecuacion("Y^* = \\frac{I+G+X}{(1-c)(1-t) + t + m}", "producto de equilibrio",
                     "despeje de la condición anterior; el denominador es la fracción de cada unidad de ingreso que se filtra."),
        ],
        intuicion=("Cada unidad monetaria gastada vuelve como ingreso y se vuelve a gastar, "
                   "menos la parte que se ahorra, se paga en impuestos o se va en importaciones. "
                   "El circuito solo se sostiene en el nivel Y* donde esas salidas son "
                   "exactamente compensadas por las entradas autónomas (I, G, X). Si las "
                   "filtraciones exceden a las inyecciones, el flujo se contrae; si son "
                   "menores, se expande: por eso el equilibrio es estable."),
        equilibrio=("Y* iguala filtraciones e inyecciones. Estabilidad: para Y > Y* las "
                    "filtraciones superan a las inyecciones y el flujo cae (y viceversa), "
                    "de modo que el circuito converge a Y*."),
        limitaciones=[
            "Es un esquema contable con proporciones fijas, no una teoría del comportamiento.",
            "I, G y X caen del cielo: no hay tasa de interés, expectativas ni tipo de cambio que los expliquen.",
            "Sin precios: no puede hablar de inflación ni distinguir flujos nominales de reales.",
            "Estático: describe la repetición del circuito, no su dinámica de ajuste período a período.",
        ],
        evolucion=("m02 mide este flujo con la identidad del PIB (Y = C+I+G+XN); m03 "
                   "reemplaza la proporción fija c por una función de consumo con "
                   "comportamiento (Keynes); m04 muestra que las inyecciones se "
                   "multiplican; y m05 explota la primera paradoja del circuito: "
                   "querer ahorrar más puede reducir el ingreso sin aumentar el ahorro."),
        referencias=["Quesnay, Tableau économique (1758) — antecedente histórico (mención, no verificado)",
                     "Esquema estándar de manuales introductorios de macroeconomía"],
    ),
    escenarios=[
        Escenario("mayor_inversion", "las empresas elevan la inversión de 200 a 300",
                  {"I": 300.0},
                  "una inyección adicional expande TODO el circuito: Y* sube más que la "
                  "propia ΔI (multiplicador), y con él suben C, S, T y M.",
                  cadena=["↑I", "↑ inyecciones", "el circuito se expande", "↑Y*",
                          "↑S, ↑T, ↑M hasta reequilibrar filtraciones e inyecciones"]),
        Escenario("apertura_importadora", "la propensión a importar sube de 0.20 a 0.30",
                  {"m": 0.30},
                  "una filtración mayor drena el circuito: el mismo nivel de inyecciones "
                  "sostiene un Y* menor.",
                  cadena=["↑m", "mayor filtración externa", "↓ re-gasto interno",
                          "↓Y*", "el circuito reequilibra más abajo"]),
        Escenario("mas_frugalidad", "los hogares consumen menos de su renta (c: 0.8→0.7)",
                  {"c": 0.70},
                  "el intento colectivo de ahorrar más encoge el circuito — anticipo de la "
                  "paradoja del ahorro (m05).",
                  cadena=["↓c", "↑ filtración por ahorro", "↓ re-gasto", "↓Y*",
                          "anticipo de la paradoja (m05)"]),
    ],
    verificaciones=[
        Verificacion("filtraciones = inyecciones en Y*", _v_circuito),
        Verificacion("identidades contables C+S=Yd, Yd+T=Y", _v_contabilidad),
        Verificacion("linealidad: ΔY/ΔI = multiplicador", _v_linealidad),
        Verificacion("mayor frugalidad contrae el circuito", _v_frugalidad),
    ],
    notas="Barras rojas: filtraciones evaluadas en Y*. Barras verdes: inyecciones exógenas.",
)
