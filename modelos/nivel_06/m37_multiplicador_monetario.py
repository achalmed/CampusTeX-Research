# m37_multiplicador_monetario.py — creación de dinero y multiplicador (nivel 6).
#
# La base B (efectivo + reservas) se multiplica en dinero M vía el circuito
# depósito → préstamo → redepósito (el m04 del sistema bancario):
#   redepósito por unidad depositada: κ = (1−r)/(1+c)
#   m = M/B = (1+c)/(c+r)   con  c = efectivo/depósitos,  r = reservas/depósitos
# Identidad de cierre: B = C + R exacta en el límite.
#
# Procedencia: mecánica estándar de manuales de dinero y banca — conocimiento
# general. La crítica moderna (dinero endógeno: los bancos crean depósitos al
# prestar y el banco central acomoda reservas) se documenta en limitaciones.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _m(p):
    return (1 + p["c"]) / (p["c"] + p["r"])


def _serie(p):
    n = np.arange(int(round(p["rondas"])) + 1)
    kappa = (1 - p["r"]) / (1 + p["c"])
    dep = (p["B"] / (1 + p["c"])) * kappa ** n          # depósito nuevo de la ronda
    D_acum = np.cumsum(dep)
    M_acum = (1 + p["c"]) * D_acum                       # M = C + D = (1+c)·D
    return n, dep, M_acum, kappa


def _curvas(p):
    n, dep, M_acum, kappa = _serie(p)
    tope = np.full_like(n, _m(p) * p["B"], dtype=float)
    return {"lineas": {"dinero $M$ acumulado": (n, M_acum, config.AZUL2),
                       "depósito nuevo de la ronda": (n, dep, config.ROJO),
                       "límite $m \\cdot B$": (n, tope, config.GRIS)},
            "equilibrio": (float(n[-1]), float(M_acum[-1])),
            "anotacion": (f"$m = \\frac{{1+c}}{{c+r}} = \\frac{{{1 + p['c']:.2f}}}{{{p['c'] + p['r']:.2f}}} "
                          f"= {_m(p):.2f}$\n"
                          f"$M = m \\cdot B = {_m(p) * p['B']:,.1f}$\n"
                          f"redepósito por ronda: $\\kappa = {kappa:.2f}$")}


def _resultados(p):
    n, dep, M_acum, kappa = _serie(p)
    m = _m(p)
    D = M_acum[-1] / (1 + p["c"])
    return {"multiplicador m = (1+c)/(c+r)": m,
            "dinero total M = m·B": m * p["B"],
            f"M tras {int(n[-1])} rondas": float(M_acum[-1]),
            "depósitos D": float(D),
            "efectivo C = c·D": float(p["c"] * D),
            "reservas R = r·D": float(p["r"] * D)}


def _ecuaciones_calibradas(p):
    return [f"$\\kappa = (1-{p['r']:.2f})/(1+{p['c']:.2f}) = {(1 - p['r']) / (1 + p['c']):.2f}$",
            f"$m = (1+{p['c']:.2f})/({p['c']:.2f}+{p['r']:.2f}) = {_m(p):.2f}$",
            f"$M = {_m(p):.2f} \\times {p['B']:.0f} = {_m(p) * p['B']:,.0f}$"]


_P0 = {"B": 100.0, "r": 0.10, "c": 0.25, "rondas": 20.0}


def _v_suma_geometrica():
    _, _, M_acum, _ = _serie(dict(_P0, rondas=400))
    return abs(float(M_acum[-1]) - _m(_P0) * _P0["B"]) < 1e-6, \
        f"la suma de rondas converge exactamente a m·B = {_m(_P0) * _P0['B']:,.1f}"


def _v_identidad_base():
    r = _resultados(dict(_P0, rondas=400))
    uso = r["efectivo C = c·D"] + r["reservas R = r·D"]
    return abs(uso - _P0["B"]) < 1e-6, (f"C + R = {uso:,.1f} = B: cada sol de base termina "
                                        "de efectivo en bolsillos o de reserva en bóvedas")


def _v_encaje_frena():
    m1, m2 = _m(_P0), _m(dict(_P0, r=0.25))
    return m2 < m1, f"subir el encaje (r: 0.10→0.25) baja m de {m1:.2f} a {m2:.2f}: menos préstamo por depósito"


def _v_fuga_a_efectivo():
    m1, m2 = _m(_P0), _m(dict(_P0, c=0.60))
    return m2 < m1, (f"si el público huye a efectivo (c: 0.25→0.60), m cae de {m1:.2f} a {m2:.2f}: "
                     "la mecánica de una corrida bancaria (m73)")


