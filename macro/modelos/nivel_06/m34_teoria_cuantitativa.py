# m34_teoria_cuantitativa.py — teoría cuantitativa del dinero (nivel 6).
#
#   M·V = P·Y   (ecuación de cambio, Fisher)
# Con V estable e Y de pleno empleo: P = (V/Y)·M — los precios son
# proporcionales al dinero. En tasas de crecimiento (exacto):
#   1+π = (1+g_M)(1+g_V)/(1+g_Y)   ≈   π ≈ g_M + g_V − g_Y
#
# Procedencia: Fisher (1911, The Purchasing Power of Money — mención);
# antecedentes: Bodin, Hume (menciones); lectura moderna: Friedman
# ("la inflación es siempre y en todas partes un fenómeno monetario",
# mención) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _p(p):
    return p["M"] * p["V"] / p["Y"]


def _pi_exacta(p):
    return (1 + p["gM"] / 100) * (1 + p["gV"] / 100) / (1 + p["gY"] / 100) - 1


def _curvas(p):
    M = np.linspace(0, 1200, 200)
    return {"lineas": {"$P = (V/Y)\\,M$": (M, p["V"] / p["Y"] * M, config.AZUL2)},
            "equilibrio": (p["M"], _p(p)),
            "anotacion": (f"$P = {p['M']:.0f} \\times {p['V']:.1f} / {p['Y']:.0f} = {_p(p):.2f}$\n"
                          f"$\\pi = {100 * _pi_exacta(p):.2f}\\%$  "
                          f"(≈ $g_M + g_V - g_Y = {p['gM'] + p['gV'] - p['gY']:.1f}\\%$)")}


def _resultados(p):
    return {"nivel de precios P": _p(p),
            "π exacta de los crecimientos (%)": 100 * _pi_exacta(p),
            "π aproximada gM+gV−gY (%)": p["gM"] + p["gV"] - p["gY"],
            "saldos reales M/P": p["M"] / _p(p),
            "velocidad V (dada)": p["V"]}


def _ecuaciones_calibradas(p):
    return [f"${p['M']:.0f} \\times {p['V']:.1f} = {_p(p):.2f} \\times {p['Y']:.0f}$",
            f"$\\pi = \\frac{{(1+{p['gM'] / 100:.2f})(1+{p['gV'] / 100:.2f})}}{{1+{p['gY'] / 100:.2f}}} - 1 "
            f"= {100 * _pi_exacta(p):.2f}\\%$"]


_P0 = {"M": 500.0, "V": 2.0, "Y": 1000.0, "gM": 8.0, "gV": 0.0, "gY": 3.0}


def _v_identidad():
    P = _p(_P0)
    return abs(_P0["M"] * _P0["V"] - P * _P0["Y"]) < 1e-9, \
        f"MV = PY se cumple exacto (P = {P:.3f}): es una identidad, el contenido está en los supuestos"


def _v_proporcionalidad():
    P1, P2 = _p(_P0), _p(dict(_P0, M=2 * _P0["M"]))
    return abs(P2 / P1 - 2.0) < 1e-12, ("duplicar M duplica P exactamente (V, Y fijos): "
                                        "la neutralidad cuantitativa en su forma más pura")


def _v_aproximacion():
    exacta = 100 * _pi_exacta(_P0)
    aprox = _P0["gM"] + _P0["gV"] - _P0["gY"]
    return abs(exacta - aprox) < 0.5, (f"la aproximación gM+gV−gY ({aprox:.1f}%) difiere de la exacta "
                                       f"({exacta:.2f}%) en menos de 0.5 pp con tasas moderadas")


def _v_real_intacto():
    r1 = _resultados(_P0)["saldos reales M/P"]
    r2 = _resultados(dict(_P0, M=3 * _P0["M"]))["saldos reales M/P"]
    return abs(r1 - r2) < 1e-9, ("triplicar M deja M/P intacto: lo nominal escala, "
                                 "lo real no — el ancla de m22, ahora con V explícita")


