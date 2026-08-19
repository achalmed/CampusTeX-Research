# m19_shock_oferta.py — shock de oferta y estanflación (nivel 3).
#
# El mismo aparato AD-SRAS de m18, pero el shock golpea la OFERTA (costos):
#   AD:    Y = A + dA − b·P            (dA: posible respuesta de política)
#   SRAS:  P = Pe + ds + λ·(Y − Y*)    (ds: shock de costos — petróleo, clima)
# Firma del shock de OFERTA: P sube e Y cae — direcciones OPUESTAS.
# Dilema del banco central: acomodar (dA>0, recupera Y pagando más inflación)
# o resistir (dA<0, contiene P profundizando la recesión).
#
# Procedencia: AD-AS de manual (conocimiento general); episodios OPEP 1973/79:
# mención histórica; calibración: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _eq(p, ds, dA):
    Y = (p["A"] + dA - p["b"] * (p["Pe"] + ds) + p["b"] * p["lam"] * p["Ystar"]) / (1 + p["b"] * p["lam"])
    P = p["Pe"] + ds + p["lam"] * (Y - p["Ystar"])
    return Y, P


def _curvas(p):
    Y = np.linspace(400, 800, 200)
    ad = (p["A"] + p["dA"] - Y) / p["b"]
    sras0 = p["Pe"] + p["lam"] * (Y - p["Ystar"])
    sras1 = p["Pe"] + p["ds"] + p["lam"] * (Y - p["Ystar"])
    (Y0, P0), (Y1, P1) = _eq(p, 0.0, 0.0), _eq(p, p["ds"], p["dA"])
    return {"lineas": {"AD (con respuesta $dA$)": (Y, ad, config.AZUL2),
                       "SRAS base": (Y, sras0, config.VERDE),
                       "SRAS con shock de costos ($ds$)": (Y, sras1, config.ROJO)},
            "puntos": [(Y0, P0, f"antes $({Y0:,.0f},\\,{P0:.2f})$"),
                       (Y1, P1, f"después $({Y1:,.0f},\\,{P1:.2f})$")],
            "anotacion": (f"$\\Delta Y = {Y1 - Y0:+.1f}$,  $\\Delta P = {P1 - P0:+.2f}$\n"
                          "direcciones opuestas: ESTANFLACIÓN")}


def _resultados(p):
    (Y0, P0), (Y1, P1) = _eq(p, 0.0, 0.0), _eq(p, p["ds"], p["dA"])
    du = -0.4 * (100 * (Y1 - Y0) / Y0)
    return {"Y antes": Y0, "Y después": Y1, "ΔY": Y1 - Y0,
            "P antes": P0, "P después": P1, "ΔP": P1 - P0,
            "Δu vía Okun β=0.4 (pp)": du,
            "brecha final (Y−Y*)": Y1 - p["Ystar"]}


_P0 = {"A": 700.0, "b": 50.0, "Pe": 2.0, "lam": 0.02, "Ystar": 600.0,
       "ds": 0.5, "dA": 0.0}


def _v_equilibrio():
    Y1, P1 = _eq(_P0, _P0["ds"], _P0["dA"])
    ad = _P0["A"] + _P0["dA"] - _P0["b"] * P1
    sras = _P0["Pe"] + _P0["ds"] + _P0["lam"] * (Y1 - _P0["Ystar"])
    return abs(ad - Y1) < 1e-9 and abs(sras - P1) < 1e-9, "el equilibrio satisface AD y SRAS con shock"


def _v_estanflacion():
    (Y0, P0), (Y1, P1) = _eq(_P0, 0.0, 0.0), _eq(_P0, _P0["ds"], 0.0)
    ok = (Y1 - Y0) < 0 and (P1 - P0) > 0
    return ok, f"ΔY={Y1 - Y0:+.1f} y ΔP={P1 - P0:+.2f}: signos OPUESTOS — la firma que rompió a m13"


def _v_acomodo():
    Y_sin, P_sin = _eq(_P0, _P0["ds"], 0.0)
    Y_con, P_con = _eq(_P0, _P0["ds"], 25.0)
    ok = abs(Y_con - _P0["Ystar"]) < 1e-9 and P_con > P_sin
    return ok, (f"acomodo dA=25: recupera Y=Y* exacto, pero P sube a {P_con:.2f} "
                f"(vs {P_sin:.2f} sin acomodar) — el dilema en números")


def _v_resistencia():
    Y_sin, P_sin = _eq(_P0, _P0["ds"], 0.0)
    Y_res, P_res = _eq(_P0, _P0["ds"], -25.0)
    ok = P_res < P_sin and Y_res < Y_sin
    return ok, (f"resistir dA=−25: contiene P ({P_res:.2f}) al precio de hundir más Y "
                f"({Y_res:,.0f}) — no hay respuesta gratis a un shock de oferta")


