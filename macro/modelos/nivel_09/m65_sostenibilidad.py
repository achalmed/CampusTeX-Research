# m65_sostenibilidad.py — sostenibilidad fiscal: ¿cuánta deuda cabe? (nivel 9).
#
# La ecuación de m64 convertida en DIAGNÓSTICO. Tres números:
#   sp*  = b·(r−g)/(1+g)     el primario REQUERIDO para estabilizar
#   sp_max                    el primario FACTIBLE (techo político-económico)
#   b_max = sp_max·(1+g)/(r−g)   la deuda máxima sostenible (donde se cruzan)
# Diagnóstico: sostenible si sp* ≤ sp_max (equivale a b ≤ b_max). La prueba
# de ESTRÉS repite el cálculo con r+Δr y g−Δg: las crisis no avisan con los
# parámetros de tiempos de paz (así trabajan los DSA del FMI, mención).
#
# Procedencia: análisis de sostenibilidad estándar (DSA; condición de
# no-Ponzi como fundamento — menciones) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sp_req(b, r, g):
    return b * (r / 100 - g / 100) / (1 + g / 100)


def _b_max(p, r=None, g=None):
    r = p["r"] if r is None else r
    g = p["g"] if g is None else g
    if r <= g:
        return float("inf")
    return p["sp_max"] * (1 + g / 100) / (r / 100 - g / 100)


def _curvas(p):
    b = np.linspace(0, 160, 200)
    req = _sp_req(b, p["r"], p["g"])
    req_estres = _sp_req(b, p["r"] + p["dr"], p["g"] - p["dg"])
    bmax = _b_max(p)
    lineas = {"$sp^*(b)$ requerido": (b, req, config.AZUL2),
              "$sp^*(b)$ bajo ESTRÉS": (b, req_estres, config.ROJO),
              "techo factible $sp_{max}$": (b, np.full_like(b, p["sp_max"]), config.GRIS)}
    puntos = [(p["b0"], float(_sp_req(p["b0"], p["r"], p["g"])), "tu país (base)")]
    if np.isfinite(bmax):
        puntos.append((bmax, p["sp_max"], f"$b_{{max}} = {bmax:.0f}\\%$"))
    return {"lineas": lineas, "puntos": puntos,
            "anotacion": (f"margen en base: {p['sp_max'] - _sp_req(p['b0'], p['r'], p['g']):+.2f}% del PIB\n"
                          f"margen bajo estrés: "
                          f"{p['sp_max'] - _sp_req(p['b0'], p['r'] + p['dr'], p['g'] - p['dg']):+.2f}%\n"
                          "sostenible = el requerido cabe bajo el techo")}


def _resultados(p):
    req = _sp_req(p["b0"], p["r"], p["g"])
    req_s = _sp_req(p["b0"], p["r"] + p["dr"], p["g"] - p["dg"])
    bmax = _b_max(p)
    bmax_s = _b_max(p, r=p["r"] + p["dr"], g=p["g"] - p["dg"])
    return {"sp* requerido (base, % PIB)": req,
            "sp* requerido (estrés)": req_s,
            "margen base (sp_max − sp*)": p["sp_max"] - req,
            "margen bajo estrés": p["sp_max"] - req_s,
            "b_max sostenible (base, %)": bmax if np.isfinite(bmax) else 9999.0,
            "b_max bajo estrés (%)": bmax_s if np.isfinite(bmax_s) else 9999.0}


def _ecuaciones_calibradas(p):
    return [f"$sp^* = {p['b0']:.0f} \\times \\frac{{{(p['r'] - p['g']) / 100:.3f}}}{{{1 + p['g'] / 100:.2f}}} "
            f"= {_sp_req(p['b0'], p['r'], p['g']):.2f}\\%$",
            f"$b_{{max}} = {p['sp_max']:.1f} \\times \\frac{{{1 + p['g'] / 100:.2f}}}"
            f"{{{(p['r'] - p['g']) / 100:.3f}}} = {_b_max(p):.0f}\\%$"]


_P0 = {"b0": 60.0, "r": 5.0, "g": 3.0, "sp_max": 1.5, "dr": 2.0, "dg": 1.0}


def _v_cruce():
    bmax = _b_max(_P0)
    req_en_bmax = _sp_req(bmax, _P0["r"], _P0["g"])
    return abs(req_en_bmax - _P0["sp_max"]) < 1e-12, \
        (f"en b_max = {bmax:.1f}% el requerido iguala EXACTO al techo: la deuda máxima "
         "es el cruce de dos rectas — aritmética, no opinión")


