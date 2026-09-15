"""simuladores/macro/modelos/nivel_06/m40_metas_inflacion.py — inflación objetivo: el ancla nominal moderna (nivel 6).

Un régimen de metas ancla las expectativas: cada período, la inflación es
jalada hacia la meta con fuerza θ (el ANCLAJE, resultado de credibilidad):
  π_{t+1} = π* + (1−θ)(π_t − π*)
Con θ alto los desvíos mueren rápido (semivida = ln2/−ln(1−θ)); con θ≈0 la
inflación es (casi) una caminata: los 70. El gráfico compara AMBOS regímenes
con el mismo punto de partida. El BCRP adoptó metas explícitas en 2002
(meta actual 2% ±1pp — mención; series exactas vía BCRP en el nivel 12).

Procedencia: esquema de metas (Nueva Zelanda 1990 como pionero — mención);
formulación del anclaje: decisión de diseño didáctica sobre conocimiento
general del régimen.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _senda(pi0, theta, meta, T):
    pi = np.empty(int(T) + 1)
    pi[0] = pi0
    for t in range(int(T)):
        pi[t + 1] = meta + (1 - theta) * (pi[t] - meta)
    return pi


def _curvas(p):
    T = int(round(p["T"]))
    t = np.arange(T + 1)
    con = _senda(p["pi0"], p["theta"], p["pi_meta"], T)
    sin = _senda(p["pi0"], p["theta_debil"], p["pi_meta"], T)
    return {"lineas": {f"con ancla ($\\theta = {p['theta']:.2f}$)": (t, con, config.AZUL2),
                       f"sin ancla ($\\theta = {p['theta_debil']:.2f}$)": (t, sin, config.ROJO),
                       "meta $\\pi^*$": (t, np.full(T + 1, p["pi_meta"]), config.GRIS)},
            "anotacion": (f"semivida con ancla: {np.log(2) / -np.log(1 - p['theta']):.1f} períodos\n"
                          f"semivida sin ancla: {np.log(2) / -np.log(1 - p['theta_debil']):.1f}\n"
                          "θ no se decreta: se GANA (m41)")}


def _resultados(p):
    T = int(round(p["T"]))
    con = _senda(p["pi0"], p["theta"], p["pi_meta"], T)
    sin = _senda(p["pi0"], p["theta_debil"], p["pi_meta"], T)
    return {"semivida con ancla (períodos)": float(np.log(2) / -np.log(1 - p["theta"])),
            "semivida sin ancla": float(np.log(2) / -np.log(1 - p["theta_debil"])),
            f"π con ancla en t={T}": float(con[-1]),
            f"π sin ancla en t={T}": float(sin[-1]),
            "desvío inicial (pp)": p["pi0"] - p["pi_meta"]}


def _ecuaciones_calibradas(p):
    return [f"$\\pi_{{t+1}} = {p['pi_meta']:.1f} + {1 - p['theta']:.2f}\\,(\\pi_t - {p['pi_meta']:.1f})$",
            f"$semivida = \\ln 2 / (-\\ln{1 - p['theta']:.2f}) = "
            f"{np.log(2) / -np.log(1 - p['theta']):.1f}$"]


_P0 = {"theta": 0.6, "theta_debil": 0.08, "pi_meta": 2.0, "pi0": 8.0, "T": 12.0}


def _v_geometrica():
    pi = _senda(_P0["pi0"], _P0["theta"], _P0["pi_meta"], 30)
    desv = pi - _P0["pi_meta"]
    razones = desv[1:6] / desv[0:5]
    return bool(np.all(np.abs(razones - (1 - _P0["theta"])) < 1e-12)), \
        f"el desvío decae exactamente a razón (1−θ) = {1 - _P0['theta']:.2f} por período"


def _v_semivida():
    theta = _P0["theta"]
    pi = _senda(_P0["pi0"], theta, _P0["pi_meta"], 60)
    desv = np.abs(pi - _P0["pi_meta"])
    idx = int(np.argmax(desv <= desv[0] / 2))
    teo = np.log(2) / -np.log(1 - theta)
    return abs(idx - np.ceil(teo)) < 1 + 1e-9, \
        f"semivida simulada ({idx}) = ⌈ln2/−ln(1−θ)⌉ ({teo:.2f}): la fórmula gobierna"


def _v_ancla_acelera():
    s1 = np.log(2) / -np.log(1 - 0.6)
    s2 = np.log(2) / -np.log(1 - 0.08)
    return s1 < 1.0 < s2 and s2 > 8, (f"el mismo desvío muere en {s1:.1f} períodos con ancla y "
                                      f"tarda {s2:.1f} sin ella: θ ES el régimen")


def _v_sin_ancla_persiste():
    pi = _senda(_P0["pi0"], _P0["theta_debil"], _P0["pi_meta"], int(_P0["T"]))
    frac = (pi[-1] - _P0["pi_meta"]) / (_P0["pi0"] - _P0["pi_meta"])
    return frac > 1 / 3, (f"con θ={_P0['theta_debil']:.2f}, tras {int(_P0['T'])} períodos aún queda "
                          f"el {100 * frac:.0f}% del desvío (π={pi[-1]:.1f}%): la persistencia de los 70")


MODELO = Modelo(
    id="m40", nivel=6,
    nombre="Inflación objetivo (metas)",
    xlabel="Período $t$", ylabel="Inflación $\\pi$ (%)",
    parametros=[
        Parametro("theta", _P0["theta"], 0.05, 0.95, 0.05, "Anclaje θ (régimen con metas)", grupo="régimen",
                  definicion="fuerza con que las expectativas jalan π a la meta"),
        Parametro("theta_debil", _P0["theta_debil"], 0.01, 0.4, 0.01, "Anclaje sin régimen", grupo="régimen",
                  definicion="el contrafactual: los 70"),
        Parametro("pi0", _P0["pi0"], 2, 15, 0.5, "Inflación inicial π0 (%)", grupo="situación",
                  definicion="el desvío que hay que domar"),
        Parametro("pi_meta", _P0["pi_meta"], 1, 4, 0.5, "Meta π* (%)", grupo="régimen",
                  definicion="pública y explícita: la mitad de su poder está en anunciarla"),
        Parametro("T", _P0["T"], 6, 30, 1, "Períodos simulados", grupo="situación"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué anunciar un número — y cumplirlo — vuelve baratos los shocks de inflación?",
        variables=[("π_t", "inflación — endógena, jalada por el ancla"),
                   ("θ", "anclaje — NO es un instrumento: es credibilidad acumulada (m41)"),
                   ("π*", "la meta pública — el número que coordina expectativas")],
        derivacion=["\\pi_{t+1} - \\pi^* = (1-\\theta)\\,(\\pi_t - \\pi^*)",
                    "\\pi_t - \\pi^* = (1-\\theta)^t\\,(\\pi_0 - \\pi^*)",
                    "t_{1/2} = \\frac{\\ln 2}{-\\ln(1-\\theta)}"],
        contexto=("Tras el fracaso de las metas monetarias (m34: V inestable) y el "
                  "trauma de los 70 (m14), Nueva Zelanda probó en 1990 algo radical: "
                  "anunciar la inflación deseada y responsabilizar al banco central "
                  "por cumplirla. Funcionó — y se volvió el estándar mundial. El "
                  "BCRP lo adoptó en 2002; la meta vigente es 2% ±1pp (mención). El "
                  "mecanismo profundo: cuando el público CREE en la meta, fija "
                  "precios y salarios con ella — y la SRAS (m21) deja de perseguir "
                  "la inflación pasada."),
        autores=("Régimen pionero: Reserva del Banco de Nueva Zelanda (1990, "
                 "mención); teoría del ancla nominal: Bernanke-Mishkin y la "
                 "literatura de los 90 (menciones); Perú: BCRP desde 2002 (mención)."),
        supuestos=[
            "θ resume TODO el régimen (independencia, comunicación, historial): aquí es parámetro; en m41 se explica por qué se gana o se pierde.",
            "El proceso jala hacia π* sin costo real explícito: la tasa de sacrificio (m14) vive detrás de θ — anclar AHORRA sacrificio, no lo elimina.",
            "Shocks de una vez (π0): choques repetidos de oferta tensionan el esquema (flexible IT, mención).",
        ],
        ecuaciones=[
            Ecuacion("\\pi_{t+1} = \\pi^* + (1-\\theta)(\\pi_t - \\pi^*)", "el ancla en acción",
                     "cada período, una fracción θ del desvío se evapora porque contratos y "
                     "expectativas ya apuntan a π*: la meta hace parte del trabajo de la tasa."),
            Ecuacion("t_{1/2} = \\ln 2 / (-\\ln(1-\\theta))", "el dividendo de credibilidad",
                     "con θ=0.6 un shock muere en un período; con θ=0.08 dura una década: la "
                     "diferencia entre el Perú post-2002 y los años 80."),
        ],
        intuicion=("La meta es una profecía autocumplida institucionalizada: si "
                   "todos esperan 2%, negocian al 2%, y la inflación efectiva gravita "
                   "al 2% — el banco central casi no necesita actuar. El gráfico de "
                   "dos líneas es el argumento completo: mismo shock, mismo país, "
                   "dos regímenes — uno lo olvida en dos años, el otro lo arrastra "
                   "una década. La lección peruana de los choques de alimentos: con "
                   "ancla, los picos de π vuelven solos (m113 lo verá con datos)."),
        equilibrio=("π* es el punto fijo, globalmente estable para θ∈(0,1] "
                    "(verificado: decaimiento geométrico exacto y semivida = "
                    "fórmula). Con θ→0 el punto fijo existe pero es irrelevante a "
                    "horizonte humano: la persistencia de los 70."),
        limitaciones=[
            "θ exógeno es la simplificación central: la credibilidad se GANA con historial y se pierde con un desliz — m41 endogeneiza el porqué.",
            "Sin distinción demanda/oferta: ante shocks de oferta la meta estricta puede costar producto (flexible IT: horizonte de convergencia, mención).",
            "El ancla ata expectativas de INFLACIÓN, no burbujas ni tipo de cambio: los flancos abiertos son el nivel 7 y el 10.",
        ],
        evolucion=("El régimen queda montado: instrumento (m39) + regla (m38) + "
                   "ancla (m40). Falta el fundamento de todo: POR QUÉ atarse funciona "
                   "— la inconsistencia temporal y su solución institucional (m41) — "
                   "y el papel de las expectativas racionales (m42). El contraste "
                   "empírico peruano (inflación pre y post 2002) es m99."),
    ),
    escenarios=[
        Escenario("adopcion_del_regimen", "un país adopta metas: θ pasa de 0.08 a 0.7",
                  {"theta": 0.7},
                  "el mismo desvío de 6pp muere en ~0.6 períodos: la historia "
                  "monetaria peruana post-2002 contada por un parámetro.",
                  cadena=["meta pública + independencia + historial", "↑θ",
                          "contratos apuntan a π*", "los desvíos mueren solos",
                          "la tasa trabaja menos (m38) para lo mismo"]),
        Escenario("ancla_perdida", "crisis de credibilidad: θ cae a 0.05",
                  {"theta": 0.05},
                  "el shock se vuelve régimen: π apenas cede en 12 períodos — sin "
                  "ancla, cada choque de oferta se hereda (los 70, m14).",
                  cadena=["desliz o dominancia fiscal", "↓θ", "expectativas miran π pasada",
                          "el desvío persiste", "desinflar exigirá sacrificio (m14)"]),
        Escenario("choque_de_alimentos", "shock transitorio: π0 = 5% con ancla fuerte",
                  {"pi0": 5.0, "theta": 0.7},
                  "π vuelve a la meta en ~2 períodos SIN gran apretón: la respuesta "
                  "peruana típica a los choques de alimentos importados (m113).",
                  cadena=["shock de oferta puntual", "π salta sobre la meta",
                          "las expectativas NO se mueven (ancladas)",
                          "π regresa sola al disiparse el shock"]),
    ],
    verificaciones=[
        Verificacion("decaimiento geométrico exacto a razón (1−θ)", _v_geometrica),
        Verificacion("semivida simulada = fórmula", _v_semivida),
        Verificacion("el ancla acelera órdenes de magnitud", _v_ancla_acelera),
        Verificacion("sin ancla, la persistencia de los 70", _v_sin_ancla_persiste),
    ],
    notas="Una profecía autocumplida con directorio y memoria: θ no se decreta, se gana (m41).",
)
