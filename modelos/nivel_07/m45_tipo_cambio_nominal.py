# m45_tipo_cambio_nominal.py — el mercado cambiario (nivel 7).
#
# El precio de la divisa como cualquier precio: oferta y demanda de dólares.
#   oferta  O(E) = a + b·E   (exportadores y capitales que entran: con E alto
#                             — sol depreciado — exportar rinde más soles)
#   demanda D(E) = c − d·E + dBC  (importadores, salidas… y el banco central)
#   E* = (c + dBC − a)/(b + d)      [E = soles por dólar]
# Convención crucial: E↑ = DEPRECIACIÓN del sol; E↓ = apreciación.
# dBC>0: el banco central COMPRA dólares (acumula RIN y frena la apreciación
# — la intervención típica del BCRP en bonanzas, mención).
#
# Procedencia: mercado de flujos didáctico (manuales) — conocimiento general;
# la visión moderna de activos llega en m48 (UIP). Calibración didáctica
# alrededor de E≈3.5 PEN/USD.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _e_eq(p):
    return (p["c"] + p["dBC"] - p["a"]) / (p["b"] + p["d"])


def _curvas(p):
    E = np.linspace(2.5, 4.5, 200)
    O = p["a"] + p["b"] * E
    D = p["c"] + p["dBC"] - p["d"] * E
    Ee = _e_eq(p)
    return {"lineas": {"oferta de USD (exportadores, capitales)": (O, E, config.AZUL2),
                       "demanda de USD (importadores + BC)": (D, E, config.ROJO)},
            "equilibrio": (p["a"] + p["b"] * Ee, Ee),
            "anotacion": (f"$E^* = {Ee:.3f}$ soles/USD\n"
                          f"intervención del BC: {p['dBC']:+.0f} USD "
                          f"({'compra' if p['dBC'] > 0 else 'venta' if p['dBC'] < 0 else 'ninguna'})\n"
                          "E↑ = sol depreciado · E↓ = sol apreciado")}


def _resultados(p):
    Ee = _e_eq(p)
    return {"tipo de cambio E* (PEN/USD)": Ee,
            "USD transados en equilibrio": p["a"] + p["b"] * Ee,
            "RIN acumuladas por el BC (=dBC)": p["dBC"],
            "dE*/d(oferta autónoma)": -1 / (p["b"] + p["d"]),
            "dE*/d(demanda autónoma)": 1 / (p["b"] + p["d"])}


def _ecuaciones_calibradas(p):
    return [f"$O(E) = {p['a']:.0f} + {p['b']:.0f}\\,E$",
            f"$D(E) = {p['c'] + p['dBC']:.0f} - {p['d']:.0f}\\,E$",
            f"$E^* = ({p['c'] + p['dBC']:.0f} - {p['a']:.0f})/{p['b'] + p['d']:.0f} = {_e_eq(p):.3f}$"]


_P0 = {"a": 50.0, "b": 40.0, "c": 330.0, "d": 40.0, "dBC": 0.0}


def _v_equilibrio():
    Ee = _e_eq(_P0)
    dif = (_P0["a"] + _P0["b"] * Ee) - (_P0["c"] + _P0["dBC"] - _P0["d"] * Ee)
    return abs(dif) < 1e-12, f"en E*={Ee:.3f} la oferta iguala a la demanda de dólares (exceso = 0)"


def _v_bonanza_aprecia():
    e0, e1 = _e_eq(_P0), _e_eq(dict(_P0, a=90.0))
    return e1 < e0, (f"más dólares entrando (a: 50→90) aprecian el sol (E {e0:.2f}→{e1:.2f}): "
                     "la bonanza del cobre baja el tipo de cambio")


def _v_intervencion():
    e0, e1 = _e_eq(_P0), _e_eq(dict(_P0, dBC=40.0))
    return e1 > e0, (f"si el BC compra 40 de USD, E sube de {e0:.2f} a {e1:.2f}: la compra "
                     "frena la apreciación Y acumula RIN — dos pájaros (m43)")


def _v_linealidad():
    e0 = _e_eq(_P0)
    e1 = _e_eq(dict(_P0, c=_P0["c"] + 8.0))
    return abs((e1 - e0) - 8.0 / 80.0) < 1e-12, \
        "ΔE = Δdemanda/(b+d) exacto: la pendiente del mercado es 1/(b+d)"


