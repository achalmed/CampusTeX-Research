"""simuladores/macro/modelos/nivel_04/m24_estanflacion.py — estanflación en el aparato completo (nivel 4).

El episodio de los 70 reconstruido con el AD-AS de m23 y leído en el tablero
completo del policymaker: producto, precios (π), tasa implícita y desempleo
(vía Okun). Compara las tres respuestas históricas al shock de costos:
  nada / acomodar (dM>0, la Fed de Burns) / resistir (dM<0, Volcker).

Procedencia: aparato AD-AS de manual; episodios OPEP 1973/1979, Fed de
Burns y desinflación de Volcker: menciones históricas de conocimiento
general. Okun con β didáctico (m15).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _equilibrio(p, ds, dM, dG):
    F, bh, Ac = _adas.estructura(p)
    Y, P = _adas.equilibrio_corto(F + dG, bh, Ac, p["M"] + dM,
                                  p["Pe"] + ds, p["lam"], p["Ystar"])
    return Y, P, (p["k"] * Y - (p["M"] + dM) / P) / p["h"]


def _curvas(p):
    F, bh, Ac = _adas.estructura(p)
    Y = np.linspace(550, 850, 200)
    ad0 = bh * p["M"] / (Ac * Y - F)
    ad1 = bh * (p["M"] + p["dM"]) / (Ac * Y - (F + p["dG"]))
    sras0 = p["Pe"] + p["lam"] * (Y - p["Ystar"])
    sras1 = p["Pe"] + p["ds"] + p["lam"] * (Y - p["Ystar"])
    (Y0, P0, _), (Y1, P1, _) = _equilibrio(p, 0, 0, 0), _equilibrio(p, p["ds"], p["dM"], p["dG"])
    pi = 100 * (P1 / P0 - 1)
    du = -0.4 * (100 * (Y1 - Y0) / Y0)
    return {"lineas": {"AD (con respuesta $dM,\\,dG$)": (Y, ad1, config.AZUL2),
                       "AD original": (Y, ad0, config.GRIS),
                       "SRAS con costos ($ds$)": (Y, sras1, config.ROJO),
                       "SRAS original": (Y, sras0, config.VERDE)},
            "puntos": [(Y0, P0, "antes"), (Y1, P1, "después")],
            "anotacion": (f"tablero del policymaker:\n"
                          f"$\\pi = {pi:+.1f}\\%$,  $\\Delta u \\approx {du:+.1f}$ pp (Okun)\n"
                          f"brecha $= {Y1 - p['Ystar']:+.1f}$")}


def _resultados(p):
    (Y0, P0, r0), (Y1, P1, r1) = _equilibrio(p, 0, 0, 0), _equilibrio(p, p["ds"], p["dM"], p["dG"])
    return {"Y antes": Y0, "Y después": Y1,
            "π del episodio (%)": 100 * (P1 / P0 - 1),
            "Δu vía Okun β=0.4 (pp)": -0.4 * (100 * (Y1 - Y0) / Y0),
            "r antes": r0, "r después": r1,
            "brecha final": Y1 - p["Ystar"]}


_P0 = {"ds": 0.4, "dM": 0.0, "dG": 0.0,
       "c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "G": 200.0, "T": 100.0,
       "k": 0.5, "h": 10.0, "M": 590.0, "Pe": 2.0, "lam": 0.004, "Ystar": 700.0}


def _v_tablero_imposible():
    r = _resultados(_P0)
    ok = r["π del episodio (%)"] > 0 and r["Δu vía Okun β=0.4 (pp)"] > 0
    return ok, (f"π={r['π del episodio (%)']:+.1f}% Y Δu={r['Δu vía Okun β=0.4 (pp)']:+.1f} pp "
                "SUBEN a la vez: el punto que la Phillips original (m13) declaraba imposible")


def _v_acomodo_inflacionario():
    _, P_nada, _ = _equilibrio(_P0, _P0["ds"], 0.0, 0.0)
    Y_aco, P_aco, _ = _equilibrio(_P0, _P0["ds"], 100.0, 0.0)
    Y_nada, _, _ = _equilibrio(_P0, _P0["ds"], 0.0, 0.0)
    return (Y_aco > Y_nada and P_aco > P_nada), \
        (f"acomodar (dM=100) recupera producto ({Y_nada:,.0f}→{Y_aco:,.0f}) pagando más "
         f"inflación ({P_nada:.2f}→{P_aco:.2f}): la Fed de Burns")


def _v_resistencia_recesiva():
    Y_nada, P_nada, _ = _equilibrio(_P0, _P0["ds"], 0.0, 0.0)
    Y_res, P_res, _ = _equilibrio(_P0, _P0["ds"], -80.0, 0.0)
    return (Y_res < Y_nada and P_res < P_nada), \
        (f"resistir (dM=−80) contiene precios ({P_nada:.2f}→{P_res:.2f}) profundizando la "
         f"recesión ({Y_nada:,.0f}→{Y_res:,.0f}): Volcker")


def _v_sin_shock_sin_drama():
    Y, P, _ = _equilibrio(_P0, 0.0, 0.0, 0.0)
    return abs(Y - _P0["Ystar"]) < 1e-9 and abs(P - _P0["Pe"]) < 1e-9, \
        "sin shock de costos el sistema descansa en (Y*, Pe): el drama lo trae ds"


MODELO = Modelo(
    id="m24", nivel=4,
    nombre="Estanflación (episodio en el aparato completo)",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("ds", _P0["ds"], 0.0, 0.8, 0.05, "Shock de costos ds (petróleo)"),
        Parametro("dM", _P0["dM"], -150, 150, 10, "Respuesta monetaria dM"),
        Parametro("dG", _P0["dG"], -80, 80, 10, "Respuesta fiscal dG"),
        Parametro("lam", _P0["lam"], 0.001, 0.012, 0.001, "Rigidez λ"),
        Parametro("Pe", _P0["Pe"], 1.5, 2.8, 0.1, "Precio esperado Pe"),
        Parametro("Ystar", _P0["Ystar"], 620, 780, 10, "Producto potencial Y*"),
        Parametro("M", _P0["M"], 450, 750, 10, "Dinero nominal M"),
        Parametro("G", _P0["G"], 120, 300, 10, "Gasto público G"),
        Parametro("T", _P0["T"], 20, 250, 10, "Impuestos T"),
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de I a r (b)"),
        Parametro("k", _P0["k"], 0.25, 0.9, 0.05, "Demanda de dinero por Y (k)"),
        Parametro("h", _P0["h"], 5, 22, 1, "Demanda de dinero por r (h)"),
        Parametro("c0", _P0["c0"], 60, 180, 10, "Consumo autónomo c0"),
        Parametro("I0", _P0["I0"], 80, 260, 10, "Inversión autónoma I0"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="Ante un shock petrolero, ¿acomodar o resistir — y quién paga cada opción?",
        contexto=("1973-1982: dos shocks petroleros, inflación de dos dígitos y "
                  "desempleo récord en las economías industriales — al mismo tiempo. "
                  "La palabra 'estanflación' nombró lo que la teoría de los 60 no "
                  "tenía cómo nombrar. Este modelo repite el episodio dentro del "
                  "AD-AS completo y pone al usuario en el sillón del banquero "
                  "central: la Fed de Burns acomodó (y la inflación se enquistó), "
                  "la de Volcker resistió (y la recesión de 1982 fue el precio)."),
        autores=("Aparato: síntesis neoclásica (m23); lectura del episodio: patrimonio "
                 "común de la literatura sobre los 70 (Burns, Volcker: menciones); el "
                 "porqué teórico profundo lo dieron Friedman-Phelps (m14)."),
        supuestos=[
            "Los del AD-AS completo (m23), con el shock entrando por costos (ds).",
            "Pe fijo durante el episodio: si el shock contamina expectativas (como en los 70 reales), la SRAS sigue subiendo sola — eso es m25 con ds persistente.",
            "Okun con β=0.4 didáctico para leer empleo (m15).",
        ],
        ecuaciones=[
            Ecuacion("ds > 0: \\; Y\\downarrow,\\; P\\uparrow,\\; u\\uparrow", "la tripleta imposible",
                     "en la Phillips original π y u no podían subir juntos; con la SRAS "
                     "desplazándose, sí — el shock de costos mueve la oferta, no la demanda."),
            Ecuacion("\\text{acomodar: } dM>0 \\;\\to\\; Y\\uparrow,\\,P\\uparrow\\uparrow \\;;\\;"
                     "\\text{resistir: } dM<0 \\;\\to\\; P\\downarrow,\\,Y\\downarrow\\downarrow",
                     "el menú del banquero central",
                     "no hay respuesta que recupere producto Y precios a la vez: el shock de "
                     "oferta solo se REPARTE, no se anula."),
        ],
        intuicion=("La estanflación es una transferencia forzada: el insumo caro "
                   "empobrece a la economía y la política solo decide en qué moneda "
                   "pagar — inflación o desempleo. La salida real de los 70 no fue "
                   "ninguna de las dos: fue anclar expectativas (Volcker primero por "
                   "las malas, las metas de inflación después por las buenas, m40-41)."),
        equilibrio=("Estática comparativa del AD-AS con desplazamiento de SRAS y "
                    "respuesta opcional de AD; el tablero (π, Δu, r, brecha) resume "
                    "cada equilibrio para leerlo como episodio de política."),
        limitaciones=[
            "Un solo período: la persistencia real de los 70 vino de expectativas contaminadas período tras período (m25 con ds; la espiral completa exige m14).",
            "Okun didáctico: el pass-through a desempleo depende del mercado laboral (para Perú, m15/m112).",
            "El shock ds es exógeno: en economías importadoras es tipo de cambio × precio internacional — inflación importada (m113).",
        ],
        evolucion=("Cierra el arco teórico del nivel 3-4: lo que m13 no podía "
                   "explicar, m14 predijo y m23-m24 representan con fundamento. La "
                   "pregunta pendiente — ¿cómo DEBE responder el banco central? — es "
                   "el corazón del nivel 6 (m38-m41) y del modelo de 3 ecuaciones (m56)."),
    ),
    escenarios=[
        Escenario("opep_sin_respuesta", "shock ds=0.4, política pasiva",
                  {"ds": 0.4, "dM": 0.0, "dG": 0.0},
                  "la tripleta imposible en el tablero: π>0, Δu>0, brecha negativa.",
                  cadena=["↑ds", "SRAS → arriba", "↓Y con ↑P", "Okun: ↑u",
                          "π y u suben JUNTOS: estanflación"]),
        Escenario("fed_de_burns", "acomodar con dM=+100",
                  {"ds": 0.4, "dM": 100.0},
                  "el producto casi vuelve… y la inflación del episodio se duplica: "
                  "así se enquistó la inflación de los 70.",
                  cadena=["shock + ↑dM", "AD → derecha", "Y casi vuelve",
                          "P sube el doble", "inflación enquistada (Burns)"]),
        Escenario("volcker", "resistir con dM=−80",
                  {"ds": 0.4, "dM": -80.0},
                  "los precios ceden pero la brecha se hace el doble de honda: la "
                  "recesión de 1982 como precio de la credibilidad.",
                  cadena=["shock + ↓dM", "AD → izquierda", "P cede",
                          "brecha doble", "la recesión de 1982 (Volcker)"]),
        Escenario("doble_shock", "1979: segundo shock encima del primero (ds=0.8)",
                  {"ds": 0.8, "dM": 0.0},
                  "con el doble de shock, TODO empeora más que al doble en producto: "
                  "la no linealidad de la AD (M/P) muerde.",
                  cadena=["ds ×2 (1979 sobre 1973)", "SRAS mucho más arriba",
                          "la AD hiperbólica castiga más que al doble", "1979-1982"]),
    ],
    verificaciones=[
        Verificacion("π y Δu suben a la vez (imposible para m13)", _v_tablero_imposible),
        Verificacion("acomodar recupera Y pagando inflación", _v_acomodo_inflacionario),
        Verificacion("resistir contiene P profundizando la recesión", _v_resistencia_recesiva),
        Verificacion("sin ds el sistema descansa en (Y*, Pe)", _v_sin_shock_sin_drama),
    ],
    notas="El usuario en el sillón del banquero central de 1973: no hay salida gratis, solo repartos.",
)
