# m23_adas_completo.py — modelo AD-AS completo (nivel 4).
#
# Las tres piezas juntas por primera vez:
#   AD   (m20): Y = [F + dG + (b/h)(M+dM)/P] / Ac      (derivada de IS-LM)
#   SRAS (m21): P = Pe + ds + λ(Y − Y*)
#   LRAS (m22): Y = Y*  (referencia del ajuste)
# Equilibrio de corto plazo: AD ∩ SRAS (cuadrática, _adas.py). El sistema
# entrega además la r implícita del LM: el IS-LM sigue vivo debajo.
# Calibración: la base ARRANCA en el largo plazo (Y=Y*=700, P=Pe=2).
#
# Procedencia: aparato AD-AS de la síntesis, manuales de macro intermedia —
# conocimiento general; calibración: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _equilibrio(p, dG=None, dM=None, ds=None):
    F, bh, Ac = _adas.estructura(p)
    F += p["dG"] if dG is None else dG
    M = p["M"] + (p["dM"] if dM is None else dM)
    pe_ef = p["Pe"] + (p["ds"] if ds is None else ds)
    Y, P = _adas.equilibrio_corto(F, bh, Ac, M, pe_ef, p["lam"], p["Ystar"])
    r = (p["k"] * Y - M / P) / p["h"]
    return Y, P, r


def _curvas(p):
    F, bh, Ac = _adas.estructura(p)
    Y = np.linspace(550, 850, 200)
    P_ad = bh * (p["M"] + p["dM"]) / (Ac * Y - (F + p["dG"]))
    sras = p["Pe"] + p["ds"] + p["lam"] * (Y - p["Ystar"])
    (Y0, P0, _), (Y1, P1, _) = _equilibrio(p, 0.0, 0.0, 0.0), _equilibrio(p)
    return {"lineas": {"AD (con $dG,\\,dM$)": (Y, P_ad, config.AZUL2),
                       "SRAS (con $ds$)": (Y, sras, config.VERDE),
                       "LRAS ($Y=Y^*$)": (np.full(2, p["Ystar"]), np.linspace(1.2, 3.2, 2), config.GRIS)},
            "puntos": [(Y0, P0, f"sin shocks $({Y0:,.0f},\\,{P0:.2f})$"),
                       (Y1, P1, f"con shocks $({Y1:,.0f},\\,{P1:.2f})$")],
            "anotacion": (f"brecha $= {Y1 - p['Ystar']:+.1f}$\n"
                          f"$\\Delta Y = {Y1 - Y0:+.1f}$,  $\\Delta P = {P1 - P0:+.2f}$")}


def _resultados(p):
    Y1, P1, r1 = _equilibrio(p)
    return {"Y (corto plazo)": Y1, "P (corto plazo)": P1,
            "r implícita (del LM)": r1,
            "brecha Y − Y*": Y1 - p["Ystar"],
            "P de largo plazo (AD sobre LRAS)": _adas.precio_largo_plazo(
                _adas.estructura(p)[0] + p["dG"], p["b"] / p["h"],
                _adas.estructura(p)[2], p["M"] + p["dM"], p["Ystar"])}


def _ecuaciones_calibradas(p):
    F, bh, Ac = _adas.estructura(p)
    Y, P, r = _equilibrio(p)
    return [f"$AD:\\; Y = ({F + p['dG']:.0f} + {bh:.1f} \\times {p['M'] + p['dM']:.0f}/P)\\,/\\,{Ac:.2f}$",
            f"$SRAS:\\; P = {p['Pe'] + p['ds']:.2f} + {p['lam']:.3f}\\,(Y - {p['Ystar']:.0f})$",
            f"$Y = {Y:,.1f}, \\quad P = {P:.2f}, \\quad r = {r:.2f}$"]


_P0 = {"dG": 0.0, "dM": 0.0, "ds": 0.0,
       "c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "G": 200.0, "T": 100.0,
       "k": 0.5, "h": 10.0, "M": 590.0, "Pe": 2.0, "lam": 0.004, "Ystar": 700.0}


