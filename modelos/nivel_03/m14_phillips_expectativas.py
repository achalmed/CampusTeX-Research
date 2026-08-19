# m14_phillips_expectativas.py — Phillips aumentada por expectativas (nivel 3).
#
# Expectativas ADAPTATIVAS: πe_t = π_{t−1}. La curva se vuelve dinámica:
#   π_t = π_{t−1} − α(u − un)   →   Δπ = α(un − u)  por período
# Mantener u < un no compra un punto del menú: compra ACELERACIÓN permanente
# de la inflación (hipótesis aceleracionista). En u = un, π se queda donde
# esté — la curva de largo plazo es vertical.
#
# Procedencia: Friedman (1968, discurso presidencial AEA) y Phelps (1967) —
# menciones históricas de conocimiento general, no verificadas contra fuente.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _simular(p):
    T = int(round(p["T"]))
    pi = np.empty(T + 1)
    pi[0] = p["pi0"]
    for t in range(1, T + 1):
        pi[t] = pi[t - 1] + p["alpha"] * (p["un"] - p["u_mantenida"])
    return np.arange(T + 1), pi


def _curvas(p):
    t, pi = _simular(p)
    pe = np.concatenate(([p["pi0"]], pi[:-1]))          # πe_t = π_{t−1}
    return {"lineas": {"inflación $\\pi_t$": (t, pi, config.AZUL2),
                       "expectativas $\\pi^e_t = \\pi_{t-1}$": (t, pe, config.ROJO),
                       "$\\pi_0$ inicial": (t, np.full_like(pi, p["pi0"]), config.GRIS)},
            "equilibrio": (float(t[-1]), float(pi[-1])),
            "anotacion": (f"$u$ mantenida $= {p['u_mantenida']:.1f}\\%$  ($u_n = {p['un']:.1f}\\%$)\n"
                          f"$\\Delta\\pi$ por período $= \\alpha(u_n-u) = "
                          f"{p['alpha'] * (p['un'] - p['u_mantenida']):+.2f}$ pp\n"
                          f"$\\pi$ tras {int(p['T'])} períodos: ${pi[-1]:.1f}\\%$")}


def _resultados(p):
    _, pi = _simular(p)
    return {"π final (%)": float(pi[-1]),
            "Δπ por período (pp)": p["alpha"] * (p["un"] - p["u_mantenida"]),
            "brecha u − un (pp)": p["u_mantenida"] - p["un"],
            "πe final (%)": float(pi[-2]) if len(pi) > 1 else p["pi0"],
            "π acumulada sobre la inicial (pp)": float(pi[-1]) - p["pi0"]}


_P0 = {"alpha": 1.5, "un": 6.0, "u_mantenida": 5.0, "pi0": 2.0, "T": 15.0}


def _v_aceleracion():
    _, pi = _simular(_P0)
    dpi = np.diff(pi)
    teo = _P0["alpha"] * (_P0["un"] - _P0["u_mantenida"])
    return bool(np.all(np.abs(dpi - teo) < 1e-12)), (f"aceleración constante de {teo:+.2f} pp por "
                                                     "período mientras u < un (aceleracionista)")


def _v_natural_estable():
    _, pi = _simular(dict(_P0, u_mantenida=_P0["un"]))
    return bool(np.all(np.abs(pi - _P0["pi0"]) < 1e-12)), ("en u = un la inflación se queda donde está: "
                                                           "la Phillips de largo plazo es VERTICAL")


def _v_desinflacion_simetrica():
    _, pi_frio = _simular(dict(_P0, u_mantenida=7.0))
    _, pi_calor = _simular(dict(_P0, u_mantenida=5.0))
    d_frio, d_calor = pi_frio[-1] - pi_frio[0], pi_calor[-1] - pi_calor[0]
    return abs(d_frio + d_calor) < 1e-9, ("la desinflación es el espejo exacto: enfriar 1 pp de u "
                                          "por encima de un desinfla lo que 1 pp por debajo infla")


