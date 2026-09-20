"""simuladores/macro/modelos/nivel_05/m29_solow_tecnologia.py — Solow con progreso tecnológico (nivel 5).

A_t = A0·(1+g)^t  y variables por trabajador EFECTIVO:  k̃ = K/(A·L).
  Δk̃ = s·k̃^α − (n+g+δ)·k̃   →   k̃* = (s/(n+g+δ))^{1/(1−α)}
En la senda de crecimiento balanceado (BGP): k̃ constante, y el ingreso POR
TRABAJADOR crece a la tasa g PARA SIEMPRE — el crecimiento sostenido que la
acumulación sola (m26) no podía dar. El precio teórico: g es EXÓGENA (maná).

Procedencia: Solow con progreso técnico "labor-augmenting" (formulación
estándar de manuales; Uzawa sobre la forma requerida — mención) —
conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _ngd(p):
    return p["n"] + p["g"] + p["delta"]


def _simular(p, T=None):
    """Devuelve t, y_t (ingreso por trabajador) y k̃_t (por trabajador efectivo)."""
    T = int(round(T if T is not None else p["T"]))
    kt = _solow.trayectoria(p["k0_frac"] * _solow.k_estrella(p["s"], 1.0, p["alpha"], _ngd(p)),
                            p["s"], 1.0, p["alpha"], _ngd(p), T)
    t = np.arange(T + 1)
    A = p["A0"] * (1 + p["g"]) ** t
    y = A * kt ** p["alpha"]            # y por trabajador = A·k̃^α
    return t, y, kt


def _curvas(p):
    t, y, kt = _simular(p)
    ks = _solow.k_estrella(p["s"], 1.0, p["alpha"], _ngd(p))
    y_bgp = p["A0"] * (1 + p["g"]) ** t * ks ** p["alpha"]
    return {"lineas": {"ingreso por trabajador $y_t$": (t, y, config.AZUL2),
                       "senda balanceada (BGP)": (t, y_bgp, config.GRIS)},
            "anotacion": (f"$\\tilde{{k}}^* = {ks:.2f}$ (por trabajador efectivo)\n"
                          f"en la BGP, $y$ crece a $g = {100 * p['g']:.1f}\\%$ por período\n"
                          "sin fin: la tecnología no tiene rendimientos decrecientes")}


def _resultados(p):
    t, y, kt = _simular(p, T=max(200, int(p["T"])))
    g_final = y[-1] / y[-2] - 1
    ks = _solow.k_estrella(p["s"], 1.0, p["alpha"], _ngd(p))
    return {"k̃* (por trabajador efectivo)": ks,
            "crecimiento de y al final (%)": 100 * g_final,
            "g del progreso técnico (%)": 100 * p["g"],
            f"y por trabajador en t={int(p['T'])}": float(_simular(p)[1][-1]),
            "y* efectivo (k̃*^α)": ks ** p["alpha"]}


_P0 = {"s": 0.20, "alpha": 0.33, "n": 0.01, "g": 0.02, "delta": 0.05,
       "A0": 1.0, "k0_frac": 0.5, "T": 80.0}


def _v_bgp():
    _, y, _ = _simular(_P0, T=3000)
    g_sim = y[-1] / y[-2] - 1
    return abs(g_sim - _P0["g"]) < 1e-6, (f"en la BGP el ingreso POR TRABAJADOR crece exactamente a "
                                          f"g = {100 * _P0['g']:.1f}%: crecimiento sostenido, por fin")


def _v_ktilde_constante():
    ngd = _ngd(_P0)
    ks = _solow.k_estrella(_P0["s"], 1.0, _P0["alpha"], ngd)
    kt = _solow.trayectoria(ks, _P0["s"], 1.0, _P0["alpha"], ngd, 100)
    return bool(np.all(np.abs(kt - ks) < 1e-12)), ("k̃ por trabajador EFECTIVO queda constante en la BGP: "
                                                   "todo lo per cápita crece a g, lo efectivo no")


def _v_ahorro_sigue_sin_dar_crecimiento():
    p2 = dict(_P0, s=0.35)
    _, y1, _ = _simular(_P0, T=3000)
    _, y2, _ = _simular(p2, T=3000)
    g1, g2 = y1[-1] / y1[-2] - 1, y2[-1] / y2[-2] - 1
    ok = abs(g1 - g2) < 1e-6 and y2[-1] > y1[-1]
    return ok, ("con s=0.35 el NIVEL de la senda sube pero el crecimiento sigue siendo g: "
                "ni con tecnología el ahorro compra crecimiento — solo g lo hace")


def _v_solo_g_mueve_crecimiento():
    p2 = dict(_P0, g=0.04)
    _, y2, _ = _simular(p2, T=3000)
    g2 = y2[-1] / y2[-2] - 1
    return abs(g2 - 0.04) < 1e-6, ("duplicar g duplica el crecimiento de largo plazo: TODO el "
                                   "crecimiento sostenido viene del progreso técnico — el 'residuo' manda")


MODELO = Modelo(
    id="m29", nivel=5,
    nombre="Solow con progreso tecnológico",
    xlabel="Período $t$", ylabel="Ingreso por trabajador ($y_t$)",
    parametros=[
        Parametro("g", _P0["g"], 0.0, 0.05, 0.005, "Progreso técnico g", grupo="tecnología",
                  definicion="crecimiento de la eficiencia del trabajo (exógeno: 'maná')"),
        Parametro("s", _P0["s"], 0.05, 0.6, 0.01, "Tasa de ahorro s", grupo="conducta",
                  definicion="mueve el NIVEL de la senda, no su pendiente"),
        Parametro("k0_frac", _P0["k0_frac"], 0.1, 1.5, 0.05, "Partida (fracción de k̃*)", grupo="condiciones"),
        Parametro("T", _P0["T"], 30, 150, 5, "Períodos simulados", grupo="condiciones"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α", grupo="tecnología"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="filtraciones"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="filtraciones"),
        Parametro("A0", _P0["A0"], 0.5, 2.0, 0.05, "Tecnología inicial A0", grupo="tecnología"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿De dónde sale el crecimiento que no se apaga — y por qué 'de la tecnología' es una respuesta incómoda?",
        variables=[("k̃ = K/(A·L)", "capital por trabajador efectivo — endógena, converge"),
                   ("y = A·k̃^α", "ingreso por trabajador — crece a g en la BGP"),
                   ("g", "progreso técnico — EXÓGENO (la confesión del modelo)")],
        derivacion=["\\tilde{k} = \\frac{K}{A\\,L}, \\quad A_t = A_0(1+g)^t",
                    "\\Delta\\tilde{k} = s\\,\\tilde{k}^{\\alpha} - (n+g+\\delta)\\,\\tilde{k}",
                    "\\tilde{k}^* = \\Big(\\frac{s}{n+g+\\delta}\\Big)^{1/(1-\\alpha)} \\;\\Rightarrow\\; y_t = A_t\\,\\tilde{k}^{*\\alpha} \\propto (1+g)^t"],
        contexto=("m26 terminó en un problema: sin progreso técnico, el crecimiento "
                  "per cápita se apaga — pero llevamos dos siglos creciendo. La "
                  "salida de Solow fue tan potente como humilde: dejar que la "
                  "eficiencia del trabajo crezca a una tasa g exógena. El modelo "
                  "recupera el crecimiento sostenido y entrega su resultado más "
                  "célebre por la puerta de atrás: al medir (Solow 1957), el capital "
                  "explica poco — el grueso es el 'residuo', ese g que el modelo NO "
                  "explica. La teoría del crecimiento moderna es la disputa por "
                  "endogeneizar ese residuo (m32-m33)."),
        autores=("Solow (1956, 1957 — menciones); la forma 'labor-augmenting' como "
                 "requisito de la senda balanceada es de Uzawa (1961, mención)."),
        supuestos=["Progreso técnico EXÓGENO a tasa g constante: cae del cielo, nadie lo produce ni lo paga.",
                   "Aumenta la eficiencia del TRABAJO (A·L): la única forma compatible con una BGP (Uzawa).",
                   "Los demás de m26, releídos por trabajador efectivo (filtración total: n+g+δ)."],
        ecuaciones=[
            Ecuacion("y_t = A_t\\,\\tilde{k}_t^{\\alpha}", "producción con tecnología creciente",
                     "la misma Cobb-Douglas, pero el 'trabajador efectivo' A·L mejora cada año: "
                     "el mismo k rinde más."),
            Ecuacion("\\Delta\\tilde{k} = s\\,\\tilde{k}^{\\alpha} - (n+g+\\delta)\\,\\tilde{k}",
                     "acumulación efectiva",
                     "g entra como TERCERA filtración: el capital debe crecer también para equipar "
                     "la tecnología nueva, no solo a los trabajadores nuevos."),
            Ecuacion("\\frac{\\Delta y}{y}\\Big|_{BGP} = g", "senda de crecimiento balanceada",
                     "en el largo plazo TODO lo per cápita (y, k, c, salarios) crece a g: la tasa "
                     "de crecimiento de una economía madura ES su progreso técnico."),
        ],
        intuicion=("La tecnología escapa de los rendimientos decrecientes porque no es "
                   "un factor que se acumula: es la VARA con que se miden los demás. "
                   "Por eso g puede sostener lo que s no: ahorrar más es subir un "
                   "escalón (nivel); mejorar tecnología es subir la escalera mecánica "
                   "(pendiente). La política de crecimiento se reordena: todo lo que "
                   "mueve s (impuestos, pensiones) cambia niveles; solo lo que mueve g "
                   "(innovación, educación, instituciones) cambia destinos."),
        equilibrio=("k̃* estable (misma lógica de m26 con n+g+δ); la BGP es el "
                    "equilibrio EN MOVIMIENTO: crecimiento constante a g, verificado "
                    "con precisión 1e-6."),
        limitaciones=[
            "g exógeno es una confesión, no una teoría: el modelo explica todo MENOS la fuente del crecimiento.",
            "El residuo de Solow mezcla tecnología, instituciones, errores de medición: 'a measure of our ignorance' (Abramovitz, mención).",
            "Sin difusión: cada país tiene 'su' g — pero la tecnología cruza fronteras (m30 usará esto).",
        ],
        evolucion=("El vacío de g exógeno abre la agenda moderna: m32 (AK) elimina los "
                   "rendimientos decrecientes para que la acumulación misma genere g; "
                   "m33 mete capital humano (educación produce eficiencia); Romer "
                   "endogeneiza las ideas (mención, nivel 8+). Y m30 pregunta qué pasa "
                   "cuando países con el mismo g parten de distinto k̃."),
    ),
    escenarios=[
        Escenario("motor_encendido", "g = 2% con partida al 50% de k̃*",
                  {"g": 0.02},
                  "transición rápida al principio (efecto m27) que se funde con el "
                  "crecimiento perpetuo a g: la anatomía de una economía sana.",
                  cadena=["k̃ < k̃*", "transición: crecimiento extra transitorio",
                          "k̃ → k̃*", "queda solo la escalera mecánica", "y crece a g por siempre"]),
        Escenario("mas_ahorro_mismo_destino", "s: 0.20 → 0.35 con el mismo g",
                  {"s": 0.35},
                  "la senda SALTA de nivel pero su pendiente no cambia: ni con "
                  "tecnología el ahorro compra crecimiento de largo plazo.",
                  cadena=["↑s", "k̃* mayor", "la senda BGP se desplaza hacia arriba",
                          "la PENDIENTE sigue siendo g", "nivel sí, crecimiento no"]),
        Escenario("apagon_tecnologico", "g cae a 0 (estancamiento secular)",
                  {"g": 0.0},
                  "de vuelta al Solow básico: la economía converge y se detiene — el "
                  "miedo del 'estancamiento secular' es, en este lenguaje, un g≈0.",
                  cadena=["g → 0", "la escalera mecánica se detiene",
                          "solo queda la transición", "y converge a un techo", "crecimiento 0"]),
        Escenario("milagro_tecnologico", "g salta a 4% (revolución industrial/digital)",
                  {"g": 0.04},
                  "duplicar g duplica el crecimiento PERMANENTE: ningún otro parámetro "
                  "del laboratorio tiene ese poder.",
                  cadena=["↑g", "la vara A mejora más rápido", "todas las variables per cápita",
                          "aceleran a la nueva g", "el único almuerzo que se sirve eterno"]),
    ],
    verificaciones=[
        Verificacion("en la BGP, y crece exactamente a g", _v_bgp),
        Verificacion("k̃ efectivo constante en la BGP", _v_ktilde_constante),
        Verificacion("s mueve el nivel de la senda, no su pendiente", _v_ahorro_sigue_sin_dar_crecimiento),
        Verificacion("solo g mueve el crecimiento de largo plazo", _v_solo_g_mueve_crecimiento),
    ],
    notas="El ahorro sube escalones; la tecnología es la escalera mecánica. El residuo manda — y sigue sin teoría (m32-m33).",
)