def _v_base_largo_plazo():
    Y, P, _ = _equilibrio(_P0)
    ok = abs(Y - _P0["Ystar"]) < 1e-9 and abs(P - _P0["Pe"]) < 1e-9
    return ok, f"sin shocks el sistema descansa en el largo plazo (Y={Y:,.1f}=Y*, P={P:.2f}=Pe)"


def _v_residuos():
    Y, P, _ = _equilibrio(dict(_P0, dG=50.0))
    F, bh, Ac = _adas.estructura(_P0)
    res_ad = Ac * Y - (F + 50.0) - bh * _P0["M"] / P
    res_sras = P - (_P0["Pe"] + _P0["lam"] * (Y - _P0["Ystar"]))
    return abs(res_ad) < 1e-9 and abs(res_sras) < 1e-9, \
        f"la raíz de la cuadrática satisface AD y SRAS (residuos {res_ad:.1e}, {res_sras:.1e})"


def _v_fiscal():
    (Y0, P0, r0), (Y1, P1, r1) = _equilibrio(_P0), _equilibrio(dict(_P0, dG=50.0))
    ok = Y1 > Y0 and P1 > P0 and r1 > r0
    return ok, (f"↑G: Y↑ ({Y0:,.0f}→{Y1:,.0f}), P↑ ({P0:.2f}→{P1:.2f}) y r↑ "
                f"({r0:.2f}→{r1:.2f}): demanda con precios Y tasa endógenos")


def _v_dinero_no_neutral_cp():
    (Y0, _, _), (Y1, _, _) = _equilibrio(_P0), _equilibrio(dict(_P0, dM=60.0))
    return Y1 > Y0, (f"a CORTO plazo el dinero NO es neutral: dM=60 sube Y "
                     f"({Y0:,.0f}→{Y1:,.0f}) — contraste directo con m22")


def _v_oferta():
    (Y0, P0, _), (Y1, P1, _) = _equilibrio(_P0), _equilibrio(dict(_P0, ds=0.3))
    return Y1 < Y0 and P1 > P0, (f"shock de costos: estanflación en el aparato completo "
                                 f"(Y {Y0:,.0f}→{Y1:,.0f}, P {P0:.2f}→{P1:.2f})")


