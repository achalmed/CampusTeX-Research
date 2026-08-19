# m08_mercado_dinero.py — mercado monetario: preferencia por la liquidez (nivel 2).
#
# Demanda de saldos reales:  L(Y, r) = k·Y − h·r   (Y dado aquí)
# Oferta real de dinero:     M/P  (exógena, la fija el banco central)
# Equilibrio:  M/P = k·Y − h·r   →   r* = (k·Y − M/P) / h
#
# Gráfico en el plano (saldos reales, r): demanda decreciente en r, oferta
# vertical. Es el modelo gemelo de m06: allí r era exógena y salía Y*; aquí Y
# es exógeno y sale r*.
#
# Procedencia: teoría de la preferencia por la liquidez (Keynes 1936) en su
# versión lineal de manual — conocimiento general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _r_eq(p):
    return (p["k"] * p["Y"] - p["MP"]) / p["h"]


def _curvas(p):
    r = np.linspace(0, 12, 200)
    L = p["k"] * p["Y"] - p["h"] * r          # saldos demandados a cada tasa
    r_star = _r_eq(p)
    r_oferta = np.linspace(0, 12, 2)
    return {"lineas": {"demanda $L(Y,r) = kY - hr$": (L, r, config.AZUL2),
                       "oferta $M/P$ (banco central)": (np.full(2, p["MP"]), r_oferta, config.ROJO)},
            "equilibrio": (p["MP"], r_star),
            "anotacion": (f"$r^* = (kY - M/P)/h = {r_star:.2f}\\%$\n"
                          f"demanda por transacciones $kY = {p['k'] * p['Y']:,.1f}$")}


def _resultados(p):
    r_star = _r_eq(p)
    return {"r* (tasa de equilibrio)": r_star,
            "demanda transaccional kY": p["k"] * p["Y"],
            "L en r* (= M/P)": p["k"] * p["Y"] - p["h"] * r_star,
            "dr*/d(M/P) = −1/h": -1 / p["h"],
            "dr*/dY = k/h": p["k"] / p["h"]}


_P0 = {"Y": 700.0, "k": 0.5, "h": 10.0, "MP": 300.0}


def _v_vaciado():
    r_star = _r_eq(_P0)
    L = _P0["k"] * _P0["Y"] - _P0["h"] * r_star
    return abs(L - _P0["MP"]) < 1e-9, f"en r* la demanda iguala a la oferta ({L:,.1f} = M/P)"


def _v_mas_dinero_baja_r():
    d = _r_eq(dict(_P0, MP=_P0["MP"] + 10)) - _r_eq(_P0)
    return abs(d + 10 / _P0["h"]) < 1e-12, f"dr/dMP = −1/h exacto ({d:+.2f} por +10 de dinero)"


def _v_mas_actividad_sube_r():
    d = _r_eq(dict(_P0, Y=_P0["Y"] + 10)) - _r_eq(_P0)
    return abs(d - 10 * _P0["k"] / _P0["h"]) < 1e-12, (f"dr/dY = k/h exacto ({d:+.2f} por +10 de Y): "
                                                       "la semilla de la pendiente de la LM")


