"""simuladores/macro/modelos/nivel_05/m32_crecimiento_ak.py — crecimiento endógeno: el modelo AK (nivel 5).

  y = A·k  (α = 1: SIN rendimientos decrecientes)
  Δk/k = s·A − (n+δ) = γ  →  crecimiento CONSTANTE para siempre, sin k*.
El anti-Solow: aquí el ahorro SÍ compra crecimiento permanente y no hay
convergencia alguna. El precio: α=1 es un filo de navaja, y la evidencia
de convergencia condicional (m30) lo castiga.

Procedencia: Rebelo (1991, mención); la lectura del capital "amplio" con
externalidades viene de Romer (1986, mención) — conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _gamma(p):
    return p["s"] * p["A"] - (p["n"] + p["delta"])


def _tray(p, T=None, k0=None):
    T = int(round(T if T is not None else p["T"]))
    g = _gamma(p)
    t = np.arange(T + 1)
    return t, (k0 if k0 is not None else p["k0"]) * (1 + g) ** t


def _curvas(p):
    t, k = _tray(p)
    g = _gamma(p)
    # contraste: un Solow (α=0.33) con el mismo arranque, para ver el aplanamiento
    from modelos.nivel_05 import _solow
    A_solow = p["A"] * p["k0"] ** (1 - 0.33)          # mismo y inicial
    k_solow = _solow.trayectoria(p["k0"], p["s"], A_solow, 0.33, p["n"] + p["delta"], int(p["T"]))
    return {"lineas": {"AK: $k_t = k_0(1+\\gamma)^t$": (t, k, config.AZUL2),
                       "Solow ($\\alpha=0.33$) mismo arranque": (t, k_solow, config.GRIS)},
            "anotacion": (f"$\\gamma = sA - (n{{+}}\\delta) = {p['s']:.2f}\\times{p['A']:.2f} - "
                          f"{p['n'] + p['delta']:.2f} = {100 * g:.2f}\\%$\n"
                          "AK no se aplana jamás; Solow sí — esa es TODA la diferencia")}


def _resultados(p):
    g = _gamma(p)
    t, k = _tray(p)
    return {"γ = sA − (n+δ) (%)": 100 * g,
            "crecimiento en t=1 (%)": 100 * (k[1] / k[0] - 1),
            f"crecimiento en t={int(p['T'])} (%)": 100 * (k[-1] / k[-2] - 1),
            f"k en t={int(p['T'])}": float(k[-1]),
            "¿existe k*?": 0.0,
            "años para duplicar y": float(np.log(2) / np.log(1 + g)) if g > 0 else float("inf")}


def _ecuaciones_calibradas(p):
    g = _gamma(p)
    return [f"$y = {p['A']:.2f}\\,k$",
            f"$\\gamma = {p['s']:.2f} \\times {p['A']:.2f} - {p['n'] + p['delta']:.2f} = {100 * g:.2f}\\%$",
            f"$k_t = {p['k0']:.1f}\\,(1{'+' if g >= 0 else ''}{g:.4f})^t$"]


_P0 = {"s": 0.20, "A": 0.35, "n": 0.01, "delta": 0.05, "k0": 1.0, "T": 80.0}


def _v_crecimiento_constante():
    t, k = _tray(_P0, T=500)
    tasas = k[1:] / k[:-1] - 1
    g = _gamma(_P0)
    return bool(np.all(np.abs(tasas - g) < 1e-12)), (f"la tasa de crecimiento es EXACTAMENTE γ={100 * g:.2f}% "
                                                     "en todos los períodos: sin transición, sin freno")


def _v_ahorro_compra_crecimiento():
    g1, g2 = _gamma(_P0), _gamma(dict(_P0, s=0.30))
    return g2 > g1, (f"s: 0.20→0.30 sube γ de {100 * g1:.2f}% a {100 * g2:.2f}% PARA SIEMPRE: "
                     "el anti-Solow — aquí la política de ahorro sí mueve el crecimiento")


def _v_sin_convergencia():
    _, k_pobre = _tray(_P0, T=500, k0=1.0)
    _, k_rico = _tray(_P0, T=500, k0=8.0)
    razones = k_rico / k_pobre
    return bool(np.all(np.abs(razones - 8.0) < 1e-9)), ("el rico queda 8 veces arriba PARA SIEMPRE: "
                                                        "sin rendimientos decrecientes no hay ventaja del atraso")


def _v_decadencia():
    g = _gamma(dict(_P0, s=0.15))
    return g < 0, (f"con s=0.15, γ={100 * g:.2f}%<0: la economía se ENCOGE por siempre — "
                   "en AK no hay piso de equilibrio que te sostenga")


MODELO = Modelo(
    id="m32", nivel=5,
    nombre="Crecimiento endógeno (modelo AK)",
    xlabel="Período $t$", ylabel="Capital por trabajador ($k_t$)",
    parametros=[
        Parametro("s", _P0["s"], 0.05, 0.5, 0.01, "Tasa de ahorro s", grupo="conducta",
                  definicion="aquí SÍ compra crecimiento permanente"),
        Parametro("A", _P0["A"], 0.1, 0.6, 0.01, "Productividad A", grupo="tecnología",
                  definicion="rendimiento constante del capital amplio"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="filtraciones"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="filtraciones"),
        Parametro("k0", _P0["k0"], 0.5, 10.0, 0.5, "Capital inicial k0", grupo="historia"),
        Parametro("T", _P0["T"], 20, 150, 5, "Períodos simulados", grupo="historia"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Y si el capital NO tuviera rendimientos decrecientes — puede la acumulación sola sostener el crecimiento?",
        variables=[("k", "capital AMPLIO (físico+humano+conocimiento) — endógena"),
                   ("γ", "tasa de crecimiento — por fin ENDÓGENA (función de s)"),
                   ("k*", "no existe: el sistema nunca se detiene")],
        derivacion=["y = A\\,k \\;\\;(\\alpha = 1)",
                    "\\Delta k = s\\,A\\,k - (n+\\delta)\\,k",
                    "\\frac{\\Delta k}{k} = s\\,A - (n+\\delta) = \\gamma \\;\\;(constante)"],
        contexto=("El residuo de Solow (m29) dejó el crecimiento sin teoría: g caía "
                  "del cielo. La primera respuesta de la 'nueva teoría del "
                  "crecimiento' (años 80-90) fue quirúrgica: si el capital se "
                  "entiende AMPLIO — máquinas más conocimiento más capital humano, "
                  "con externalidades que compensan los rendimientos decrecientes "
                  "privados (Romer 1986) — entonces α efectivo puede ser 1, y la "
                  "acumulación misma sostiene el crecimiento sin maná exógeno "
                  "(Rebelo 1991). El modelo AK es esa idea en su esqueleto."),
        autores=("Rebelo (1991) como formulación canónica; Romer (1986, "
                 "externalidades del conocimiento) y Lucas (1988, capital humano) "
                 "como fundamento del capital 'amplio' — menciones."),
        supuestos=[
            "α = 1 EXACTO: el capital amplio no sufre rendimientos decrecientes (externalidades compensan) — el filo de navaja del modelo.",
            "s exógena (Rebelo la deriva de preferencias; aquí se hereda de Solow).",
            "Sin transición: el modelo vive permanentemente en su senda de crecimiento.",
        ],
        ecuaciones=[
            Ecuacion("y = A\\,k", "producción lineal en el capital amplio",
                     "duplicar el capital (máquinas + saberes + organización) duplica el producto: "
                     "las ideas que acompañan a las máquinas no se agotan."),
            Ecuacion("\\gamma = s\\,A - (n+\\delta)", "crecimiento endógeno",
                     "la tasa de crecimiento es una DECISIÓN social: más ahorro, mejor A "
                     "institucional, menos filtraciones — todo mueve γ permanentemente."),
        ],
        intuicion=("Solow y AK difieren en UNA letra (α<1 vs α=1) y en todo lo demás: "
                   "en Solow el ahorro compra nivel y la política de crecimiento es "
                   "impotente a largo plazo; en AK compra crecimiento y la política lo "
                   "es todo. La figura lo muestra: mismo arranque, Solow se aplana, AK "
                   "no — y a 80 períodos la diferencia es un mundo. La pregunta "
                   "empírica decisiva es cuál α describe al capital amplio."),
        equilibrio=("No hay k*: el 'equilibrio' es la propia senda exponencial "
                    "(verificado: γ exacto todos los períodos). Sin fuerza "
                    "estabilizadora, γ<0 significa decadencia perpetua — AK no tiene "
                    "piso ni techo."),
        limitaciones=[
            "Filo de navaja: con α=0.99 vuelve Solow (a largo plazo); con α=1.01 el crecimiento EXPLOTA — la linealidad exacta es increíblemente exigente.",
            "Predice CERO convergencia (ratio constante, verificado) — pero m30 documenta convergencia condicional: la evidencia favorece α<1.",
            "Efectos de escala incómodos en las versiones con ideas (países grandes crecerían más — Jones 1995, mención, lo refuta).",
        ],
        evolucion=("AK es el extremo puro; el término medio empíricamente viable es "
                   "m33 (capital humano: α+β≈2/3, convergencia lenta pero real). La "
                   "endogeneización seria del progreso técnico — ideas no rivales, "
                   "I+D con poder de mercado (Romer 1990, mención) — espera en el "
                   "nivel 8+."),
    ),
    escenarios=[
        Escenario("mas_ahorro_mas_crecimiento", "s: 0.20 → 0.30",
                  {"s": 0.30},
                  "γ salta de 1.0% a 4.5% PARA SIEMPRE: en AK la política de ahorro "
                  "es política de crecimiento — el anti-m26.",
                  cadena=["↑s", "más inversión en capital amplio", "sin rendimientos decrecientes que frenen",
                          "↑γ permanente", "el nivel Y la pendiente suben"]),
        Escenario("decadencia", "economía que ahorra poco (s = 0.15)",
                  {"s": 0.15},
                  "γ = −0.75%: se encoge por siempre — sin k* no hay red de "
                  "seguridad; el estancamiento es acumulativo.",
                  cadena=["s·A < n+δ", "la inversión no repone el capital amplio",
                          "γ < 0", "decadencia perpetua (sin piso de equilibrio)"]),
        Escenario("mejora_institucional", "A sube de 0.35 a 0.42 (instituciones, difusión)",
                  {"A": 0.42},
                  "γ pasa de 1.0% a 2.4%: en AK cualquier mejora de eficiencia es "
                  "crecimiento permanente, no un salto de nivel.",
                  cadena=["↑A", "cada unidad de capital amplio rinde más",
                          "↑γ = sA−(n+δ)", "crecimiento permanente (vs salto de nivel en m26)"]),
    ],
    verificaciones=[
        Verificacion("crecimiento exactamente constante (γ, sin freno)", _v_crecimiento_constante),
        Verificacion("el ahorro compra CRECIMIENTO (anti-Solow)", _v_ahorro_compra_crecimiento),
        Verificacion("cero convergencia: el ratio rico/pobre no se mueve", _v_sin_convergencia),
        Verificacion("sin piso: γ<0 es decadencia perpetua", _v_decadencia),
    ],
    notas="Una letra de diferencia con Solow (α=1) y otra filosofía de política: aquí el crecimiento se ELIGE.",
)