MODELO = Modelo(
    id="m19", nivel=3,
    nombre="Shock de oferta (estanflación)",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("ds", _P0["ds"], -0.6, 1.2, 0.1, "Shock de costos ds (petróleo, clima)"),
        Parametro("dA", _P0["dA"], -60, 60, 5, "Respuesta de demanda dA (política)"),
        Parametro("lam", _P0["lam"], 0.005, 0.06, 0.005, "Pendiente de la SRAS (λ)"),
        Parametro("b", _P0["b"], 20, 100, 5, "Sensibilidad de la AD a P (b)"),
        Parametro("A", _P0["A"], 500, 900, 10, "Demanda autónoma A"),
        Parametro("Pe", _P0["Pe"], 1.0, 4.0, 0.1, "Precio esperado Pe"),
        Parametro("Ystar", _P0["Ystar"], 450, 750, 10, "Producto potencial Y*"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Por qué un shock de costos crea inflación Y recesión a la vez — y "
                  "qué puede hacer la política?"),
        contexto=("Octubre de 1973: la OPEP cuadruplica el precio del petróleo y las "
                  "economías industriales descubren una combinación que su teoría "
                  "declaraba imposible: inflación Y desempleo subiendo a la vez. La "
                  "Phillips original (m13) no tenía casilla para eso; el aparato AD-AS "
                  "sí: basta que el shock golpee los COSTOS y no el gasto. La "
                  "estanflación de los 70 reordenó la macroeconomía y encumbró a "
                  "Friedman-Phelps (m14)."),
        autores=("Aparato AD-AS de manual (conocimiento general); el análisis clásico "
                 "de los shocks petroleros de 1973 y 1979 es patrimonio común de la "
                 "literatura macro de los 70-80."),
        supuestos=[
            "El shock ds encarece producir CUALQUIER nivel de Y (petróleo, insumos, clima, salarios exógenos).",
            "Pe fijo dentro del período: si el shock contamina expectativas, la espiral es peor (m14, m24).",
            "Y* intacto: un shock persistente que destruye capacidad también recorta el potencial (limitación).",
        ],
        ecuaciones=[
            Ecuacion("P = P^e + ds + \\lambda\\,(Y - Y^*)", "SRAS desplazada",
                     "ds sube el precio al que las empresas ofrecen cada Y: la curva entera se "
                     "traslada hacia arriba — no es un movimiento SOBRE la curva."),
            Ecuacion("\\Delta Y = \\frac{-b\\,ds}{1+b\\lambda} < 0, \\quad \\Delta P = \\frac{ds}{1+b\\lambda} > 0",
                     "estanflación",
                     "el mismo shock reparte signos opuestos: la demanda, al encarecerse todo, compra "
                     "menos producto — inflación con recesión."),
            Ecuacion("dA^{acomodo} = b\\,ds", "acomodo exacto",
                     "la expansión de demanda que devuelve Y a Y*: funciona, pero convalida TODO el "
                     "shock en precios (ΔP = ds) — la semilla de la espiral de los 70."),
        ],
        intuicion=("Con shocks de demanda la política no enfrenta dilema (m18); con "
                   "shocks de oferta elige entre dos males: acomodar (recuperar "
                   "producto convalidando inflación) o resistir (defender precios "
                   "profundizando la recesión). Los 70 acomodaron y cosecharon espiral; "
                   "Volcker resistió y cosechó la recesión del 82. No hay tercera "
                   "opción dentro de este aparato — solo mejores anclas de "
                   "expectativas (m40-m41)."),
        equilibrio=("Intersección AD-SRAS'. La estática comparativa respecto de ds y dA "
                    "contiene todo el menú de política; el caso dA=b·ds (acomodo "
                    "exacto) es verificable numéricamente."),
        limitaciones=[
            "Pe fijo esconde lo peor: la indexación de expectativas convierte un shock transitorio en inflación persistente (m14; el ajuste completo es m24-m25).",
            "Shock permanente ≠ transitorio: si ds recorta Y* (energía estructuralmente más cara), acomodar persigue un potencial que ya no existe.",
            "Sin sector externo: para Perú los shocks de oferta llegan por alimentos/energía importados y clima — inflación importada (m113) y shock climático (m114).",
        ],
        evolucion=("Completa la pareja de firmas: demanda = mismo signo (m18), oferta = "
                   "signos opuestos. El nivel 4 monta ambos en el AD-AS completo con "
                   "ajuste de expectativas (m23-m25), y el nivel 6 pregunta cómo "
                   "DEBERÍA responder el banco central (m38-m41) — la respuesta moderna "
                   "del BCRP ante shocks de alimentos es el caso aplicado (m113)."),
    ),
    escenarios=[
        Escenario("opep_1973", "shock de costos ds = +0.5 sin respuesta de política",
                  {"ds": 0.5, "dA": 0.0},
                  "producto cae, precios suben, desempleo sube (Okun): la tripleta de "
                  "la estanflación que la Phillips original declaraba imposible."),
        Escenario("acomodo_monetario", "el banco central expande demanda (dA = +25)",
                  {"ds": 0.5, "dA": 25.0},
                  "Y vuelve exactamente a Y*... y la inflación se duplica: acomodar "
                  "convalida el shock — el camino de los 70."),
        Escenario("resistencia", "contracción para defender precios (dA = −25)",
                  {"ds": 0.5, "dA": -25.0},
                  "la inflación se contiene a costa de una recesión doble: el camino "
                  "de Volcker, adelantado una década."),
        Escenario("shock_favorable", "abaratamiento de costos ds = −0.3 (años 90)",
                  {"ds": -0.3, "dA": 0.0},
                  "el espejo virtuoso: más producto CON menos inflación — los "
                  "'vientos de cola' que hacen fácil cualquier política."),
    ],
    verificaciones=[
        Verificacion("equilibrio satisface AD y SRAS con shock", _v_equilibrio),
        Verificacion("firma de oferta: ΔY<0 con ΔP>0", _v_estanflacion),
        Verificacion("acomodo exacto: Y=Y* pero P convalida el shock", _v_acomodo),
        Verificacion("resistir: menos inflación, más recesión", _v_resistencia),
    ],
    notas="El dilema que no existe con shocks de demanda: acomodar o resistir, nunca gratis.",
)