MODELO = Modelo(
    id="m34", nivel=6,
    nombre="Teoría cuantitativa del dinero",
    xlabel="Dinero ($M$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("M", _P0["M"], 100, 1200, 25, "Cantidad de dinero M", grupo="nominal",
                  definicion="lo único que el banco central controla aquí"),
        Parametro("gM", _P0["gM"], 0, 60, 1, "Crecimiento del dinero gM (%)", grupo="crecimientos"),
        Parametro("gY", _P0["gY"], 0, 8, 0.5, "Crecimiento real gY (%)", grupo="crecimientos"),
        Parametro("gV", _P0["gV"], -5, 10, 0.5, "Cambio de velocidad gV (%)", grupo="crecimientos"),
        Parametro("V", _P0["V"], 0.5, 5, 0.1, "Velocidad de circulación V", grupo="estructura",
                  definicion="veces que cada sol cambia de manos por período"),
        Parametro("Y", _P0["Y"], 400, 2000, 50, "Producto real Y (pleno empleo)", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué imprimir dinero termina en inflación — y cuándo esa relación uno a uno se rompe?",
        variables=[("P", "nivel de precios — endógena (el dinero la determina)"),
                   ("M", "cantidad de dinero — exógena (el banco central)"),
                   ("V", "velocidad — SUPUESTA estable (el talón de Aquiles)"),
                   ("Y", "producto real — anclado en pleno empleo (m22)")],
        derivacion=["M\\,V = P\\,Y \\;\\;(identidad\\;de\\;cambio)",
                    "V, Y \\;dados \\;\\Rightarrow\\; P = \\frac{V}{Y}\\,M",
                    "en\\;tasas: \\; (1+\\pi) = \\frac{(1+g_M)(1+g_V)}{1+g_Y}"],
        contexto=("La teoría macroeconómica más antigua en uso: Bodin y Hume ya "
                  "conectaban el oro americano con los precios europeos en los siglos "
                  "XVI-XVIII. Fisher (1911) le dio su forma canónica MV=PY, y Friedman "
                  "la convirtió en bandera del monetarismo: si V es estable y el "
                  "producto lo fija el lado real, la inflación es SIEMPRE un fenómeno "
                  "monetario. Toda hiperinflación conocida la confirma; los períodos "
                  "tranquilos, la matizan."),
        autores=("Fisher (1911); tradición Bodin-Hume-Ricardo; resurrección "
                 "monetarista: Friedman (años 50-60) — menciones."),
        supuestos=[
            "V estable: la tecnología de pagos y los hábitos cambian lento (FALLA con innovación financiera e inflaciones altas).",
            "Y exógeno al dinero: pleno empleo clásico — válido a largo plazo (m22), falso a corto (m23).",
            "Causalidad M→P: el dinero es exógeno (con banca endógena y metas de tasa, M responde a P — m39).",
        ],
        ecuaciones=[
            Ecuacion("M\\,V \\equiv P\\,Y", "ecuación de cambio",
                     "como identidad es incontestable: todo gasto (P·Y) fue pagado con dinero que "
                     "circuló (M·V). El CONTENIDO teórico está en fijar V e Y."),
            Ecuacion("\\pi \\approx g_M + g_V - g_Y", "la aritmética de la inflación",
                     "el crecimiento del dinero que excede al del producto (ajustado por velocidad) "
                     "se hace inflación: la regla de dedo de todo banco central."),
        ],
        intuicion=("Si hay el doble de billetes persiguiendo los mismos bienes, cada "
                   "bien cuesta el doble: el dinero es un velo sobre lo real. La "
                   "potencia de la teoría está en los extremos (hiperinflaciones: gM "
                   "de tres dígitos → π de tres dígitos, sin excepción histórica) y su "
                   "debilidad en los matices (V inestable, Y respondiendo a corto "
                   "plazo)."),
        equilibrio=("P = (V/Y)·M es proporcionalidad pura: sin dinámica interna. La "
                    "versión dinámica (tasas) hereda la misma lógica período a período."),
        limitaciones=[
            "V resultó INESTABLE tras la innovación financiera de los 80: los agregados dejaron de predecir π y los bancos centrales abandonaron las metas monetarias (→ m38-m39).",
            "A corto plazo Y responde (m23): la proporcionalidad es de largo plazo.",
            "Con metas de tasa de interés, M es ENDÓGENA: la causalidad de la ecuación se lee al revés.",
        ],
        evolucion=("Es el fundamento del nivel: m35 formaliza la neutralidad dinámica, "
                   "m36 explota la ecuación como máquina fiscal (señoreaje), m37 abre "
                   "la caja de M (multiplicador), y m38-m40 cuentan por qué los bancos "
                   "centrales modernos ya no la usan como regla operativa aunque la "
                   "respetan como restricción de largo plazo."),
    ),
    escenarios=[
        Escenario("duplicar_dinero", "el banco central duplica M (500 → 1000)",
                  {"M": 1000.0},
                  "P se duplica exactamente y M/P no se mueve: el experimento mental "
                  "de Hume hecho aritmética.",
                  cadena=["↑M ×2", "mismo Y, misma V", "el doble de dinero persigue lo mismo",
                          "P ×2 exacto", "M/P intacto: neutralidad cuantitativa"]),
        Escenario("emision_desbocada", "gM = 50% anual con gY = 3%",
                  {"gM": 50.0},
                  "π ≈ 45.6%: la antesala de toda hiperinflación — el señoreaje (m36) "
                  "explica POR QUÉ un gobierno llega aquí.",
                  cadena=["gM ≫ gY", "el dinero crece mucho más que los bienes",
                          "π ≈ gM − gY", "inflación alta y creciente si gM no cede"]),
        Escenario("auge_real", "el producto acelera a gY = 6% con gM = 8%",
                  {"gY": 6.0},
                  "π cae a ~1.9%: crecer absorbe dinero — la deflación secular del "
                  "patrón oro ocurría cuando gY superaba al oro nuevo.",
                  cadena=["↑gY", "más bienes para el mismo crecimiento de M",
                          "↓π ≈ gM − gY", "el crecimiento como ancla desinflacionaria"]),
        Escenario("digitalizacion", "los pagos digitales suben V (gV = +4%)",
                  {"gV": 4.0},
                  "misma emisión, más inflación: cada sol trabaja más veces — y la "
                  "V inestable es exactamente lo que rompió las metas monetarias.",
                  cadena=["↑V (innovación de pagos)", "cada sol circula más",
                          "MV sube sin tocar M", "↑π: la V inestable rompe la regla"]),
    ],
    verificaciones=[
        Verificacion("identidad MV = PY exacta", _v_identidad),
        Verificacion("proporcionalidad: 2M ⇒ 2P exacto", _v_proporcionalidad),
        Verificacion("aproximación de tasas válida (error < 0.5 pp)", _v_aproximacion),
        Verificacion("M/P invariante a M (lo real no escala)", _v_real_intacto),
    ],
    notas="La teoría macro más vieja en uso: infalible en hiperinflaciones, frágil en los matices.",
)