def _v_base_sostenible():
    margen = _P0["sp_max"] - _sp_req(_P0["b0"], _P0["r"], _P0["g"])
    return margen > 0, (f"en la base el margen es +{margen:.2f}% del PIB: sostenible — "
                        "el requerido cabe bajo el techo político")


def _v_estres_voltea():
    req_s = _sp_req(_P0["b0"], _P0["r"] + _P0["dr"], _P0["g"] - _P0["dg"])
    return req_s > _P0["sp_max"], \
        (f"bajo estrés (r+2, g−1) el requerido salta a {req_s:.2f}% > techo {_P0['sp_max']}%: "
         "el MISMO país es insostenible con los parámetros de crisis — por eso se estresa")


def _v_linealidad():
    r1 = _sp_req(_P0["b0"], _P0["r"], _P0["g"])
    r2 = _sp_req(2 * _P0["b0"], _P0["r"], _P0["g"])
    return abs(r2 - 2 * r1) < 1e-12, \
        "sp*(2b) = 2·sp*(b): el esfuerzo requerido es lineal en la herencia (m64)"


MODELO = Modelo(
    id="m65", nivel=9,
    nombre="Sostenibilidad fiscal",
    xlabel="Deuda/PIB $b$ (%)", ylabel="Primario requerido $sp^*$ (% PIB)",
    parametros=[
        Parametro("b0", _P0["b0"], 10, 150, 5, "Deuda/PIB del país b0 (%)", grupo="posición"),
        Parametro("sp_max", _P0["sp_max"], 0.5, 4, 0.25, "Primario factible sp_max", grupo="techo",
                  definicion="el máximo esfuerzo político-económicamente creíble"),
        Parametro("r", _P0["r"], 1, 10, 0.25, "Tasa real r (%)", grupo="la carrera"),
        Parametro("g", _P0["g"], 0, 8, 0.25, "Crecimiento g (%)", grupo="la carrera"),
        Parametro("dr", _P0["dr"], 0, 5, 0.5, "Estrés de tasas +Δr (pp)", grupo="estrés"),
        Parametro("dg", _P0["dg"], 0, 4, 0.5, "Estrés de crecimiento −Δg (pp)", grupo="estrés"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánta deuda cabe en un país — y por qué la respuesta cambia justo cuando más importa?",
        variables=[("sp*(b)", "el esfuerzo requerido — recta creciente en la herencia"),
                   ("sp_max", "el techo — economía política hecha número"),
                   ("b_max", "la deuda máxima — el cruce; más allá, la aritmética no cierra")],
        derivacion=["sp^*(b) = \\frac{b\\,(r-g)}{1+g} \\;\\;(m64)",
                    "sostenible \\iff sp^*(b_0) \\le sp_{max}",
                    "b_{max} = \\frac{sp_{max}\\,(1+g)}{r-g}"],
        contexto=("La sostenibilidad no es un juicio moral sino un cruce de rectas: "
                  "el esfuerzo que la deuda EXIGE (m64) contra el esfuerzo que el "
                  "país PUEDE entregar — un techo que combina capacidad tributaria, "
                  "paciencia política y tolerancia social. El análisis practicado "
                  "(los DSA del FMI, mención) añade la vuelta de tuerca decisiva: "
                  "estresar los parámetros, porque las crisis suben r y bajan g A "
                  "LA VEZ — el mismo país que 'cabe' en tiempos de paz puede no "
                  "caber con los números de guerra, y el mercado (m48) hace esa "
                  "cuenta antes que el ministro."),
        autores=("Marco DSA del FMI (mención); fundamento teórico: condición de "
                 "no-Ponzi / restricción presupuestaria intertemporal (mención); "
                 "la relectura r<g: Blanchard 2019 (mención)."),
        supuestos=[
            "sp_max exógeno y conocido: en la realidad es difuso y se descubre en las malas (los mercados lo estiman antes, m76).",
            "r y g independientes de b: el círculo vicioso (más b ⇒ más prima ⇒ más r) queda como lectura — es el corazón de m76.",
            "Estrés paramétrico simple (r+Δr, g−Δg): los DSA reales usan distribuciones y fan charts (mención).",
        ],
        ecuaciones=[
            Ecuacion("b_{max} = \\frac{sp_{max}(1+g)}{r-g}", "la deuda máxima",
                     "con techo 1.5% y r−g=2pp: cabe hasta 77% del PIB; si el estrés lleva r−g a "
                     "5pp, el máximo se desploma a 31% — el espacio fiscal es HIJO de la carrera."),
            Ecuacion("margen = sp_{max} - sp^*(b_0)", "el espacio fiscal",
                     "positivo: colchón para contracíclica (m68); negativo: ajuste, licuación o "
                     "default en el horizonte (m36, m76)."),
        ],
        intuicion=("El gráfico es un juicio en dos actos: la recta azul (requerido "
                   "en paz) deja al país holgado; la roja (estrés) puede condenarlo "
                   "sin que nada haya pasado TODAVÍA. Esa asimetría explica la "
                   "obsesión de los emergentes por deber poco: no por virtud, sino "
                   "porque SU estrés es más violento (la prima de m48 salta más). "
                   "El margen fiscal es un seguro que se compra en las buenas — la "
                   "lógica de la regla fiscal peruana y su fondo de estabilización "
                   "(mención; m108)."),
        equilibrio=("No hay dinámica aquí: es el diagnóstico ESTÁTICO sobre la "
                    "dinámica de m64. El cruce b_max está verificado exacto; la "
                    "linealidad sp*(b) hace todo el análisis transparente."),
        limitaciones=[
            "El techo sp_max es la variable más incierta del modelo — y la menos económica: es política pura.",
            "Sin retroalimentación b→r: la sostenibilidad REAL es un equilibrio múltiple (creído sostenible ⇒ r baja ⇒ sostenible) — m76.",
            "La deuda óptima no aparece: esto acota el máximo, no recomienda un nivel (Blanchard 2019 discute si conviene más deuda cuando r<g, mención).",
        ],
        evolucion=("Cierra la aritmética del bloque (m62-m65) y arma el tablero "
                   "para los debates: ¿el ajuste ayuda o se autodestruye? (m69), "
                   "¿los hogares neutralizan la deuda? (m67), ¿y cuándo el mercado "
                   "deja de creer? (m76). La versión peruana con datos del MEF es "
                   "m108."),
    ),
    escenarios=[
        Escenario("pais_holgado", "b0=60% con techo de 1.5% y r−g=2pp",
                  {"b0": 60.0},
                  "requerido 1.17% < techo 1.5%: sostenible con margen de 0.33% — "
                  "pero la línea roja ya muestra el veredicto del estrés.",
                  cadena=["b moderada", "sp* bajo el techo", "margen positivo",
                          "espacio para contracíclica (m68)", "…mientras r−g no salte"]),
        Escenario("prueba_de_estres", "r+2pp y g−1pp (los números de crisis)",
                  {"dr": 2.0, "dg": 1.0},
                  "el requerido salta a 2.91% > 1.5%: el MISMO país, insostenible "
                  "bajo estrés — la cuenta que el mercado hace primero (m48, m76).",
                  cadena=["crisis: ↑r y ↓g a la vez", "sp* se duplica",
                          "supera al techo político", "el mercado lo ve venir",
                          "la prima sube ANTES del default: m76"]),
        Escenario("herencia_pesada", "b0 = 120% (posguerra o post-rescate)",
                  {"b0": 120.0},
                  "el requerido (2.33%) ya supera al techo EN PAZ: solo quedan "
                  "crecimiento (g), licuación inflacionaria (m36) o reestructura (m76).",
                  cadena=["b alta", "sp* > sp_max sin estrés", "el ajuste factible no alcanza",
                          "las salidas restantes no son fiscales: g, inflación o default"]),
        Escenario("techo_fragil", "capacidad de ajuste baja: sp_max = 0.8%",
                  {"sp_max": 0.8},
                  "b_max cae a 41%: con instituciones débiles, hasta deudas 'bajas' "
                  "quedan grandes — el espacio fiscal es institucional, no solo aritmético.",
                  cadena=["↓sp_max (economía política)", "b_max se desploma",
                          "el mismo b0 queda sobre el máximo", "la fragilidad es el techo, no la deuda"]),
    ],
    verificaciones=[
        Verificacion("b_max = cruce exacto de requerido y techo", _v_cruce),
        Verificacion("la base es sostenible (margen > 0)", _v_base_sostenible),
        Verificacion("el estrés voltea el diagnóstico", _v_estres_voltea),
        Verificacion("sp* lineal en b (el costo de esperar)", _v_linealidad),
    ],
    notas="Sostenibilidad = el requerido cabe bajo el techo. El estrés hace la cuenta que las crisis harán.",
)