MODELO = Modelo(
    id="m23", nivel=4,
    nombre="Modelo AD-AS completo",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dG", _P0["dG"], -100, 100, 10, "Shock fiscal dG", grupo="experimento",
                  definicion="desplaza la AD vía gasto"),
        Parametro("dM", _P0["dM"], -150, 150, 10, "Shock monetario dM", grupo="experimento",
                  definicion="desplaza la AD vía saldos reales"),
        Parametro("ds", _P0["ds"], -0.4, 0.6, 0.05, "Shock de costos ds", grupo="experimento",
                  definicion="desplaza la SRAS (petróleo, clima, salarios)"),
        Parametro("Pe", _P0["Pe"], 1.2, 3.0, 0.1, "Precio esperado Pe", grupo="oferta agregada",
                  definicion="posición de la SRAS: lo que los contratos esperaban"),
        Parametro("lam", _P0["lam"], 0.001, 0.012, 0.001, "Rigidez λ", grupo="oferta agregada",
                  definicion="pendiente de la SRAS: presión de precios por unidad de brecha"),
        Parametro("Ystar", _P0["Ystar"], 600, 800, 10, "Producto potencial Y*", grupo="oferta agregada",
                  definicion="ancla de largo plazo (su interior es el nivel 5)"),
        Parametro("M", _P0["M"], 400, 800, 10, "Dinero nominal M", grupo="mercado de dinero",
                  definicion="lo fija el banco central; real es M/P"),
        Parametro("k", _P0["k"], 0.2, 1.0, 0.05, "Demanda de dinero por Y (k)", grupo="mercado de dinero",
                  definicion="liquidez transaccional"),
        Parametro("h", _P0["h"], 4, 25, 1, "Demanda de dinero por r (h)", grupo="mercado de dinero",
                  definicion="sustitución dinero-bonos"),
        Parametro("G", _P0["G"], 100, 350, 10, "Gasto público G", grupo="mercado de bienes",
                  definicion="componente fiscal del gasto autónomo"),
        Parametro("T", _P0["T"], 0, 300, 10, "Impuestos T", grupo="mercado de bienes",
                  definicion="entran vía renta disponible"),
        Parametro("c1", _P0["c1"], 0.2, 0.9, 0.05, "Propensión a consumir c1", grupo="mercado de bienes",
                  definicion="re-gasto marginal de los hogares"),
        Parametro("b", _P0["b"], 5, 40, 1, "Sensibilidad de I a r (b)", grupo="mercado de bienes",
                  definicion="inversión descartada por punto de tasa"),
        Parametro("c0", _P0["c0"], 50, 200, 10, "Consumo autónomo c0", grupo="mercado de bienes",
                  definicion="consumo independiente del ingreso"),
        Parametro("I0", _P0["I0"], 50, 300, 10, "Inversión autónoma I0", grupo="mercado de bienes",
                  definicion="ánimo inversor autónomo"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta=("¿Cómo responden producto, precios y tasa de interés — a la vez — "
                  "ante shocks de demanda y de oferta?"),
        variables=[("Y, P, r", "producto, precios y tasa — endógenas simultáneas"),
                   ("dG, dM, ds", "shocks de política y de costos — exógenos"),
                   ("Pe", "expectativas de precios — dadas en el período (m25 las mueve)"),
                   ("Y*", "producto potencial — ancla de largo plazo (m22)")],
        derivacion=["A_c\\,Y = F + \\frac{b}{h}\\,\\frac{M}{P} \\;\\;(AD)",
                    "P = P^e + ds + \\lambda\\,(Y - Y^*) \\;\\;(SRAS)",
                    "A_c\\,Y\\,P(Y) = F\\,P(Y) + \\frac{b}{h}\\,M",
                    "a_2\\,Y^2 + a_1\\,Y + a_0 = 0 \\;\\to\\; Y^{+} \\;(raíz\\;positiva)"],
        contexto=("El aparato con el que la síntesis neoclásica enseñó macroeconomía "
                  "medio siglo: demanda derivada del IS-LM (m20), oferta de corto "
                  "plazo con expectativas (m21) y ancla clásica de largo plazo (m22), "
                  "todo en un solo plano (Y, P). Reconcilia a Keynes con los clásicos "
                  "por horizonte temporal: keynesiano mientras las expectativas están "
                  "fijas, clásico cuando terminan de ajustarse."),
        autores=("Síntesis neoclásica (Samuelson y los manuales de posguerra, "
                 "mención); las piezas: Hicks (AD vía IS-LM), Friedman-Phelps-Lucas "
                 "(la SRAS con expectativas), la tradición clásica (LRAS)."),
        supuestos=[
            "Los de sus tres piezas (m20, m21, m22) a la vez.",
            "Pe fijo DENTRO del período: este modelo es el fotograma; la película (Pe moviéndose) es m25.",
            "Un solo bien, sin sector externo (la versión abierta llega con Mundell-Fleming, m49).",
        ],
        ecuaciones=[
            Ecuacion("Y = \\frac{F + \\frac{b}{h}\\,\\frac{M}{P}}{A_c} \\;\\; \\wedge \\;\\; P = P^e + ds + \\lambda(Y-Y^*)",
                     "el sistema completo",
                     "dos ecuaciones, dos incógnitas (Y, P); sustituir P(Y) en la AD da una "
                     "cuadrática — el precio dentro de M/P hace al sistema no lineal."),
            Ecuacion("r = \\frac{k\\,Y - M/P}{h}", "la tasa implícita",
                     "el IS-LM sigue operando debajo: cada equilibrio AD-AS trae su tasa de "
                     "interés — los shocks de demanda ahora mueven (Y, P, r) a la vez."),
        ],
        intuicion=("Todo shock se lee con una pregunta: ¿movió la AD o la SRAS? Demanda "
                   "→ (Y, P) juntos y r según el instrumento; costos → (Y, P) opuestos "
                   "y el dilema de m19. La novedad respecto del nivel 3 es que nada es "
                   "postulado: detrás de la AD hay un IS-LM, detrás de la SRAS hay "
                   "contratos, y la LRAS espera al final del ajuste."),
        equilibrio=("Corto plazo: AD ∩ SRAS (raíz positiva de la cuadrática, exacta). "
                    "Largo plazo: AD ∩ LRAS, con P_LR cerrado. La brecha entre ambos "
                    "es exactamente lo que el ajuste de expectativas (m25) recorre."),
        limitaciones=[
            "Estático: muestra el fotograma de corto y el ancla de largo plazo, pero no la trayectoria entre ambos (m25).",
            "Trabaja en NIVELES de precios; la política moderna piensa en INFLACIÓN — la traducción es el aparato dinámico del nivel 8 (m52-m56).",
            "M exógena: con reglas de tasa (BCRP), la AD se redibuja desde IS-MP (m51).",
        ],
        evolucion=("m24 lo usa para revivir los 70 (estanflación con tablero completo) "
                   "y m25 lo pone en movimiento (Pe_{t+1} = P_t) para mostrar la "
                   "autocorrección — cerrando el arco que abrió el nivel 1: de la cruz "
                   "keynesiana al equilibrio clásico, pasando por todos los rezagos."),
    ),
    escenarios=[
        Escenario("expansion_fiscal", "dG = +50 partiendo del largo plazo",
                  {"dG": 50.0},
                  "Y sube pero MENOS que en IS-LM puro (los precios se comen parte) y "
                  "r sube por partida doble (ingreso y precios): brecha positiva que "
                  "m25 hará pagar.",
                  cadena=["↑dG", "AD → derecha", "sobre la SRAS: ↑Y y ↑P",
                          "↑P ⇒ ↓M/P ⇒ ↑r (doble freno)", "brecha positiva (m25 la cobrará)"]),
        Escenario("expansion_monetaria", "dM = +60",
                  {"dM": 60.0},
                  "a corto plazo el dinero NO es neutral: Y sube — compárese con el "
                  "mismo experimento en m22, donde solo movía precios.",
                  cadena=["↑dM", "AD → derecha", "↑Y y ↑P a corto plazo",
                          "NO neutral a CP (contraste con m22)"]),
        Escenario("shock_de_costos", "ds = +0.3 (petróleo/alimentos)",
                  {"ds": 0.3},
                  "estanflación en el aparato completo: Y cae, P sube y la r implícita "
                  "también se tensa — los 70 en una figura.",
                  cadena=["↑ds", "SRAS → arriba", "↑P con ↓Y (estanflación)",
                          "↑P ⇒ ↓M/P ⇒ r se tensa también"]),
        Escenario("enfriamiento", "contracción monetaria dM = −80",
                  {"dM": -80.0},
                  "la receta desinflacionaria: brecha negativa hoy a cambio de menos "
                  "presión de precios — el costo lo cuantifica el sacrificio de m14.",
                  cadena=["↓dM", "AD → izquierda", "↓P y ↓Y (brecha negativa)",
                          "desinflación pagada en producto (m14)"]),
    ],
    verificaciones=[
        Verificacion("la base descansa en el largo plazo (Y*, Pe)", _v_base_largo_plazo),
        Verificacion("residuos AD y SRAS < 1e-9 (cuadrática exacta)", _v_residuos),
        Verificacion("expansión fiscal: Y↑, P↑, r↑", _v_fiscal),
        Verificacion("dinero no neutral a corto plazo (vs m22)", _v_dinero_no_neutral_cp),
        Verificacion("shock de costos: estanflación", _v_oferta),
    ],
    notas="El fotograma completo: (Y, P, r) de una vez. La película del ajuste es m25.",
)
