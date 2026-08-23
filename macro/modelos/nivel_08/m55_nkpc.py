# m55_nkpc.py — la curva de Phillips nuevo keynesiana (nivel 8).
#
# La Phillips que mira al FUTURO (la de m14 miraba al pasado):
#   π_t = β·π_{t+1} + κ·x_t
# Iterando hacia adelante (π terminal = 0):
#   π_t = κ · Σ_{j≥t} β^{j−t} · x_j
# La inflación de HOY es el valor presente de TODAS las brechas futuras. La
# pendiente κ nace de la rigidez de Calvo (m53): κ = (1−θ)(1−βθ)/θ (mención).
# Consecuencia célebre y polémica: una desinflación PERFECTAMENTE creíble no
# cuesta nada — sin inercia intrínseca, π salta donde digan las brechas.
#
# Procedencia: NKPC estándar (derivación de Calvo: Galí, Woodford — menciones;
# el paper de Calvo 1983 está en la biblioteca) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    ini, K = int(round(p["t_ini"])), int(round(p["K"]))
    x = np.where((t >= ini) & (t < ini + K), p["x_size"], 0.0)
    pi = np.zeros(T + 2)
    for j in range(T, -1, -1):                      # π_t = β π_{t+1} + κ x_t
        pi[j] = p["beta"] * pi[j + 1] + p["kappa"] * x[j]
    return t, x, pi[:-1]


def _curvas(p):
    t, x, pi = _sendas(p)
    return {"lineas": {"inflación $\\pi_t$": (t, pi, config.ROJO),
                       "brecha anunciada $x_t$": (t, x, config.AZUL2),
                       "cero": (t, np.zeros_like(pi), config.GRIS)},
            "anotacion": (f"$\\pi_0 = \\kappa\\,\\Sigma\\,\\beta^j x_j = {float(pi[0]):.3f}$\n"
                          f"boom de {p['x_size']:.1f} × {int(p['K'])} períodos desde "
                          f"$t={int(p['t_ini'])}$\n"
                          "la inflación de hoy YA contiene las brechas de mañana")}


def _resultados(p):
    t, x, pi = _sendas(p)
    ini, K = int(round(p["t_ini"])), int(round(p["K"]))
    cerrada = (p["kappa"] * p["x_size"] * p["beta"] ** ini
               * (1 - p["beta"] ** K) / (1 - p["beta"]))
    return {"π hoy (iteración)": float(pi[0]),
            "π hoy (fórmula cerrada)": cerrada,
            "π al iniciar el boom": float(pi[ini]) if ini < len(pi) else 0.0,
            "π si la brecha fuera permanente (κx/(1−β))":
                p["kappa"] * p["x_size"] / (1 - p["beta"]),
            "descuento del futuro β": p["beta"]}


def _ecuaciones_calibradas(p):
    return [f"$\\pi_t = {p['beta']:.2f}\\,\\pi_{{t+1}} + {p['kappa']:.2f}\\,x_t$",
            f"$\\pi_0 = {p['kappa']:.2f} \\times {p['x_size']:.1f} \\times "
            f"{p['beta']:.2f}^{{{int(p['t_ini'])}}}\\,\\frac{{1-{p['beta']:.2f}^{{{int(p['K'])}}}}}"
            f"{{1-{p['beta']:.2f}}} = {float(_sendas(p)[2][0]):.3f}$"]


_P0 = {"beta": 0.97, "kappa": 0.2, "x_size": 2.0, "K": 4.0, "t_ini": 3.0, "T": 14.0}


def _v_suma_cerrada():
    r = _resultados(_P0)
    return abs(r["π hoy (iteración)"] - r["π hoy (fórmula cerrada)"]) < 1e-12, \
        f"la recursión reproduce la suma geométrica cerrada ({r['π hoy (iteración)']:.4f})"


def _v_permanente():
    p = dict(_P0, t_ini=0.0, K=600.0, T=600.0)
    _, _, pi = _sendas(p)
    teo = p["kappa"] * p["x_size"] / (1 - p["beta"])
    return abs(float(pi[0]) - teo) / teo < 1e-6, \
        (f"con brecha permanente, π = κx/(1−β) = {teo:.2f}: pequeñas brechas sostenidas "
         "son MUCHA inflación (el descuento apenas muerde)")