MODELO = Modelo(
    id="m45", nivel=7,
    nombre="Tipo de cambio nominal (mercado cambiario)",
    xlabel="Dólares transados", ylabel="Tipo de cambio $E$ (PEN/USD)",
    parametros=[
        Parametro("a", _P0["a"], 20, 150, 5, "Oferta autónoma de USD", grupo="oferta",
                  definicion="exportaciones y entradas de capital a cualquier E"),
        Parametro("c", _P0["c"], 250, 420, 5, "Demanda autónoma de USD", grupo="demanda",
                  definicion="importaciones, salidas, dolarización de portafolios"),
        Parametro("dBC", _P0["dBC"], -80, 80, 5, "Intervención del BC (dBC)", grupo="banco central",
                  definicion=">0 compra USD (acumula RIN); <0 vende (defiende el sol)"),
        Parametro("b", _P0["b"], 10, 80, 5, "Sensibilidad de la oferta b", grupo="oferta"),
        Parametro("d", _P0["d"], 10, 80, 5, "Sensibilidad de la demanda d", grupo="demanda"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Qué mueve el precio del dólar — y qué hace exactamente el banco central cuando 'interviene'?",
        variables=[("E", "soles por dólar — E↑ deprecia el sol (¡la convención importa!)"),
                   ("O(E), D(E)", "flujos de divisas — comercio y capitales"),
                   ("dBC", "la intervención — comprar/vender divisas contra RIN")],
        derivacion=["O(E) = a + b\\,E, \\quad D(E) = c + dBC - d\\,E",
                    "O(E^*) = D(E^*)",
                    "E^* = \\frac{c + dBC - a}{b + d}"],
        contexto=("El tipo de cambio es el precio más visible de una economía "
                  "abierta: encarece el pollo importado y decide cuántos soles vale "
                  "una tonelada de cobre. La versión de flujos — divisas que entran "
                  "por exportaciones y capital, divisas que salen por importaciones "
                  "y portafolios — es el punto de partida didáctico; la visión "
                  "moderna (m48) añadirá que a corto plazo mandan los STOCKS de "
                  "activos y las expectativas. La intervención esterilizada del "
                  "BCRP para suavizar el sol es práctica habitual (mención; series "
                  "reales en m102)."),
        autores=("Análisis de mercado de flujos (manuales de economía "
                 "internacional, conocimiento general); la crítica de activos: "
                 "literatura post-Bretton Woods (menciones)."),
        supuestos=["Flujos por período con pendientes estables (elasticidades de comercio: condición Marshall-Lerner detrás de b, d — mención).",
                   "El BC interviene comprando/vendiendo contra RIN sin efectos monetarios (esterilización implícita).",
                   "Sin expectativas: el E de mañana no mueve los flujos de hoy (eso es m48)."],
        ecuaciones=[
            Ecuacion("E^* = \\frac{c + dBC - a}{b + d}", "el precio de la divisa",
                     "aritmética de mercado: entra más dólar (a↑) → sol se aprecia; se demanda "
                     "más dólar (c↑) → sol se deprecia; el BC corre la demanda con dBC."),
        ],
        intuicion=("Pensar el dólar como cualquier fruta del mercado mayorista "
                   "desarma la mitad de la mística cambiaria: bonanza exportadora = "
                   "cosecha abundante = precio (E) baja. La intervención del banco "
                   "central es un comprador gigante que se lleva el excedente para "
                   "el almacén (RIN) — y ese almacén es exactamente el que financia "
                   "las defensas de m43/m50 cuando el viento cambia."),
        equilibrio=("E* único y estable (exceso de demanda decreciente en E). La "
                    "estática comparativa lineal ΔE = Δshock/(b+d) está verificada "
                    "exacta."),
        limitaciones=[
            "Los flujos comerciales explican el E de LARGO plazo; el de corto lo dominan capitales y expectativas — sin m48, este mercado no entiende un viernes de pánico.",
            "Intervención sin límites ni costos: las RIN son finitas (m50) y la esterilización tiene costo cuasifiscal (mención).",
            "Elasticidades fijas: la curva J y Marshall-Lerner (respuestas lentas del comercio) quedan como mención.",
        ],
        evolucion=("El E nominal es solo la mitad del precio: m46 lo deflacta (RER, "
                   "la competitividad de verdad), m47 le da ancla de largo plazo "
                   "(PPP) y m48 le da su motor de corto plazo (UIP). Todo desemboca "
                   "en m49. La serie PEN/USD real es m102."),
    ),
    escenarios=[
        Escenario("bonanza_exportadora", "entra más dólar: oferta autónoma 50 → 90",
                  {"a": 90.0},
                  "el sol se aprecia de 3.50 a 3.00: el síntoma cambiario de todo "
                  "boom de materias primas — y la antesala de la enfermedad "
                  "holandesa (m88).",
                  cadena=["↑precio del cobre", "más USD de exportadores", "exceso de oferta de divisas",
                          "E↓ (sol se aprecia)", "los transables no mineros sufren (m46)"]),
        Escenario("fuga_hacia_el_dolar", "demanda autónoma 330 → 390 (ruido político)",
                  {"c": 390.0},
                  "E salta a 4.25: la dolarización de portafolios en tiempo real — "
                  "lo que m48 explicará con expectativas y m74 convertirá en crisis.",
                  cadena=["incertidumbre", "portafolios se dolarizan", "exceso de demanda de USD",
                          "E↑ (sol se deprecia)", "passthrough a precios en camino (m46)"]),
        Escenario("bcrp_compra", "el BC compra 40 para frenar la apreciación",
                  {"a": 90.0, "dBC": 40.0},
                  "con bonanza + compra, E queda en 3.50 en vez de 3.00 y las RIN "
                  "suben 40: la flotación administrada peruana en una jugada.",
                  cadena=["bonanza aprecia", "el BC compra el excedente de USD",
                          "demanda total se repone", "E casi estable", "RIN +40 (m43)"]),
        Escenario("defensa_del_sol", "el BC vende 50 en plena fuga",
                  {"c": 390.0, "dBC": -50.0},
                  "la venta contiene E en 3.63 (vs 4.25)… gastando RIN: la defensa "
                  "tiene combustible finito — el reloj de m50.",
                  cadena=["fuga de portafolios", "el BC vende USD de las RIN",
                          "la depreciación se modera", "RIN caen: la defensa tiene fecha (m74)"]),
    ],
    verificaciones=[
        Verificacion("vaciado del mercado en E* (exceso = 0)", _v_equilibrio),
        Verificacion("bonanza de divisas aprecia el sol", _v_bonanza_aprecia),
        Verificacion("la compra del BC deprecia y acumula RIN", _v_intervencion),
        Verificacion("estática comparativa 1/(b+d) exacta", _v_linealidad),
    ],
    notas="E↑ = sol depreciado. El dólar como fruta de mercado — hasta que las expectativas (m48) entran a comprar.",
)
