"""simuladores/macro/modelos/nivel_09/m64_dinamica_deuda_pib.py — dinámica deuda/PIB (nivel 9, ANCLA).

La ecuación central de la macroeconomía fiscal: dividir m63 por el PIB
(que crece a g) introduce el término que decide todo:
  b_{t+1} = b_t·(1+r)/(1+g) − sp     [b: deuda/PIB; sp: primario/PIB]
  Δb ≈ b·(r−g) − sp
Si r > g: la bola de nieve sobrevive en ratios — estabilizar exige superávit
  sp* = b·(r−g)/(1+g)   (exacto, verificado)
Si g > r: la aritmética AMABLE — el crecimiento licúa; se puede sostener
déficit primario moderado con deuda estable. La carrera (r vs g) es el
corazón de todo debate fiscal — incluido el peruano (m108, con datos MEF).

Procedencia: ecuación estándar de dinámica de deuda (análisis de
sostenibilidad del FMI, mención) — conocimiento general; calibración
didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _senda(p, T=None, sp=None):
    T = int(round(T if T is not None else p["T"]))
    sp = p["sp"] if sp is None else sp
    factor = (1 + p["r"] / 100) / (1 + p["g"] / 100)
    b = np.empty(T + 1)
    b[0] = p["b0"]
    for t in range(T):
        b[t + 1] = factor * b[t] - sp
    return np.arange(T + 1), b


def _sp_estrella(p, b=None):
    b = p["b0"] if b is None else b
    return b * (p["r"] / 100 - p["g"] / 100) / (1 + p["g"] / 100)


def _curvas(p):
    t, b = _senda(p)
    sp_e = _sp_estrella(p)
    return {"lineas": {"deuda/PIB $b_t$": (t, b, config.ROJO),
                       "nivel inicial $b_0$": (t, np.full(len(t), p["b0"]), config.GRIS)},
            "anotacion": (f"$\\Delta b \\approx b\\,(r-g) - sp$ con $r-g = "
                          f"{p['r'] - p['g']:+.1f}$ pp\n"
                          f"$sp^*$ que congela $= {sp_e:+.2f}\\%$ del PIB "
                          f"(tu $sp = {p['sp']:+.1f}$)\n"
                          + ("aritmética CRUEL: r>g — la bola vive en ratios"
                             if p["r"] > p["g"] else
                             "aritmética AMABLE: g>r — el crecimiento licúa"))}


def _resultados(p):
    t, b = _senda(p)
    return {"deuda/PIB final (%)": float(b[-1]),
            "Δb del primer año (pp)": float(b[1] - b[0]),
            "sp* que congela b0 (% PIB)": _sp_estrella(p),
            "r − g (la carrera, pp)": p["r"] - p["g"],
            "brecha de esfuerzo sp*−sp": _sp_estrella(p) - p["sp"]}


def _ecuaciones_calibradas(p):
    factor = (1 + p["r"] / 100) / (1 + p["g"] / 100)
    return [f"$b_{{t+1}} = \\frac{{1+{p['r'] / 100:.2f}}}{{1+{p['g'] / 100:.2f}}}\\,b_t - "
            f"{p['sp']:.1f} = {factor:.4f}\\,b_t - {p['sp']:.1f}$",
            f"$sp^* = {p['b0']:.0f} \\times \\frac{{{(p['r'] - p['g']) / 100:.3f}}}"
            f"{{{1 + p['g'] / 100:.2f}}} = {_sp_estrella(p):+.2f}$"]


_P0 = {"b0": 50.0, "r": 5.0, "g": 3.0, "sp": 0.0, "T": 30.0}


def _v_recursion():
    t, b = _senda(_P0)
    factor = (1 + _P0["r"] / 100) / (1 + _P0["g"] / 100)
    res = np.max(np.abs(b[1:] - (factor * b[:-1] - _P0["sp"])))
    return res < 1e-9, f"la recursión deuda/PIB se cumple exacta (residuo {res:.1e})"


def _v_congela():
    sp_e = _sp_estrella(_P0)
    t, b = _senda(dict(_P0, sp=sp_e), T=100)
    return bool(np.all(np.abs(b - _P0["b0"]) < 1e-6)), \
        (f"sp* = b(r−g)/(1+g) = {sp_e:.3f}% congela el ratio EXACTAMENTE: la fórmula "
         "que todo ministerio de finanzas recalcula cada año")


def _v_aritmetica_amable():
    p = dict(_P0, g=6.0)
    t, b = _senda(p, T=100)
    ok = bool(np.all(np.diff(b) < 1e-12)) and float(b[-1]) < p["b0"]
    return ok, (f"con g=6%>r=5% y primario CERO, b cae sola de 50 a {float(b[-1]):.1f}%: "
                "el crecimiento licúa — la salida de deuda más barata de la historia")


def _v_esfuerzo_escala_con_b():
    sp1 = _sp_estrella(_P0)
    sp2 = _sp_estrella(_P0, b=2 * _P0["b0"])
    return abs(sp2 - 2 * sp1) < 1e-12, \
        (f"duplicar b duplica el sp* requerido ({sp1:.2f}→{sp2:.2f}): cuanto más se "
         "espera, más cuesta — el argumento del ajuste temprano")


MODELO = Modelo(
    id="m64", nivel=9,
    nombre="Dinámica deuda/PIB",
    xlabel="Año $t$", ylabel="Deuda/PIB $b_t$ (%)",
    parametros=[
        Parametro("sp", _P0["sp"], -4, 4, 0.25, "Primario sp (% del PIB)", grupo="decisión",
                  definicion="la perilla de control, ahora en ratios"),
        Parametro("r", _P0["r"], 1, 10, 0.25, "Tasa real r (%)", grupo="la carrera",
                  definicion="lo que cobra el mercado (m48: incluye prima)"),
        Parametro("g", _P0["g"], 0, 8, 0.25, "Crecimiento g (%)", grupo="la carrera",
                  definicion="el gran licuador (m26-m29)"),
        Parametro("b0", _P0["b0"], 10, 150, 5, "Deuda/PIB inicial b0 (%)", grupo="herencia"),
        Parametro("T", _P0["T"], 10, 60, 5, "Años simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuándo puede un país convivir con déficits — y cuándo la deuda lo persigue aunque ajuste? La resta r−g decide.",
        variables=[("b = B/Y", "deuda/PIB — LA métrica fiscal (los niveles engañan)"),
                   ("r − g", "la carrera — tasa contra crecimiento: el signo lo es todo"),
                   ("sp*", "el primario que congela — el número que persigue a los ministros")],
        derivacion=["B_{t+1} = (1+r)B_t - SP \\;\\;(m63)",
                    "dividir\\;por\\;Y_{t+1} = (1+g)Y_t:",
                    "b_{t+1} = \\frac{1+r}{1+g}\\,b_t - sp \\;\\;\\Rightarrow\\;\\; \\Delta b \\approx b(r-g) - sp"],
        contexto=("Dividir la bola de nieve de m63 por el PIB cambia la pregunta y "
                  "a veces la respuesta: lo que importa no es cuánto se debe sino "
                  "cuánto se debe RESPECTO de lo que se produce — y el denominador "
                  "crece. La resta r−g organiza dos mundos: las posguerras y los "
                  "booms (g>r) licúan deudas gigantes sin ajuste; los años de tasas "
                  "altas y estancamiento (r>g) convierten deudas modestas en "
                  "persecuciones. El debate Blanchard (2019, mención: ¿y si r<g es "
                  "lo normal?) y toda regla fiscal — la peruana incluida (mención; "
                  "m108 con datos MEF) — viven dentro de esta ecuación."),
        autores=("Ecuación estándar del análisis de sostenibilidad (DSA del FMI, "
                 "mención); la relectura moderna de r<g: Blanchard (2019, AEA "
                 "presidential address, mención)."),
        supuestos=[
            "r y g constantes y EXÓGENOS: en la realidad pelean entre sí (el ajuste puede bajar g, el riesgo puede subir r — m65 y m69).",
            "sp constante: la política real es contingente (m68); aquí se aísla la aritmética.",
            "Deuda en moneda propia a tasa única: la deuda en dólares cambia el juego (r incluye depreciación — m84, m110).",
        ],
        ecuaciones=[
            Ecuacion("\\Delta b \\approx b\\,(r-g) - sp", "la ecuación central",
                     "tres términos y toda la política fiscal: la herencia (b) multiplicada por "
                     "la carrera (r−g), contra el esfuerzo (sp)."),
            Ecuacion("sp^* = \\frac{b\\,(r-g)}{1+g}", "el primario que congela",
                     "exacto (verificado): con r−g=2pp y b=50%, basta 0.97% del PIB; con b=100%, "
                     "el doble — la deuda alta encarece su propia estabilización."),
        ],
        intuicion=("La deuda/PIB es una bañera con dos grifos y un desagüe: r llena "
                   "(intereses), g vacía (el denominador crece) y sp es la mano en "
                   "el desagüe. Cuando g>r, la bañera se vacía sola y hasta se "
                   "puede dejar un grifo abierto (déficit primario permanente "
                   "sostenible). Cuando r>g, no hay descanso: cada punto de deuda "
                   "exige esfuerzo perpetuo. Por eso las dos preguntas previas a "
                   "todo plan fiscal son ajenas al fisco: ¿cuánto crecerá el país "
                   "(m26-m29)? ¿cuánto cobrará el mercado (m48)?"),
        equilibrio=("b constante sii sp = sp* (verificado exacto). Con r>g el "
                    "equilibrio es INESTABLE hacia arriba (b mayor exige sp mayor: "
                    "la persecución); con g>r es estable — los déficits moderados "
                    "convergen a un b* finito."),
        limitaciones=[
            "r−g no es un parámetro sino un campo de batalla: el propio nivel de b puede subir r (prima, m48/m76) y el ajuste puede bajar g (m69) — los círculos viciosos viven fuera de esta linealidad.",
            "El PIB como denominador esconde composición: deuda en dólares con PIB en soles es otra aritmética (m84).",
            "Sin límite político: sp* puede ser aritméticamente claro e institucionalmente imposible — esa brecha es m65.",
        ],
        evolucion=("Es LA ecuación del nivel: m65 la convierte en diagnóstico "
                   "(¿el sp* requerido es factible?), m69 la usa para la paradoja "
                   "de la austeridad (el denominador contraataca), y m108 la "
                   "alimentará con la deuda peruana real (MEF/BCRP) — donde la "
                   "regla fiscal (mención) es un sp* institucionalizado."),
    ),
    escenarios=[
        Escenario("aritmetica_cruel", "r=5% > g=3% con primario cero",
                  {"sp": 0.0},
                  "b sube de 50% a 89% en 30 años sin ningún déficit primario: la "
                  "bola de nieve sobrevive a la división por el PIB cuando r>g.",
                  cadena=["r > g", "los intereses corren más que el denominador",
                          "Δb = b(r−g) > 0 con sp=0", "el ratio crece solo",
                          "sp* positivo y creciente: la persecución"]),
        Escenario("aritmetica_amable", "el crecimiento gana: g=6% > r=5%",
                  {"g": 6.0},
                  "con primario CERO, b cae sola de 50% a 38%: así licuaron sus "
                  "deudas las posguerras — y así ayudó el boom peruano de los 2000 "
                  "(mención; m108 lo medirá).",
                  cadena=["g > r", "el denominador corre más que los intereses",
                          "Δb < 0 sin esfuerzo", "la deuda se licúa creciendo",
                          "la mejor política fiscal es el crecimiento (m26)"]),
        Escenario("consolidacion", "superávit primario de 1.5% del PIB",
                  {"sp": 1.5},
                  "b cae a 24%: el esfuerzo sostenido vence a la aritmética cruel — "
                  "1.5% del PIB cada año, la diferencia entre 89% y 24%.",
                  cadena=["sp > sp*", "el esfuerzo supera a la carrera",
                          "Δb < 0 año tras año", "b desciende — y el sp* requerido baja con ella"]),
        Escenario("punto_exacto", "el primario que congela: sp = sp*",
                  {"sp": 0.9708737864077669},
                  "la línea plana perfecta: b clavada en 50% — la fórmula "
                  "sp*=b(r−g)/(1+g) verificada en vivo.",
                  cadena=["sp = b(r−g)/(1+g)", "esfuerzo = carrera exactamente",
                          "Δb = 0 para siempre", "el statu quo tiene precio de lista"]),
    ],
    verificaciones=[
        Verificacion("recursión deuda/PIB exacta", _v_recursion),
        Verificacion("sp* congela el ratio exactamente", _v_congela),
        Verificacion("g>r con primario cero: la deuda se licúa sola", _v_aritmetica_amable),
        Verificacion("el esfuerzo requerido escala con b (ajuste temprano)", _v_esfuerzo_escala_con_b),
    ],
    notas="La bañera fiscal: r llena, g vacía, sp es la mano en el desagüe. El signo de r−g organiza el mundo.",
)