def _v_descuento_beta():
    pi_3 = float(_sendas(dict(_P0, t_ini=3.0))[2][0])
    pi_6 = float(_sendas(dict(_P0, t_ini=6.0))[2][0])
    return abs(pi_6 / pi_3 - _P0["beta"] ** 3) < 1e-9, \
        (f"alejar el boom 3 períodos multiplica π_0 por β³ = {_P0['beta'] ** 3:.4f} exacto: "
         "el futuro pesa, descontado")


def _v_sin_inercia():
    p = dict(_P0, x_size=0.0)
    _, _, pi = _sendas(p)
    return bool(np.all(np.abs(pi) < 1e-12)), \
        ("sin brechas presentes NI futuras, π = 0 en todo t: la NKPC pura no tiene "
         "inercia — la desinflación creíble sale gratis (y ESO es su problema empírico)")


MODELO = Modelo(
    id="m55", nivel=8,
    nombre="Curva de Phillips nuevo keynesiana (NKPC)",
    xlabel="Período $t$", ylabel="Desviaciones",
    parametros=[
        Parametro("x_size", _P0["x_size"], -3, 4, 0.5, "Tamaño de la brecha anunciada", grupo="anuncio"),
        Parametro("K", _P0["K"], 1, 8, 1, "Duración del boom K", grupo="anuncio"),
        Parametro("t_ini", _P0["t_ini"], 0, 8, 1, "Inicio del boom", grupo="anuncio"),
        Parametro("kappa", _P0["kappa"], 0.05, 0.6, 0.05, "Pendiente κ (de Calvo, m53)", grupo="estructura",
                  definicion="rigidez alta (θ↑) ⇒ κ baja: la Phillips se aplana"),
        Parametro("beta", _P0["beta"], 0.90, 0.99, 0.01, "Descuento β", grupo="estructura"),
        Parametro("T", _P0["T"], 8, 30, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si los precios los ponen firmas que miran al futuro, ¿de quién es hija la inflación de hoy?",
        variables=[("π_t", "inflación — valor presente de brechas futuras"),
                   ("x_t", "la brecha — el costo marginal en versión macro"),
                   ("κ", "la pendiente — nacida de la rigidez θ de m53"),
                   ("β", "el descuento — cuánto pesa el mañana en el precio de hoy")],
        derivacion=["Calvo\\;(m53): \\;solo\\;(1-\\theta)\\;reajusta\\;\\Rightarrow\\;precio\\;nuevo\\;mira\\;al\\;futuro",
                    "\\pi_t = \\beta\\,\\pi_{t+1} + \\kappa\\,x_t, \\quad \\kappa = \\frac{(1-\\theta)(1-\\beta\\theta)}{\\theta}\\;(mención)",
                    "\\pi_t = \\kappa \\sum_{j\\ge t} \\beta^{\\,j-t}\\,x_j"],
        contexto=("La Phillips de m14 miraba por el retrovisor (πe = π pasada); la "
                  "NKPC nace de firmas de Calvo (m53) que, al reajustar, fijan el "
                  "precio pensando en TODO el período que ese precio vivirá — o sea, "
                  "en el futuro. El resultado invierte la causalidad de la "
                  "inflación: no es herencia, es PROFECÍA. De ahí su promesa (la "
                  "desinflación creíble no cuesta — el fundamento fino de m40-m41) "
                  "y su problema (la inflación real ES persistente: la NKPC pura no "
                  "la genera, y la versión híbrida con un pie en m14 fue el arreglo "
                  "— mención Galí-Gertler)."),
        autores=("Derivación desde Calvo (1983, en biblioteca): Galí, Woodford, "
                 "Clarida-Galí-Gertler (menciones); la evidencia de la versión "
                 "híbrida: Galí y Gertler (1999, mención)."),
        supuestos=[
            "Expectativas RACIONALES con previsión de la senda de brechas (aquí: anunciada y creída).",
            "κ constante heredada de θ (m53): con inflación alta, θ cae y la curva se empina (mención).",
            "π terminal = 0: el ancla de largo plazo (la meta de m40) cierra la recursión.",
        ],
        ecuaciones=[
            Ecuacion("\\pi_t = \\beta\\,\\pi_{t+1} + \\kappa\\,x_t", "la NKPC",
                     "la inflación de hoy tiene DOS padres: la brecha presente (κx) y la "
                     "inflación que se espera para mañana (βπ') — el pasado no aparece."),
            Ecuacion("\\pi_t = \\kappa\\sum_{j\\ge t}\\beta^{j-t}x_j", "la inflación como profecía",
                     "todo boom futuro anunciado sube la inflación DESDE HOY (verificado con "
                     "descuento β^j exacto): la gemela de la IS de m54."),
        ],
        intuicion=("Las dos curvas del NK son la misma idea en espejos: la demanda "
                   "de hoy descuenta tasas futuras (m54) y la inflación de hoy "
                   "descuenta brechas futuras (m55). Por eso la política moderna es "
                   "GESTIÓN DE EXPECTATIVAS: quien controla lo que se espera, "
                   "controla lo que pasa. Y por eso la credibilidad (m41) vale "
                   "puntos de PIB: con NKPC creída, anunciar desinflación ES "
                   "desinflar."),
        equilibrio=("Trayectoria única dada la senda de brechas y el ancla terminal "
                    "(recursión = suma cerrada, verificado). La 'inflación de "
                    "equilibrio' con brecha permanente, κx/(1−β), muestra el "
                    "apalancamiento del futuro: β cerca de 1 multiplica por ~33."),
        limitaciones=[
            "Sin inercia intrínseca (verificado: sin brechas, π=0 instantáneo): la persistencia inflacionaria real obliga a híbridas con término backward (m14 se venga).",
            "κ estimada es pequeña y esquiva (la Phillips 'plana' post-2000, mención): identificarla es un problema econométrico serio (nivel 12).",
            "Anuncios creídos al 100%: la fe es endógena a la historia del banco central (m41).",
        ],
        evolucion=("Con la IS de m54 y esta NKPC, solo falta cerrar quién decide la "
                   "senda de tasas: la regla de Taylor (m38). m56 junta las tres "
                   "ecuaciones y resuelve el sistema racional completo — el modelo "
                   "canónico de la política monetaria moderna."),
    ),
    escenarios=[
        Escenario("boom_anunciado", "brecha +2 durante 4 períodos desde t=3",
                  {"x_size": 2.0},
                  "π sube DESDE HOY (0.42%) aunque el boom no empezó: los precios "
                  "nuevos ya lo incorporan — la inflación como profecía.",
                  cadena=["anuncio de boom futuro", "las firmas que reajustan hoy miran esa demanda",
                          "suben el precio YA", "π_0 = κΣβ^j x_j", "el futuro factura por adelantado"]),
        Escenario("enfriamiento_anunciado", "brechas negativas creíbles (x = −2)",
                  {"x_size": -2.0},
                  "π cae desde hoy sin recesión presente: la desinflación creíble "
                  "de m40-m41, ahora con su mecanismo exacto — y su letra chica "
                  "(hace falta que TODOS crean).",
                  cadena=["anuncio creíble de apretón", "los precios nuevos nacen más bajos",
                          "π cae desde t=0", "el costo real se minimiza", "la credibilidad ES el ahorro"]),
        Escenario("phillips_empinada", "κ = 0.5 (poca rigidez, θ bajo)",
                  {"kappa": 0.5},
                  "el mismo anuncio produce 2.5× más inflación: en economías de "
                  "precios ágiles la NKPC muerde fuerte — y la política enfría barato.",
                  cadena=["↓θ (m53)", "↑κ", "cada brecha mueve más los precios",
                          "π más sensible: potencia y castigo crecen juntos"]),
    ],
    verificaciones=[
        Verificacion("recursión = suma geométrica cerrada", _v_suma_cerrada),
        Verificacion("brecha permanente ⇒ π = κx/(1−β)", _v_permanente),
        Verificacion("el futuro pesa β^j exacto", _v_descuento_beta),
        Verificacion("sin brechas, π=0: cero inercia intrínseca", _v_sin_inercia),
    ],
    notas="La gemela de m54: la demanda descuenta tasas; la inflación descuenta brechas. m56 las casa.",
)