MODELO = Modelo(
    id="m14", nivel=3,
    nombre="Phillips aumentada por expectativas",
    xlabel="Período $t$", ylabel="Inflación $\\pi$ (%)",
    parametros=[
        Parametro("u_mantenida", _P0["u_mantenida"], 3.0, 9.0, 0.25, "Desempleo que la política mantiene"),
        Parametro("un", _P0["un"], 4.0, 8.0, 0.5, "Tasa natural un"),
        Parametro("alpha", _P0["alpha"], 0.3, 3.0, 0.1, "Sensibilidad α"),
        Parametro("pi0", _P0["pi0"], 0.0, 10.0, 0.5, "Inflación inicial π0"),
        Parametro("T", _P0["T"], 5, 40, 1, "Períodos simulados"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Qué pasa con la inflación si la política intenta sostener el "
                  "desempleo por debajo de su tasa natural?"),
        contexto=("En 1967-68, con la Phillips original en su apogeo, Friedman y Phelps "
                  "predijeron su colapso: los trabajadores negocian salarios REALES, así "
                  "que la inflación pasada se incorpora a las expectativas y la curva se "
                  "desplaza hacia arriba. Mantener el desempleo bajo la tasa natural "
                  "exigiría sorprender a la gente con inflación cada vez MAYOR. Los 70 "
                  "les dieron la razón punto por punto — una de las predicciones "
                  "teóricas más exitosas de la macroeconomía."),
        autores=("Friedman (1968, 'The Role of Monetary Policy'); Phelps (1967), "
                 "independientemente. La hipótesis de la tasa natural es de ambos; la "
                 "aplicación desinflacionaria célebre es Volcker (Fed, 1979-82)."),
        supuestos=[
            "Expectativas ADAPTATIVAS: πe_t = π_{t−1} (se aprende del pasado, con un período de rezago).",
            "La tasa natural un es un ancla real que la política de demanda no puede mover.",
            "α estable (la estructura de negociación salarial no cambia con el régimen — supuesto que Lucas atacará, m42).",
        ],
        ecuaciones=[
            Ecuacion("\\pi_t = \\pi_{t-1} - \\alpha\\,(u - u_n)", "Phillips con expectativas adaptativas",
                     "la Phillips de m13 con πe = π_{t−1}: la curva de corto plazo se re-dibuja "
                     "cada período a la altura de la inflación heredada."),
            Ecuacion("\\Delta\\pi = \\alpha\\,(u_n - u)", "hipótesis aceleracionista",
                     "u < un no fija una inflación ALTA sino una inflación CRECIENTE: el menú de "
                     "m13 solo existe mientras la gente no aprende."),
            Ecuacion("u = u_n \\;\\Rightarrow\\; \\pi_t = \\pi_{t-1}", "Phillips de largo plazo vertical",
                     "cualquier inflación es compatible con u = un: a largo plazo no hay trade-off "
                     "que explotar."),
        ],
        intuicion=("El menú de m13 era una ilusión óptica de corto plazo: funcionaba "
                   "solo mientras la inflación efectiva superara a la esperada. En "
                   "cuanto las expectativas alcanzan a la realidad, hace falta MÁS "
                   "inflación para la misma sorpresa — la espiral de los 70. La lectura "
                   "inversa es igual de dura: desinflar exige mantener u > un por un "
                   "tiempo (la recesión de Volcker), y ese costo es la tasa de "
                   "sacrificio."),
        equilibrio=("El único reposo inflacionario es u = un (π constante en cualquier "
                    "nivel). Fuera de ahí, π sigue una escalera sin techo ni piso: el "
                    "proceso es inestable por diseño — esa inestabilidad ES el mensaje."),
        limitaciones=[
            "Las expectativas adaptativas son mecánicas: si la política es sistemática, agentes racionales la anticipan y el trade-off desaparece aún más rápido (Lucas, m42; Sargent sobre el fin de hiperinflaciones).",
            "un no es observable y se mueve (histéresis: recesiones largas pueden SUBIR la tasa natural — Blanchard-Summers, mención).",
            "La relación lineal exagera: con inflación muy baja la curva parece aplanarse (debate post-2008).",
        ],
        evolucion=("De aquí salen tres rutas del currículo: la crítica de expectativas "
                   "racionales (m42), la curva de Phillips nuevo keynesiana con "
                   "expectativas FORWARD-looking (m55), y la maquinaria de "
                   "desinflación con credibilidad (m40-m41) que el BCRP aplica desde "
                   "2002 con metas de inflación."),
    ),
    escenarios=[
        Escenario("espiral_de_los_70", "mantener u=5% (1 pp bajo la natural) 15 períodos",
                  {"u_mantenida": 5.0},
                  "la inflación sube 1.5 pp CADA período: de 2% a 24.5% — la espiral que "
                  "convirtió el menú de los 60 en la pesadilla de los 70.",
                  cadena=["u < un sostenido", "π sorprende a πe", "πe = π_{t−1} se revisa al alza",
                          "la curva de CP se desplaza", "π acelera α(un−u) CADA período"]),
        Escenario("volcker", "recesión deliberada: u=8% hasta domar la inflación",
                  {"u_mantenida": 8.0, "pi0": 10.0},
                  "π baja 3 pp por período desde 10%: la desinflación funciona, pero su "
                  "precio en desempleo acumulado es la tasa de sacrificio.",
                  cadena=["u > un sostenido", "π queda bajo πe", "expectativas se revisan a la baja",
                          "desinflación de α(u−un) por período", "costo acumulado = sacrificio"]),
        Escenario("en_la_natural", "la política respeta un: u = 6%",
                  {"u_mantenida": 6.0},
                  "π se queda exactamente en π0 para siempre: cualquier inflación es "
                  "estable en un — por eso el largo plazo es vertical.",
                  cadena=["u = un", "sin sorpresas de precios", "πe alcanza a π",
                          "π constante en π0", "Phillips de largo plazo VERTICAL"]),
    ],
    verificaciones=[
        Verificacion("aceleración constante α(un−u)", _v_aceleracion),
        Verificacion("en u=un la inflación no se mueve (LP vertical)", _v_natural_estable),
        Verificacion("desinflación simétrica a la inflación", _v_desinflacion_simetrica),
    ],
    notas="Primer modelo DINÁMICO del laboratorio: el eje x ya no es un mercado sino el tiempo.",
)
