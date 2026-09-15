"""simuladores/macro/modelos/nivel_08/m61_shocks_productividad.py — persistencia y propagación (nivel 8, cierre).

La asignatura pendiente de m57-m58: ¿el modelo AÑADE memoria al shock, o
solo la hereda? Se añade el capital de Solow (m26) al esqueleto RBC:
  y_t = a_t + α·k_t ;   k_{t+1} = (1−δ)·k_t + s·y_t ;   a_t = ρ_a^t
Sin capital (α=0): y ≡ a — cola idéntica al impulso (m58). Con capital: la
inversión de hoy es capacidad de mañana → y sobrevive al shock (semivida
mayor) y k tiene JOROBA (pico después del impacto): propagación INTERNA.
El "propagation puzzle" (Cogley-Nason, mención): el RBC básico propaga poco
— la agenda que llevó a los DSGE medianos (Smets-Wouters, mención).

Procedencia: mecánica Solow-RBC didáctica (decisión de diseño sobre m26/m57);
crítica de propagación: Cogley y Nason (1995, mención).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    a = p["a0"] * p["rho_a"] ** t
    k = np.zeros(T + 1)
    y = np.zeros(T + 1)
    for j in range(T + 1):
        y[j] = a[j] + p["alpha"] * k[j]
        if j < T:
            k[j + 1] = (1 - p["delta"]) * k[j] + p["s"] * y[j]
    return t, a, y, k


def _semivida(serie):
    """Primer período en que la serie cae a la mitad de su impacto."""
    objetivo = serie[0] / 2
    idx = np.argmax(serie <= objetivo)
    return float(idx) if serie[int(idx)] <= objetivo else float(len(serie))


def _curvas(p):
    t, a, y, k = _sendas(p)
    return {"lineas": {"producto $y_t = a_t + \\alpha k_t$": (t, y, config.AZUL2),
                       "capital $k_t$ (con joroba)": (t, k, config.DORADO),
                       "impulso $a_t = \\rho^t$": (t, a, config.GRIS)},
            "anotacion": (f"semivida del impulso: {_semivida(a):.0f} · "
                          f"semivida del producto: {_semivida(y):.0f}\n"
                          f"pico del capital en $t = {int(np.argmax(k))}$ (joroba)\n"
                          "la diferencia es PROPAGACIÓN interna — lo que m57 no tenía")}


def _resultados(p):
    t, a, y, k = _sendas(p, T=200)
    return {"semivida del impulso a": _semivida(a),
            "semivida del producto y": _semivida(y),
            "propagación (diferencia de semividas)": _semivida(y) - _semivida(a),
            "pico del capital (período)": float(np.argmax(k)),
            "capital máximo alcanzado": float(np.max(k))}


def _ecuaciones_calibradas(p):
    return [f"$y_t = a_t + {p['alpha']:.2f}\\,k_t$",
            f"$k_{{t+1}} = {1 - p['delta']:.2f}\\,k_t + {p['s']:.2f}\\,y_t$"]


_P0 = {"a0": 1.0, "rho_a": 0.5, "alpha": 0.33, "s": 0.2, "delta": 0.1, "T": 30.0}


def _v_sin_capital_sin_propagacion():
    p = dict(_P0, alpha=0.0)
    t, a, y, k = _sendas(p, T=100)
    return bool(np.all(np.abs(y - a) < 1e-12)), \
        "con α=0, y ≡ a exacto: el esqueleto de m57-m58 no añade UN período de memoria"


def _v_capital_propaga():
    r = _resultados(_P0)
    return r["semivida del producto y"] > r["semivida del impulso a"], \
        (f"con capital, el producto sobrevive al impulso (semividas {r['semivida del producto y']:.0f} "
         f"vs {r['semivida del impulso a']:.0f}): la inversión de hoy es capacidad de mañana")


def _v_joroba():
    t, a, y, k = _sendas(_P0, T=100)
    pico = int(np.argmax(k))
    return pico >= 2 and float(k[pico]) > float(k[1]), \
        (f"el capital tiene JOROBA (pico en t={pico}, después del impacto): la firma "
         "de la acumulación — los datos tienen jorobas, los esqueletos sin capital no")


def _v_estacionario():
    # autovalor del sistema: (1−δ)+s·α = 0.966 → converger toma cientos de períodos
    t, a, y, k = _sendas(_P0, T=800)
    return abs(float(y[-1])) < 1e-6 and abs(float(k[-1])) < 1e-6, \
        "todo regresa a cero: la propagación alarga la visita del shock, no lo vuelve permanente"


MODELO = Modelo(
    id="m61", nivel=8,
    nombre="Shocks de productividad (persistencia y propagación)",
    xlabel="Período $t$", ylabel="Respuesta (%)",
    parametros=[
        Parametro("rho_a", _P0["rho_a"], 0.0, 0.9, 0.05, "Persistencia del impulso ρ_a", grupo="impulso",
                  definicion="corta a propósito: para VER lo que propaga el modelo"),
        Parametro("alpha", _P0["alpha"], 0.0, 0.5, 0.01, "Peso del capital α", grupo="propagación",
                  definicion="α=0 apaga la propagación (el esqueleto de m57)"),
        Parametro("s", _P0["s"], 0.05, 0.3, 0.05, "Tasa de inversión s", grupo="propagación",
                  definicion="estabilidad: (1−δ)+s·α < 1 — no acercarse a la raíz unitaria"),
        Parametro("delta", _P0["delta"], 0.05, 0.3, 0.05, "Depreciación δ", grupo="propagación"),
        Parametro("a0", _P0["a0"], 0.5, 3, 0.25, "Tamaño del shock a0", grupo="impulso"),
        Parametro("T", _P0["T"], 15, 60, 5, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿De quién es la persistencia del ciclo: del shock que llega o del modelo que lo digiere?",
        variables=[("a_t", "el impulso — deliberadamente corto (ρ=0.5)"),
                   ("k_t", "el capital — la memoria física de la economía"),
                   ("semivida(y) − semivida(a)", "la PROPAGACIÓN — el número que juzga al modelo")],
        derivacion=["y_t = a_t + \\alpha\\,k_t \\;\\;(m26\\;log-lineal)",
                    "k_{t+1} = (1-\\delta)\\,k_t + s\\,y_t \\;\\;(acumulación)",
                    "\\alpha = 0 \\Rightarrow y \\equiv a \\;\\;(cero\\;propagación)"],
        contexto=("m57 y m58 dejaron una confesión verificada: el esqueleto RBC "
                  "hereda TODA su persistencia del impulso (autocorr(y) = "
                  "autocorr(a) exacta). Cogley y Nason (1995, mención) elevaron la "
                  "confesión a acusación: los RBC 'explican' el ciclo metiéndole la "
                  "persistencia al shock exógeno. Este modelo muestra el mecanismo "
                  "propagador más antiguo del currículo — el capital de Solow (m26) "
                  "— trabajando dentro del ciclo: la inversión de hoy es capacidad "
                  "de mañana, y el producto sobrevive a su causa. La agenda de "
                  "'mecanismos que alargan colas' (hábitos, ajuste de capital, "
                  "rigideces) es el camino a los DSGE medianos que hoy usan los "
                  "bancos centrales (Smets-Wouters, mención)."),
        autores=("Crítica de propagación: Cogley y Nason (1995, mención); la "
                 "respuesta DSGE mediana: Christiano-Eichenbaum-Evans (2005), "
                 "Smets y Wouters (2007) — menciones."),
        supuestos=[
            "El impulso es CORTO a propósito (ρ=0.5): así la cola del producto delata al mecanismo, no al shock.",
            "Acumulación log-lineal didáctica (k entra con α; s y δ fijos): el Solow de m26 dentro del ciclo.",
            "Sin trabajo variable ni consumo explícito: se aísla UN mecanismo propagador para verlo limpio.",
        ],
        ecuaciones=[
            Ecuacion("k_{t+1} = (1-\\delta)k_t + s\\,y_t", "la memoria física",
                     "cada período de producto alto deja capital que produce MAÑANA: el shock se "
                     "va, la capacidad que financió se queda un tiempo."),
            Ecuacion("semivida(y) > semivida(a)", "el veredicto",
                     "la definición operativa de propagación interna: verificada aquí, ausente "
                     "en m57-m58 (y en el m56 puro, cuyas IRFs decaen a ρ exacto)."),
        ],
        intuicion=("La pregunta '¿de quién es la persistencia?' es la prueba de "
                   "madurez de un modelo de ciclo: cualquiera reproduce datos "
                   "persistentes ASUMIENDO shocks persistentes (m58 con ρ=0.95); el "
                   "mérito es generar cola con impulsos cortos. El capital lo logra "
                   "modestamente (la joroba de k es su firma); los DSGE medianos "
                   "apilan mecanismos hasta que las colas del modelo igualan las de "
                   "los datos — ese es, literalmente, el oficio de calibrar un "
                   "banco central moderno."),
        equilibrio=("Retorno global a cero verificado (la propagación alarga la "
                    "visita, no la vuelve permanente); la joroba del capital "
                    "(pico DESPUÉS del impacto) y la brecha de semividas son las "
                    "firmas cuantificadas del mecanismo."),
        limitaciones=[
            "Un solo mecanismo: hábitos de consumo, costos de ajuste, fricciones laborales y financieras añaden colas que aquí no están (menciones).",
            "Log-lineal sin nivel de estado estacionario: es el juguete del mecanismo, no el Solow completo (m26-m27 tienen los niveles).",
            "Shocks solo tecnológicos: la agenda de identificación (¿qué golpea de verdad?) sigue abierta (nivel 12).",
        ],
        evolucion=("Cierra el nivel 8 con su lección metodológica: los modelos se "
                   "juzgan por sus COLAS y sus JOROBAS. El nivel 9 (fiscal) usará "
                   "esta vara con la deuda (persistencia por acumulación de "
                   "pasivos, m63-m64) y el nivel 10 con las crisis (persistencia "
                   "por destrucción de balances)."),
    ),
    escenarios=[
        Escenario("con_capital", "el mecanismo encendido (α=0.33, s=0.2)",
                  {"alpha": 0.33},
                  "el impulso muere en 1 período; el producto tarda 2 y el capital "
                  "hace joroba en t≈4: propagación interna medible.",
                  cadena=["shock corto", "y alto financia inversión", "k se acumula (joroba)",
                          "k produce cuando a ya se fue", "semivida(y) > semivida(a)"]),
        Escenario("esqueleto_desnudo", "α = 0: el mundo de m57-m58",
                  {"alpha": 0.0},
                  "y calca al impulso, punto a punto: cero propagación — la "
                  "acusación de Cogley-Nason en una línea plana.",
                  cadena=["α=0", "el capital no entra en y", "y ≡ a exacto",
                          "toda la persistencia es prestada"]),
        Escenario("economia_inversora", "más memoria física: s=0.30 con δ=0.12",
                  {"s": 0.30, "delta": 0.12},
                  "más inversión por punto de producto = joroba más alta y cola más "
                  "larga: las economías que invierten fuerte digieren más lento sus shocks.",
                  cadena=["↑s", "cada boom deja más capital", "la joroba crece",
                          "la cola del producto se alarga"]),
        Escenario("capital_fugaz", "δ = 0.25: la memoria se oxida rápido",
                  {"delta": 0.25},
                  "la joroba se achata y la propagación casi desaparece: sin "
                  "capital duradero no hay cola — la durabilidad ES la memoria.",
                  cadena=["↑δ", "el capital acumulado se evapora",
                          "k no alcanza a producir mañana", "la propagación se apaga"]),
    ],
    verificaciones=[
        Verificacion("α=0 ⇒ y≡a exacto (cero propagación, m57)", _v_sin_capital_sin_propagacion),
        Verificacion("con capital: semivida(y) > semivida(a)", _v_capital_propaga),
        Verificacion("la joroba del capital (pico tras el impacto)", _v_joroba),
        Verificacion("retorno global a cero (visita, no mudanza)", _v_estacionario),
    ],
    notas="Los modelos se juzgan por sus colas y sus jorobas: cierre metodológico del nivel 8.",
)
