# m39_corredor_tasas.py — el banco central y la tasa: corredor operativo (nivel 6).
#
# Cómo se IMPLEMENTA la tasa de política (la que Taylor recomienda en m38):
# el mercado interbancario de reservas con un corredor de facilidades:
#   demanda de reservas:  R(i) = a − b·i   (decreciente: la tasa es su costo)
#   oferta: S (operaciones del banco central) ;  corredor: [i_dep, i_vent]
#   i_eq = min(max((a−S)/b, i_dep), i_vent)   — el corredor ACOTA siempre.
# Los bancos centrales modernos (BCRP incluido: tasa de referencia +
# ventanillas — mención) fijan el PRECIO del dinero, no su cantidad.
#
# Procedencia: operativa estándar de bancos centrales con corredor —
# conocimiento general (doc. institucional); calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _corredor(p):
    return p["i_pol"] - p["ancho"] / 2, p["i_pol"] + p["ancho"] / 2


def _i_eq(p, S=None):
    S = p["S"] if S is None else S
    piso, techo = _corredor(p)
    return float(min(max((p["a"] - S) / p["b"], piso), techo))


def _curvas(p):
    piso, techo = _corredor(p)
    i = np.linspace(max(0, piso - 2), techo + 2, 200)
    R = p["a"] - p["b"] * i
    Rspan = np.linspace(min(R.min(), p["S"] - 10), max(R.max(), p["S"] + 10), 2)
    return {"lineas": {"demanda de reservas $R(i) = a - b\\,i$": (R, i, config.AZUL2),
                       "oferta $S$ (operaciones del BC)": (np.full(2, p["S"]), np.linspace(i.min(), i.max(), 2), config.ROJO),
                       "techo: ventanilla $i_{vent}$": (Rspan, np.full(2, techo), config.GRIS),
                       "piso: depósitos $i_{dep}$": (Rspan, np.full(2, piso), config.VERDE)},
            "equilibrio": (p["S"], _i_eq(p)),
            "anotacion": (f"corredor: $[{piso:.2f},\\,{techo:.2f}]$ en torno a "
                          f"$i_{{pol}} = {p['i_pol']:.2f}\\%$\n"
                          f"interbancaria efectiva: $i = {_i_eq(p):.2f}\\%$\n"
                          "nadie presta bajo el piso ni pide sobre el techo")}


def _resultados(p):
    piso, techo = _corredor(p)
    sin_corredor = (p["a"] - p["S"]) / p["b"]
    i = _i_eq(p)
    return {"tasa interbancaria efectiva (%)": i,
            "tasa sin corredor (a−S)/b (%)": sin_corredor,
            "piso (facilidad de depósito, %)": piso,
            "techo (ventanilla, %)": techo,
            "¿qué ata? (0 mercado, −1 piso, +1 techo)":
                (-1.0 if sin_corredor < piso else (1.0 if sin_corredor > techo else 0.0))}


def _ecuaciones_calibradas(p):
    piso, techo = _corredor(p)
    return [f"$R(i) = {p['a']:.0f} - {p['b']:.0f}\\,i, \\quad S = {p['S']:.0f}$",
            f"$i_{{mercado}} = ({p['a']:.0f}-{p['S']:.0f})/{p['b']:.0f} = {(p['a'] - p['S']) / p['b']:.2f}\\%$",
            f"$i = clip({(p['a'] - p['S']) / p['b']:.2f};\\,{piso:.2f},\\,{techo:.2f}) = {_i_eq(p):.2f}\\%$"]


_P0 = {"i_pol": 4.0, "ancho": 1.0, "S": 100.0, "a": 140.0, "b": 10.0}


def _v_interior():
    i = _i_eq(_P0)
    return abs(i - (140 - 100) / 10) < 1e-12, \
        f"con liquidez equilibrada la interbancaria queda en el centro: i = {i:.2f}% = i_pol"


def _v_piso_ata():
    i = _i_eq(_P0, S=125.0)
    return abs(i - 3.5) < 1e-12, ("con exceso de liquidez (S=125) el mercado pediría 1.5% pero "
                                  f"NADIE presta bajo el piso: i = {i:.2f}% (el piso ata)")


