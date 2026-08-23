# m52_adas_expectativas.py — AD-AS dinámico con expectativas (nivel 8).
#
# El aparato moderno en INFLACIÓN (ya no en niveles de precios, m23):
#   AD (vía regla):  Y_t = Y* − α·(π_t − π*) + d_t     (m51 hecho curva)
#   AS (Phillips):   π_t = π^e_t + λ·(Y_t − Y*) + s_t
#   expectativas adaptativas: π^e_t = π_{t−1}
# Forma reducida por período:  π_t·(1+λα) = π_{t−1} + λα·π* + λ·d_t + s_t
# Converge SOLO porque la regla (α>0) inclina la AD: el ancla institucional
# de m38-m40 es lo que hace estable a la economía de este nivel.
#
# Procedencia: AD-AS dinámico de manuales modernos (Mankiw, mención) —
# conocimiento general; calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _simular(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    d = np.where(t == int(p["t_shock"]), p["shock_d"], 0.0)
    s = np.where(t == int(p["t_shock"]), p["shock_s"], 0.0)
    pi = np.empty(T + 1); y = np.empty(T + 1)
    pe = p["pi_meta"]
    for j in range(T + 1):
        pi[j] = (pe + p["lam"] * p["alpha"] * p["pi_meta"]
                 + p["lam"] * d[j] + s[j]) / (1 + p["lam"] * p["alpha"])
        y[j] = p["Ystar"] - p["alpha"] * (pi[j] - p["pi_meta"]) + d[j]
        pe = pi[j]
    return t, pi, y


def _curvas(p):
    t, pi, y = _simular(p)
    return {"lineas": {"inflación $\\pi_t$ (%)": (t, pi, config.ROJO),
                       "producto $Y_t$ (índice)": (t, y, config.AZUL2),
                       "meta $\\pi^*$ / potencial $Y^*$": (t, np.full(len(t), p["pi_meta"]), config.GRIS)},
            "anotacion": (f"shock en $t={int(p['t_shock'])}$: "
                          f"demanda {p['shock_d']:+.1f}, costos {p['shock_s']:+.1f}\n"
                          f"la AD inclinada por la regla ($\\alpha={p['alpha']:.1f}$) "
                          "trae todo de vuelta\n(nota: $Y^*=100$ y $\\pi^*=2$ comparten eje)")}


def _resultados(p):
    t, pi, y = _simular(p, T=200)
    t0 = int(p["t_shock"])
    return {"π en el impacto (%)": float(pi[t0]),
            "Y en el impacto": float(y[t0]),
            "π de largo plazo (%)": float(pi[-1]),
            "Y de largo plazo": float(y[-1]),
            "períodos con |π−π*| > 0.1": float(np.sum(np.abs(pi - p["pi_meta"]) > 0.1))}


_P0 = {"Ystar": 100.0, "pi_meta": 2.0, "alpha": 1.0, "lam": 0.5,
       "shock_d": 3.0, "shock_s": 0.0, "t_shock": 3.0, "T": 15.0}


def _v_estado_estacionario():
    p = dict(_P0, shock_d=0.0, shock_s=0.0)
    t, pi, y = _simular(p)
    ok = bool(np.all(np.abs(pi - p["pi_meta"]) < 1e-12)) and bool(np.all(np.abs(y - p["Ystar"]) < 1e-12))
    return ok, "sin shocks el sistema descansa exacto en (Y*, π*): el ancla institucional en reposo"


def _v_convergencia():
    t, pi, y = _simular(_P0, T=300)
    ok = abs(pi[-1] - _P0["pi_meta"]) < 1e-9 and abs(y[-1] - _P0["Ystar"]) < 1e-9
    return ok, "tras el shock, TODO regresa a (Y*, π*): la regla convierte los shocks en visitas"


def _v_regla_estabiliza():
    n_dura = _resultados(dict(_P0, alpha=2.0))["períodos con |π−π*| > 0.1"]
    n_blanda = _resultados(dict(_P0, alpha=0.3))["períodos con |π−π*| > 0.1"]
    return n_dura < n_blanda, (f"con regla dura (α=2) el desvío dura {n_dura:.0f} períodos; con "
                               f"blanda (α=0.3), {n_blanda:.0f}: la pendiente de la AD ES el ancla")