MODELO = Modelo(
    id="m08", nivel=2,
    nombre="Mercado monetario (preferencia por la liquidez)",
    xlabel="Saldos reales ($M/P$, $L$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("MP", _P0["MP"], 100, 600, 10, "Oferta real de dinero M/P"),
        Parametro("Y", _P0["Y"], 300, 1100, 25, "Ingreso Y (exógeno aquí)"),
        Parametro("k", _P0["k"], 0.1, 1.0, 0.05, "Sensibilidad de L a Y (k)"),
        Parametro("h", _P0["h"], 2, 30, 1, "Sensibilidad de L a r (h)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Qué determina la tasa de interés cuando el banco central fija la cantidad de dinero?",
        contexto=("¿Por qué alguien guardaría dinero, que no rinde, en vez de bonos, que "
                  "pagan r? Keynes respondió con la preferencia por la liquidez: se "
                  "demanda dinero para transar (crece con Y) y se sacrifica liquidez solo "
                  "si el premio r compensa (cae con r). Con ello la tasa de interés dejó "
                  "de ser el precio que equilibra ahorro e inversión (visión clásica de "
                  "fondos prestables) y pasó a ser el precio de la LIQUIDEZ."),
        autores=("Keynes (1936): motivos transacción, precaución y especulación; "
                 "formalización lineal de manual (síntesis); refinamientos posteriores: "
                 "Baumol-Tobin (demanda transaccional por inventarios, años 50)."),
        supuestos=[
            "Dos activos: dinero (líquido, rinde 0) y bonos (rinden r) — equilibrar el dinero equilibra los bonos (ley de Walras).",
            "Y exógeno: el mercado de bienes está 'congelado' mientras se analiza el del dinero.",
            "Oferta monetaria exógena: el banco central controla M y el nivel de precios P está fijo.",
            "Demanda lineal L = kY − hr (aproximación didáctica).",
        ],
        ecuaciones=[
            Ecuacion("L(Y,r) = k\\,Y - h\\,r", "demanda de saldos reales",
                     "kY: dinero para transar, proporcional a la actividad; −hr: costo de "
                     "oportunidad — con r alta se economiza liquidez y se prefieren bonos."),
            Ecuacion("\\frac{M}{P} = k\\,Y - h\\,r", "equilibrio del mercado",
                     "la oferta real (vertical: no depende de r) debe ser absorbida por la demanda."),
            Ecuacion("r^* = \\frac{k\\,Y - M/P}{h}", "tasa de equilibrio",
                     "dado Y: más dinero baja r (sobra liquidez → se compran bonos → sube su precio "
                     "→ cae su rendimiento); más actividad sube r (falta liquidez)."),
        ],
        intuicion=("El ajuste ocurre por el precio de los bonos: si hay exceso de dinero, "
                   "los agentes compran bonos, su precio sube y su rendimiento (r) cae "
                   "hasta que alguien esté dispuesto a retener todo el dinero emitido. "
                   "La tasa de interés es el precio que convence al público de mantener "
                   "exactamente la liquidez que existe."),
        equilibrio=("r* único y estable dado Y: con r > r* sobra dinero (se compran bonos, "
                    "r baja); con r < r* falta (se venden bonos, r sube)."),
        limitaciones=[
            "Y no es exógeno en la realidad: la tasa que aquí 'sale' afecta la inversión y por tanto Y — exige resolver ambos mercados a la vez (m10).",
            "Los bancos centrales modernos no fijan M: fijan la propia r y dejan M endógena (m39, m51).",
            "Sin inflación esperada: confunde tasa nominal y real (Fisher llega en m34/m38).",
            "La dicotomía dinero/bonos es extrema: sin depósitos remunerados, crédito bancario ni riesgo.",
        ],
        evolucion=("m09 barre este modelo sobre Y para trazar la curva LM (igual que m07 "
                   "barrió m06 sobre r). Cuando el instrumento pasa de M a la tasa "
                   "(práctica moderna del BCRP y todo banco central), la LM se vuelve "
                   "horizontal en la tasa de política: esa es la ruta a IS-MP (m51)."),
    ),
    escenarios=[
        Escenario("inyeccion_liquidez", "el banco central sube M/P de 300 a 330",
                  {"MP": 330.0},
                  "sobra liquidez → se compran bonos → r* cae de 5% a 2%: el mecanismo "
                  "diario de la política monetaria expansiva."),
        Escenario("contraccion", "venta de bonos del banco central (M/P: 300→250)",
                  {"MP": 250.0},
                  "falta liquidez → r* salta a 10%: el costo del dinero como freno."),
        Escenario("auge_de_actividad", "el ingreso sube de 700 a 800 con M fija",
                  {"Y": 800.0},
                  "más transacciones demandan más liquidez y, con oferta fija, r* sube a "
                  "10%: por esto la curva LM tendrá pendiente positiva (m09)."),
    ],
    verificaciones=[
        Verificacion("vaciado del mercado: L(r*) = M/P", _v_vaciado),
        Verificacion("más dinero baja r (dr/dMP = −1/h)", _v_mas_dinero_baja_r),
        Verificacion("más actividad sube r (dr/dY = k/h)", _v_mas_actividad_sube_r),
    ],
    notas="Modelo gemelo de m06: allí r exógena → Y*; aquí Y exógeno → r*. m10 resuelve ambos a la vez.",
)