def _v_techo_ata():
    i = _i_eq(_P0, S=80.0)
    return abs(i - 4.5) < 1e-12, ("con escasez (S=80) el mercado pediría 6% pero nadie paga más "
                                  f"que la ventanilla: i = {i:.2f}% (el techo ata)")


def _v_acotacion_universal():
    piso, techo = _corredor(_P0)
    ok = all(piso - 1e-12 <= _i_eq(_P0, S=s) <= techo + 1e-12 for s in np.linspace(20, 250, 47))
    return ok, "para CUALQUIER nivel de reservas, i queda dentro del corredor: el control es robusto"


MODELO = Modelo(
    id="m39", nivel=6,
    nombre="Banco central y tasa de interés (corredor)",
    xlabel="Reservas bancarias ($R$)", ylabel="Tasa interbancaria $i$ (%)",
    parametros=[
        Parametro("i_pol", _P0["i_pol"], 0.5, 8, 0.25, "Tasa de política i_pol", grupo="banco central",
                  definicion="el centro del corredor: la decisión de m38"),
        Parametro("S", _P0["S"], 20, 250, 5, "Oferta de reservas S", grupo="banco central",
                  definicion="operaciones de mercado abierto"),
        Parametro("ancho", _P0["ancho"], 0.25, 3, 0.25, "Ancho del corredor (pp)", grupo="banco central",
                  definicion="ventanilla − depósitos"),
        Parametro("a", _P0["a"], 80, 220, 5, "Demanda autónoma de reservas a", grupo="bancos"),
        Parametro("b", _P0["b"], 2, 30, 1, "Sensibilidad de la demanda b", grupo="bancos",
                  definicion="cuántas reservas liberan los bancos por punto de tasa"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo hace el banco central para que la tasa que anuncia sea la que rige — sin adivinar la demanda de dinero?",
        variables=[("i", "tasa interbancaria — el precio que se controla"),
                   ("S", "reservas ofrecidas — el ajuste fino"),
                   ("[i_dep, i_vent]", "el corredor — dos promesas que acotan todo")],
        derivacion=["R(i) = a - b\\,i \\;\\;(demanda\\;de\\;reservas)",
                    "mercado: \\; i_m = \\frac{a-S}{b}",
                    "i = \\min(\\max(i_m,\\,i_{dep}),\\,i_{vent})"],
        contexto=("m34-m37 explicaron por qué controlar CANTIDADES de dinero falló: "
                  "V inestable, m endógeno, demanda impredecible. La solución "
                  "operativa moderna invierte el problema: fijar el PRECIO. El banco "
                  "central promete prestar sin límite a la tasa techo (ventanilla) y "
                  "remunerar depósitos a la tasa piso: ningún banco cruza esas "
                  "promesas, así que la interbancaria vive dentro del corredor pase "
                  "lo que pase con la demanda. El BCRP opera así: tasa de referencia "
                  "con facilidades de ventanilla (mención; detalles con datos en "
                  "nivel 12)."),
        autores=("Operativa institucional de bancos centrales modernos (BCE, Canadá, "
                 "BCRP… — menciones de conocimiento general); análisis del 'canal': "
                 "literatura de implementación monetaria (Woodford, mención)."),
        supuestos=[
            "Las facilidades son creíbles e ilimitadas: el arbitraje hace el resto.",
            "Demanda de reservas lineal y estable a corto plazo (los errores los absorbe el corredor, no la tasa).",
            "Un solo mercado interbancario sin fricciones ni estigma de ventanilla (mención: el estigma existe).",
        ],
        ecuaciones=[
            Ecuacion("i \\in [i_{dep},\\, i_{vent}]", "la promesa doble",
                     "prestar a i_vent y captar a i_dep son opciones SIEMPRE disponibles: ninguna "
                     "transacción racional ocurre fuera — el corredor es arbitraje puro."),
            Ecuacion("i = clip\\Big(\\frac{a-S}{b}\\Big)", "el equilibrio acotado",
                     "dentro del corredor manda el mercado; en los bordes mandan las facilidades: "
                     "los errores de pronóstico de demanda cuestan centésimas, no puntos."),
        ],
        intuicion=("El corredor convierte un problema de puntería (acertar S para "
                   "lograr i) en uno de carpintería (poner paredes donde se quiere la "
                   "tasa). Por eso subir la tasa de política es mover el corredor — "
                   "las reservas apenas cambian. La 'cantidad de dinero' pasa de "
                   "instrumento a residuo: exactamente la inversión de causalidad "
                   "que la crítica endógena de m37 pedía."),
        equilibrio=("i único para cada S (verificado: interior exacto, bordes exactos, "
                    "acotación universal). La tasa efectiva sigue a la de política "
                    "por construcción — la credibilidad operativa está resuelta; la "
                    "credibilidad ESTRATÉGICA (m41) es otra historia."),
        limitaciones=[
            "Estigma de ventanilla: en crisis los bancos evitan el techo y la tasa puede tensarse (mención 2008).",
            "Con exceso estructural de reservas (post-QE) el sistema opera 'de piso': solo importa i_dep (mención).",
            "El corredor fija la tasa CORTA: la transmisión a las tasas largas y al crédito es el canal completo (m10, m101).",
        ],
        evolucion=("Con el instrumento resuelto, las preguntas restantes son de "
                   "RÉGIMEN: qué meta anunciar (m40), cómo hacerla creíble (m41) y "
                   "qué pasa cuando los agentes anticipan la regla (m42). La versión "
                   "peruana — tasa de referencia del BCRP y su transmisión a la "
                   "inflación — es m100-m101."),
    ),
    escenarios=[
        Escenario("inyeccion_de_liquidez", "el BC compra títulos: S sube a 125",
                  {"S": 125.0},
                  "sin corredor la tasa caería a 1.5%; el piso la sostiene en 3.5%: "
                  "el error de cantidad no se vuelve error de precio.",
                  cadena=["↑S (compra de títulos)", "exceso de reservas",
                          "el mercado pediría i muy baja", "nadie presta bajo i_dep",
                          "i = piso: el corredor absorbe el exceso"]),
        Escenario("drenaje", "el BC vende títulos: S baja a 80",
                  {"S": 80.0},
                  "el mercado pediría 6%; la ventanilla presta ilimitado a 4.5%: "
                  "el techo ata y la escasez no se vuelve crisis de liquidez.",
                  cadena=["↓S", "escasez de reservas", "presión alcista sobre i",
                          "la ventanilla presta a i_vent", "i = techo"]),
        Escenario("subir_la_tasa", "decisión de política: i_pol de 4% a 5%",
                  {"i_pol": 5.0},
                  "el corredor entero sube y la interbancaria lo sigue (el piso "
                  "nuevo la arrastra) casi sin tocar reservas: así 'sube la tasa' "
                  "un banco central moderno.",
                  cadena=["anuncio: ↑i_pol", "el corredor se traslada",
                          "el arbitraje reprecia el interbancario",
                          "i efectiva sube SIN mover S", "el precio manda, la cantidad acomoda"]),
        Escenario("corredor_angosto", "afinar el control: ancho de 1.0 a 0.25 pp",
                  {"ancho": 0.25},
                  "la tasa efectiva queda a ±0.125 pp de la política: más precisión "
                  "a cambio de menos mercado interbancario (todo pasa por el BC).",
                  cadena=["↓ancho", "las paredes se acercan", "volatilidad de i mínima",
                          "el interbancario pierde papel (trade-off)"]),
    ],
    verificaciones=[
        Verificacion("interior: i = (a−S)/b exacto", _v_interior),
        Verificacion("exceso de liquidez: el piso ata exacto", _v_piso_ata),
        Verificacion("escasez: el techo ata exacto", _v_techo_ata),
        Verificacion("acotación universal (cualquier S)", _v_acotacion_universal),
    ],
    notas="Fijar el precio y dejar que la cantidad acomode: la inversión operativa que m37 pedía.",
)
