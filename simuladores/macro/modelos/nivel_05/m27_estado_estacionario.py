"""simuladores/macro/modelos/nivel_05/m27_estado_estacionario.py — la transición hacia el estado estacionario (nivel 5).

El diagrama de m26 dice A DÓNDE va la economía; este modelo dice CÓMO y
CUÁN RÁPIDO: trayectorias k_t desde distintos puntos de partida y la
velocidad de convergencia λ ≈ (1−α)(n+δ) — verificable contra la semivida
simulada. Es la física del "largo plazo": ¿cuántos AÑOS son?

Procedencia: dinámica de transición estándar del modelo de Solow (manuales
de crecimiento) — conocimiento general; λ por linealización: resultado
estándar (matemática elemental).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _ngd(p):
    return p["n"] + p["delta"]


def _curvas(p):
    ngd = _ngd(p)
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], ngd)
    T = int(round(p["T"]))
    t = np.arange(T + 1)
    k_pobre = _solow.trayectoria(p["k0_frac"] * ks, p["s"], p["A"], p["alpha"], ngd, T)
    k_rico = _solow.trayectoria(1.8 * ks, p["s"], p["A"], p["alpha"], ngd, T)
    lam = _solow.velocidad(p["alpha"], ngd)
    return {"lineas": {"desde abajo ($k_0 < k^*$)": (t, k_pobre, config.AZUL2),
                       "desde arriba ($k_0 > k^*$)": (t, k_rico, config.ROJO),
                       "$k^*$": (t, np.full(T + 1, ks), config.GRIS)},
            "anotacion": (f"$k^* = {ks:.2f}$\n"
                          f"$\\lambda \\approx (1-\\alpha)(n+\\delta) = {lam:.3f}$\n"
                          f"semivida $\\approx \\ln 2/\\lambda = {np.log(2) / lam:.0f}$ períodos")}


def _resultados(p):
    ngd = _ngd(p)
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], ngd)
    lam = _solow.velocidad(p["alpha"], ngd)
    k = _solow.trayectoria(p["k0_frac"] * ks, p["s"], p["A"], p["alpha"], ngd, int(p["T"]))
    return {"k*": ks, "y*": _solow.f(ks, p["A"], p["alpha"]),
            "velocidad λ = (1−α)(n+δ)": lam,
            "semivida teórica (períodos)": float(np.log(2) / lam),
            f"k tras {int(p['T'])} períodos (desde {p['k0_frac']:.0%} de k*)": float(k[-1]),
            "brecha restante (%)": float(100 * (ks - k[-1]) / ks)}


_P0 = {"s": 0.20, "A": 1.0, "alpha": 0.33, "n": 0.01, "delta": 0.05,
       "k0_frac": 0.3, "T": 60.0}


def _v_semivida():
    ngd = _ngd(_P0)
    ks = _solow.k_estrella(_P0["s"], _P0["A"], _P0["alpha"], ngd)
    k0 = 0.9 * ks                       # cerca de k*: vale la linealización
    k = _solow.trayectoria(k0, _P0["s"], _P0["A"], _P0["alpha"], ngd, 400)
    brecha = np.abs(ks - k)
    idx = int(np.argmax(brecha <= brecha[0] / 2))
    teo = np.log(2) / _solow.velocidad(_P0["alpha"], ngd)
    ok = abs(idx - teo) / teo < 0.15
    return ok, f"semivida simulada ({idx} períodos) ≈ teórica ln2/λ ({teo:.1f}): la linealización manda"


def _v_lento():
    lam = _solow.velocidad(_P0["alpha"], _ngd(_P0))
    return np.log(2) / lam > 10, (f"con α=1/3 y (n+δ)=6%, la semivida es ~{np.log(2) / lam:.0f} "
                                  "períodos: el 'largo plazo' se mide en DÉCADAS")


def _v_mas_alpha_mas_lento():
    l1 = _solow.velocidad(0.33, _ngd(_P0))
    l2 = _solow.velocidad(0.6, _ngd(_P0))
    return l2 < l1, (f"con α=0.6 (capital amplio, incluye humano) λ cae de {l1:.3f} a {l2:.3f}: "
                     "más capital acumulable = convergencia más lenta (clave para m33)")


def _v_monotonia():
    ngd = _ngd(_P0)
    ks = _solow.k_estrella(_P0["s"], _P0["A"], _P0["alpha"], ngd)
    k = _solow.trayectoria(0.3 * ks, _P0["s"], _P0["A"], _P0["alpha"], ngd, 300)
    ok = bool(np.all(np.diff(k) > -1e-12)) and bool(np.all(k <= ks + 1e-9))
    return ok, "desde abajo, k_t sube SIN sobrepasar k*: transición monótona (sin ciclos)"


MODELO = Modelo(
    id="m27", nivel=5,
    nombre="Estado estacionario y transición",
    xlabel="Período $t$", ylabel="Capital por trabajador ($k_t$)",
    parametros=[
        Parametro("k0_frac", _P0["k0_frac"], 0.05, 0.95, 0.05, "Punto de partida (fracción de k*)"),
        Parametro("T", _P0["T"], 20, 150, 5, "Períodos simulados"),
        Parametro("s", _P0["s"], 0.05, 0.6, 0.01, "Tasa de ahorro s"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.6, 0.01, "Participación del capital α"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ"),
        Parametro("A", _P0["A"], 0.5, 2.0, 0.05, "Productividad A"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Cuántos años dura el 'largo plazo' — y de qué depende esa velocidad?",
        variables=[("k_t", "trayectoria del capital — endógena"),
                   ("k*", "destino — función de (s, A, α, n, δ)"),
                   ("λ", "velocidad de convergencia — resultado, no supuesto")],
        derivacion=["\\Delta k \\approx -\\lambda\\,(k - k^*) \\;\\;(linealización\\;en\\;k^*)",
                    "\\lambda = (1-\\alpha)\\,(n+\\delta)",
                    "semivida = \\ln 2 / \\lambda"],
        contexto=("El diagrama de m26 es atemporal; la política y la vida no. Si un "
                  "país reforma hoy (sube s, mejora A), ¿cuándo se nota? La respuesta "
                  "de Solow es incómoda: con parámetros realistas, la mitad del camino "
                  "toma más de una década — el 'largo plazo' keynesiano de m25 eran "
                  "trimestres; el de Solow son generaciones. Esa diferencia de relojes "
                  "organiza toda la macroeconomía aplicada."),
        autores=("Dinámica de transición del modelo de Solow (1956); la velocidad de "
                 "convergencia como objeto empírico es de la literatura de los 90 "
                 "(Barro, Sala-i-Martin — mención: ~2% anual)."),
        supuestos=["Los de m26 (rendimientos decrecientes, s exógena).",
                   "λ es una aproximación LOCAL (linealización): lejos de k* la velocidad real difiere.",
                   "Parámetros constantes durante toda la transición (décadas): heroico y explícito."],
        ecuaciones=[
            Ecuacion("\\lambda \\approx (1-\\alpha)\\,(n+\\delta)", "velocidad de convergencia",
                     "manda (1−α): si el capital pesa poco (α chico), sus rendimientos decrecen "
                     "rápido y la brecha se cierra rápido; con capital 'amplio' (α grande), lento."),
            Ecuacion("t_{1/2} = \\ln 2 / \\lambda", "semivida de la brecha",
                     "con α=1/3 y n+δ=6%: λ=0.04 → ~17 períodos para cerrar la mitad. La "
                     "evidencia empírica (≈2% anual) sugiere α EFECTIVO mayor: pista de m33."),
        ],
        intuicion=("La velocidad no la eligen los gobiernos: la fija la curvatura de la "
                   "tecnología. Un país lejos de su k* crece rápido 'gratis' "
                   "(rendimientos altos del capital escaso) y se frena al acercarse — "
                   "el patrón exacto de Japón, Corea o China. Cuando un milagro se "
                   "desacelera, Solow pregunta: ¿se agotó la transición o cayó A?"),
        equilibrio=("k* atrae monótonamente (sin ciclos ni sobreimpulso, verificado): "
                    "la transición de Solow es un deslizamiento suave, no una "
                    "oscilación — contraste con la dinámica keynesiana de m25."),
        limitaciones=[
            "λ empírica (~2%/año) es MENOR que la que predice α=1/3 (~4%): o el capital es más amplio (humano, m33) o hay otras fricciones.",
            "La linealización engaña lejos de k*: países muy pobres no crecen tan rápido como predice (m31 da una razón).",
            "Transición con parámetros fijos por décadas: las reformas reales cambian s y A por el camino.",
        ],
        evolucion=("La velocidad de convergencia es el puente hacia m30 (¿convergen "
                   "los países?) y la anomalía que motiva m33 (capital humano hace α "
                   "efectivo ≈ 2/3 y ralentiza λ hasta lo observado). m28 usa este "
                   "mismo aparato para preguntar cuánto ahorro es óptimo."),
    ),
    escenarios=[
        Escenario("despegue", "economía a 30% de su k* (posguerra, reformas)",
                  {"k0_frac": 0.3},
                  "crecimiento inicial rápido que se apaga solo: el patrón de los "
                  "'milagros' asiáticos leído como transición.",
                  cadena=["k lejos de k*", "rendimiento del capital alto", "crecimiento rápido",
                          "rendimientos decrecientes muerden", "desaceleración endógena", "k*"]),
        Escenario("capital_amplio", "α = 0.6 (capital físico + humano)",
                  {"alpha": 0.6},
                  "λ cae a 0.024 y la semivida sube a ~29 períodos: con capital amplio "
                  "la convergencia observada (~2% anual) por fin cuadra — m33.",
                  cadena=["↑α", "los rendimientos decrecen más despacio", "↓λ",
                          "transiciones de generaciones", "la evidencia empírica encaja"]),
        Escenario("demografia_rapida", "n = 0.03 acelera el reloj",
                  {"n": 0.03},
                  "paradoja de la velocidad: más dilución (n+δ) acerca k* — pero a un "
                  "k* MÁS POBRE. Converger rápido a poco no es buena noticia.",
                  cadena=["↑n", "↑λ = (1−α)(n+δ)", "semivida menor",
                          "pero k* cae (m26)", "rápido hacia un destino peor"]),
    ],
    verificaciones=[
        Verificacion("semivida simulada = ln2/λ (linealización)", _v_semivida),
        Verificacion("el largo plazo se mide en décadas", _v_lento),
        Verificacion("más α ⇒ convergencia más lenta", _v_mas_alpha_mas_lento),
        Verificacion("transición monótona sin sobreimpulso", _v_monotonia),
    ],
    notas="El reloj del crecimiento: λ=(1−α)(n+δ). La macro de corto plazo vive DENTRO de una transición de Solow.",
)