MODELO = Modelo(
    id="m37", nivel=6,
    nombre="Multiplicador monetario",
    xlabel="Ronda del circuito bancario ($n$)", ylabel="Dinero creado",
    parametros=[
        Parametro("B", _P0["B"], 20, 300, 10, "Base monetaria B", grupo="banco central",
                  definicion="efectivo + reservas: lo único que emite el banco central"),
        Parametro("r", _P0["r"], 0.02, 0.5, 0.01, "Encaje r (reservas/depósitos)", grupo="bancos",
                  definicion="fracción de depósitos que no se presta"),
        Parametro("c", _P0["c"], 0.05, 1.0, 0.05, "Preferencia por efectivo c", grupo="público",
                  definicion="efectivo/depósitos que mantiene el público"),
        Parametro("rondas", _P0["rondas"], 5, 60, 1, "Rondas simuladas", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Quién crea el dinero — y por qué la mayor parte no la imprime el banco central?",
        variables=[("B", "base monetaria — la que emite el banco central"),
                   ("M = C + D", "dinero amplio — el que usa la economía"),
                   ("m = M/B", "el multiplicador — decidido por bancos (r) y público (c)")],
        derivacion=["depósito \\to préstamo\\;(1-r) \\to redepósito\\;\\frac{1}{1+c}",
                    "\\kappa = \\frac{1-r}{1+c}, \\quad D = \\frac{B}{(1+c)(1-\\kappa)}",
                    "m = \\frac{M}{B} = \\frac{1+c}{c+r}"],
        contexto=("El grueso del dinero moderno no son billetes: son depósitos que "
                  "nacen cuando un banco presta. La mecánica del multiplicador — el "
                  "m04 del sistema bancario — explica cómo una base pequeña sostiene "
                  "una masa grande, y por qué esa masa es FRÁGIL: depende de que los "
                  "bancos quieran prestar (r) y el público quiera depositar (c). Las "
                  "corridas del nivel 10 y los colapsos monetarios de las depresiones "
                  "son este multiplicador funcionando en reversa."),
        autores=("Mecánica de manual de dinero y banca (conocimiento general); la "
                 "lectura del colapso de m en la Gran Depresión es de "
                 "Friedman-Schwartz (1963, mención)."),
        supuestos=[
            "r y c constantes durante el proceso: bancos siempre dispuestos a prestar el (1−r), público siempre re-depositando.",
            "Los préstamos encuentran demanda: nadie deja liquidez ociosa (FALLA en crisis: reservas voluntarias).",
            "Causalidad B→M: el banco central fija B y M resulta (la crítica endógena la invierte).",
        ],
        ecuaciones=[
            Ecuacion("m = \\frac{1+c}{c+r}", "el multiplicador",
                     "dos filtraciones frenan el circuito: el encaje r (dinero que duerme en "
                     "bóvedas) y el efectivo c (dinero que sale del circuito bancario)."),
            Ecuacion("B = C + R", "la identidad de cierre",
                     "al final del proceso, cada sol de base está o en bolsillos o en reservas: "
                     "verificable exacto, como las filtraciones de m01."),
        ],
        intuicion=("Es una serie geométrica con dos grifos de fuga — la misma "
                   "matemática del multiplicador keynesiano (m04), con bancos en vez "
                   "de hogares. La lección de política: m NO es una constante "
                   "técnica; es CONFIANZA hecha número. Cuando el público corre al "
                   "efectivo (c↑) o los bancos atesoran (r↑), m colapsa y la misma "
                   "base sostiene mucho menos dinero — sin que el banco central haya "
                   "tocado nada."),
        equilibrio=("Convergencia geométrica (κ<1 siempre): el límite m·B es estable "
                    "MIENTRAS r y c lo sean — que es exactamente lo que una crisis "
                    "bancaria destruye."),
        limitaciones=[
            "La visión moderna invierte la causalidad: los bancos crean depósitos al prestar y consiguen reservas después; con metas de tasa (m39) el banco central ACOMODA B — el multiplicador describe una proporción, no un mecanismo de control (McLeay et al., Banco de Inglaterra 2014 — mención).",
            "r y c son endógenos al ciclo y al pánico: precisamente cuando importa, m no es estable.",
            "Sin tasas de interés ni riesgo de crédito: el racionamiento crediticio queda fuera (nivel 10).",
        ],
        evolucion=("Cierra la mecánica clásica del dinero (M de m34 ya tiene "
                   "anatomía) y explica por qué m39 abandona el control de agregados: "
                   "si m baila con la confianza, controlar B no controla M — mejor "
                   "fijar el PRECIO del dinero (la tasa). La reversa del "
                   "multiplicador reaparece como corrida en m73."),
    ),
    escenarios=[
        Escenario("encaje_restrictivo", "el banco central sube el encaje (r: 0.10→0.25)",
                  {"r": 0.25},
                  "m cae de 3.57 a 2.50: menos crédito por cada sol de base — el "
                  "instrumento clásico de encajes que el BCRP aún usa (mención).",
                  cadena=["↑r", "cada depósito presta menos", "κ cae",
                          "el circuito muere antes", "↓m: menos M con la misma B"]),
        Escenario("panico_bancario", "el público corre al efectivo (c: 0.25→0.60)",
                  {"c": 0.60},
                  "m se hunde de 3.57 a 2.29 SIN que el banco central toque nada: la "
                  "destrucción monetaria de toda corrida (m73) — Friedman-Schwartz "
                  "leyeron así la Gran Depresión.",
                  cadena=["pánico", "↑c: retiros masivos", "los depósitos no se re-crean",
                          "↓m", "M colapsa con B constante", "deflación de crisis"]),
        Escenario("banca_digital", "billeteras y pagos digitales bajan c a 0.10",
                  {"c": 0.10},
                  "m sube a 5.5: menos efectivo circulando es más multiplicación — "
                  "el trasfondo monetario de la digitalización de pagos.",
                  cadena=["↓c (pagos digitales)", "casi todo vuelve al banco",
                          "κ sube", "↑m: más M por sol de base"]),
    ],
    verificaciones=[
        Verificacion("suma de rondas = m·B (fórmula cerrada)", _v_suma_geometrica),
        Verificacion("identidad B = C + R exacta en el límite", _v_identidad_base),
        Verificacion("más encaje ⇒ menos multiplicador", _v_encaje_frena),
        Verificacion("fuga a efectivo ⇒ m colapsa (corrida)", _v_fuga_a_efectivo),
    ],
    notas="El m04 del sistema bancario — y la confianza hecha número: cuando c o r saltan, M colapsa sola.",
)