def _v_oferta_estanflacion():
    p = dict(_P0, shock_d=0.0, shock_s=2.0)
    t, pi, y = _simular(p)
    t0 = int(p["t_shock"])
    return pi[t0] > p["pi_meta"] and y[t0] < p["Ystar"], \
        "el shock de costos sube π y baja Y a la vez: la estanflación de m19/m24, ahora en dinámica de inflación"


MODELO = Modelo(
    id="m52", nivel=8,
    nombre="AD-AS dinámico con expectativas",
    xlabel="Período $t$", ylabel="$\\pi_t$ (%) · $Y_t$ (índice)",
    parametros=[
        Parametro("shock_d", _P0["shock_d"], -5, 5, 0.5, "Shock de demanda d", grupo="experimento"),
        Parametro("shock_s", _P0["shock_s"], -3, 3, 0.5, "Shock de costos s", grupo="experimento"),
        Parametro("alpha", _P0["alpha"], 0.1, 3, 0.1, "Dureza de la regla α", grupo="régimen",
                  definicion="cuánto Y sacrifica el BC por punto de π (m38 hecho pendiente)"),
        Parametro("lam", _P0["lam"], 0.1, 1.5, 0.05, "Pendiente de Phillips λ", grupo="estructura"),
        Parametro("t_shock", _P0["t_shock"], 1, 8, 1, "Período del shock", grupo="experimento"),
        Parametro("T", _P0["T"], 8, 40, 1, "Períodos simulados", grupo="experimento"),
        Parametro("pi_meta", _P0["pi_meta"], 1, 4, 0.5, "Meta π* (%)", grupo="régimen"),
        Parametro("Ystar", _P0["Ystar"], 90, 110, 1, "Producto potencial Y*", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Cómo digiere una economía CON regla monetaria un shock — y por qué sin regla no lo digiere?",
        variables=[("π_t, Y_t", "inflación y producto — endógenos, bailan juntos"),
                   ("π^e = π_{t−1}", "expectativas adaptativas — la inercia del sistema"),
                   ("α", "la regla hecha pendiente — el ancla que trae todo de vuelta")],
        derivacion=["AD: \\;Y_t = Y^* - \\alpha(\\pi_t - \\pi^*) + d_t \\;\\;(m51)",
                    "AS: \\;\\pi_t = \\pi_{t-1} + \\lambda(Y_t - Y^*) + s_t \\;\\;(m14)",
                    "\\Rightarrow\\; \\pi_t = \\frac{\\pi_{t-1} + \\lambda\\alpha\\,\\pi^* + \\lambda d_t + s_t}{1+\\lambda\\alpha}"],
        contexto=("Es el AD-AS de m23-m25 traducido al idioma en que piensan los "
                  "bancos centrales: inflación (no nivel de precios) y una demanda "
                  "cuya pendiente ya no es el efecto Keynes sino la REGLA (m51). El "
                  "sistema entero se vuelve un promedio ponderado entre la inercia "
                  "(π de ayer) y el ancla (π*), con pesos que decide α: la política "
                  "no es un shock más — es la estructura que hace converger a los "
                  "demás."),
        autores=("Formato de manual moderno (el AD-AS dinámico de Mankiw, mención); "
                 "es el puente pedagógico estándar hacia el NK de 3 ecuaciones."),
        supuestos=["Expectativas ADAPTATIVAS: la inercia es aprendizaje rezagado (m54-m55 pondrán racionales y todo cambiará de reloj).",
                   "La regla responde solo a π (α): añadir respuesta a Y no cambia la lógica (m56 la tendrá).",
                   "Shocks de una vez; Y* y π* fijos."],
        ecuaciones=[
            Ecuacion("\\pi_t = \\frac{\\pi_{t-1} + \\lambda\\alpha\\pi^* + \\lambda d_t + s_t}{1+\\lambda\\alpha}",
                     "la forma reducida",
                     "un promedio entre la inflación heredada y la meta: el coeficiente 1/(1+λα) "
                     "es la INERCIA del sistema — la regla dura (α alto) la come rápido."),
            Ecuacion("Y_t = Y^* - \\alpha(\\pi_t - \\pi^*) + d_t", "la AD moderna",
                     "pendiente negativa en (π, Y) POR la regla: con π sobre la meta el BC "
                     "encarece el crédito y compra desinflación con brecha."),
        ],
        intuicion=("La geometría de m23 se vuelve película con un solo fotograma "
                   "repetido: cada período, la economía negocia entre lo que la "
                   "inflación de ayer exige y lo que la meta promete, y α decide "
                   "quién gana. Un shock de demanda visita y se va; uno de costos "
                   "obliga al dilema de m19 — pero ahora el retorno está GARANTIZADO "
                   "por la regla, no por la suerte: quita α (la regla) y el sistema "
                   "pierde el ancla (m40 sin θ)."),
        equilibrio=("(Y*, π*) es el único punto fijo y es globalmente estable con "
                    "α>0 (verificado: reposo exacto y convergencia). La velocidad "
                    "es 1/(1+λα) por período — el análogo dinámico de la semivida "
                    "de m40."),
        limitaciones=[
            "Adaptativas puras: con racionales, los shocks ANUNCIADOS actúan antes de llegar (m54-m56) y la desinflación puede ser barata (m42).",
            "Sin ZLB ni economía abierta: los pisos (m12) y el canal cambiario (m49) esperan en los escenarios del nivel 11.",
            "α constante: la regla real cambia de dureza según el estado (no linealidades, mención).",
        ],
        evolucion=("Este es el NK 'de entrenamiento': mismas tres piezas que m56 "
                   "(demanda con regla, Phillips, ancla) pero mirando al pasado. "
                   "m54 y m55 voltean la mirada de las dos curvas hacia el FUTURO, "
                   "y m56 resuelve el sistema racional completo."),
    ),
    escenarios=[
        Escenario("visita_de_demanda", "shock de demanda +3 en t=3",
                  {"shock_d": 3.0, "shock_s": 0.0},
                  "π e Y saltan JUNTOS y regresan en pocos períodos: la firma de "
                  "demanda (m18) con final feliz garantizado por la regla.",
                  cadena=["+d en la AD", "↑Y y ↑π juntos", "la regla encarece el crédito",
                          "πe se corrige a la baja período a período", "regreso a (Y*, π*)"]),
        Escenario("shock_de_costos", "shock de oferta +2 en t=3",
                  {"shock_d": 0.0, "shock_s": 2.0},
                  "π sube CON Y bajo el potencial (estanflación, m19) y luego ambos "
                  "vuelven: la regla no evita el dilema — evita que se vuelva régimen.",
                  cadena=["+s en la Phillips", "↑π con ↓Y (dilema m19)",
                          "la regla contiene la propagación a πe", "el shock no se hereda (m40)"]),
        Escenario("regla_dura", "α = 2: el banco halcón",
                  {"alpha": 2.0},
                  "el desvío muere en la mitad del tiempo, pagando más brecha en el "
                  "impacto: el trade-off de credibilidad de m41 hecho dinámica.",
                  cadena=["α alto", "más Y sacrificado por punto de π",
                          "la inercia 1/(1+λα) se encoge", "retorno rápido a la meta"]),
        Escenario("regla_blanda", "α = 0.3: el ancla débil",
                  {"alpha": 0.3},
                  "el shock se pasea períodos y períodos: con α→0 esto es m14 — la "
                  "espiral de los 70 es una regla sin pendiente.",
                  cadena=["α bajo", "el BC casi no responde", "πe hereda el shock",
                          "desvíos persistentes (el fantasma de m14)"]),
    ],
    verificaciones=[
        Verificacion("reposo exacto en (Y*, π*) sin shocks", _v_estado_estacionario),
        Verificacion("convergencia global tras el shock", _v_convergencia),
        Verificacion("la regla dura acorta el desvío", _v_regla_estabiliza),
        Verificacion("shock de costos ⇒ estanflación dinámica", _v_oferta_estanflacion),
    ],
    notas="El NK de entrenamiento: mismas piezas que m56, mirando todavía al pasado.",
)
