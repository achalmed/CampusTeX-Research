"""simuladores/estadistica/modelos/nivel_03/e34_experimentos_aleatorios.py — experimentos aleatorios (sección III, tema 34).

La puerta de entrada a la probabilidad. Un experimento aleatorio es aquel cuyo
resultado individual NO se puede predecir (lanzar una moneda, un dado), pero
cuyo comportamiento COLECTIVO, al repetirlo muchas veces, es sorprendentemente
estable y predecible. Esa es la paradoja fundadora de la probabilidad: del
desorden de cada tirada emerge un orden en el agregado. El modelo lanza una
moneda (posiblemente sesgada) miles de veces y muestra cómo la frecuencia
relativa —caótica al principio— se estabiliza en la probabilidad verdadera. Es
la intuición que la sección V (ley de los grandes números, e64) formalizará.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_N = 2000                                            # número de lanzamientos
_RNG_SEMILLA = 12


def _trayectoria(p):
    """Frecuencia relativa acumulada de 'cara' a lo largo de N lanzamientos."""
    rng = np.random.default_rng(_RNG_SEMILLA)
    caras = (rng.random(_N) < p).astype(float)
    return np.cumsum(caras) / np.arange(1, _N + 1)


def _curvas(p):
    prob = p["p"]
    frec = _trayectoria(prob)
    n = np.arange(1, _N + 1)
    return {"lineas": {"frecuencia relativa de cara (acumulada)": (n, frec, config.AZUL2),
                       f"probabilidad verdadera = {prob:.2f}": (n, np.full(_N, prob), config.ROJO)},
            "puntos": [(10, frec[9], f"n=10: {frec[9]:.2f} (errático)"),
                       (_N, frec[-1], f"n={_N}: {frec[-1]:.3f} (≈{prob:.2f})")],
            "anotacion": (f"una moneda con P(cara) = {prob:.2f}, lanzada {_N} veces\n"
                          f"cada lanzamiento es impredecible, pero la frecuencia se ESTABILIZA en {prob:.2f}\n"
                          "del azar individual emerge un patrón colectivo (→ ley de los grandes números, e64)")}


def _resultados(p):
    prob = p["p"]
    frec = _trayectoria(prob)
    return {"probabilidad verdadera P(cara)": prob,
            "frecuencia tras 10 lanzamientos": float(frec[9]),
            "frecuencia tras 100 lanzamientos": float(frec[99]),
            "frecuencia tras 2000 lanzamientos": float(frec[-1]),
            "error a los 10 (|frec − p|)": float(abs(frec[9] - prob)),
            "error a los 2000 (|frec − p|)": float(abs(frec[-1] - prob))}


def _ecuaciones_calibradas(p):
    prob = p["p"]
    frec = _trayectoria(prob)
    return [f"\\text{{frecuencia relativa}} = \\frac{{\\#\\,\\text{{caras}}}}{{n}} \\longrightarrow P(\\text{{cara}}) = {prob:.2f}\\ (n\\to\\infty)",
            f"n=10:\\ {frec[9]:.2f}\\ \\text{{(errático)}};\\quad n={_N}:\\ {frec[-1]:.3f}\\ \\text{{(estable)}}"]


_P0 = {"p": 0.5}


def _v_estabiliza_en_p():
    prob = 0.5
    frec = _trayectoria(prob)
    return abs(frec[-1] - prob) < 0.03, \
        (f"la frecuencia relativa se ESTABILIZA en la probabilidad verdadera: tras {_N} lanzamientos de una "
         f"moneda justa da {frec[-1]:.3f} ≈ 0.50 — del azar de cada tirada emerge un patrón colectivo estable")


def _v_corto_plazo_erratico():
    prob = 0.5
    frec = _trayectoria(prob)
    return abs(frec[9] - prob) > abs(frec[-1] - prob), \
        (f"a corto plazo es ERRÁTICO: con 10 lanzamientos la frecuencia ({frec[9]:.2f}) puede estar lejos de 0.50; "
         "con muchos se acerca. Por eso 'la ley de los promedios' del corto plazo (creer que tras varias caras 'toca' sello) es una FALACIA (e68)")


def _v_error_decrece():
    prob = 0.5
    frec = _trayectoria(prob)
    err10 = abs(frec[9] - prob)
    err2000 = abs(frec[-1] - prob)
    return err2000 < err10, \
        (f"el error decrece con n: |frec−p| baja de {err10:.2f} (n=10) a {err2000:.3f} (n={_N}) — más repeticiones, "
         "más cerca de la probabilidad verdadera; es la esencia de la definición frecuentista (e38) y de la LGN (e64)")


def _v_sesgada_converge_a_su_p():
    prob = 0.8
    frec = _trayectoria(prob)
    return abs(frec[-1] - prob) < 0.03, \
        (f"con una moneda SESGADA (P(cara)=0.8), la frecuencia converge a 0.8 ({frec[-1]:.3f}), no a 0.5: la "
         "estabilización es hacia la probabilidad VERDADERA, sea cual sea — el experimento revela su propia ley")


MODELO = Modelo(
    id="e34", nivel=3,
    nombre="Experimentos aleatorios",
    xlabel="número de lanzamientos  n", ylabel="frecuencia relativa de cara",
    parametros=[
        Parametro("p", _P0["p"], 0.1, 0.9, 0.05, "Probabilidad verdadera de cara",
                  grupo="probabilidad", definicion="la moneda puede estar sesgada; la frecuencia converge a este valor, no siempre a 0.5"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="No puedo predecir un lanzamiento de moneda, pero puedo predecir 10.000 con precisión. ¿Cómo emerge orden del azar?",
        variables=[("experimento aleatorio", "proceso de resultado individual impredecible"),
                   ("frecuencia relativa", "# de éxitos / # de intentos"),
                   ("P(A)", "probabilidad: el valor al que la frecuencia se estabiliza")],
        derivacion=["\\text{un ensayo: resultado impredecible (cara o sello)}",
                    "n \\text{ ensayos: frecuencia relativa} = \\tfrac{\\#\\,\\text{éxitos}}{n}",
                    "n \\to \\infty : \\text{frecuencia} \\to P(A) \\;(\\text{estable})",
                    "\\text{orden colectivo a partir del azar individual}"],
        contexto=("La probabilidad nace de una observación que parece "
                  "contradictoria: hay fenómenos cuyo resultado individual es "
                  "completamente impredecible pero cuyo comportamiento agregado es "
                  "asombrosamente regular. No puedes saber si la próxima moneda "
                  "caerá cara o sello —si pudieras, no sería aleatorio—, y sin "
                  "embargo puedes afirmar con enorme confianza que en un millón de "
                  "lanzamientos habrá cerca de medio millón de caras. Un experimento "
                  "ALEATORIO es precisamente eso: un proceso que se puede repetir en "
                  "condiciones similares, cuyo resultado particular no está "
                  "determinado, pero cuyos resultados posibles se conocen y cuya "
                  "distribución de largo plazo es estable. Lanzar una moneda, tirar "
                  "un dado, extraer una carta, medir cuántos clientes llegan en una "
                  "hora, observar si un paciente responde a un tratamiento: todos "
                  "son experimentos aleatorios. La probabilidad es la disciplina que "
                  "estudia esa regularidad oculta en el azar. El modelo lo hace "
                  "visible con el ejemplo más simple, la moneda: al graficar la "
                  "frecuencia relativa de caras a medida que se acumulan los "
                  "lanzamientos, se ve el fenómeno central —al principio la "
                  "frecuencia salta de forma errática (con 10 lanzamientos puede dar "
                  "0.3 o 0.7 sin problema), pero conforme n crece, se va calmando y "
                  "converge hacia la probabilidad verdadera—. Esta convergencia de "
                  "la frecuencia hacia la probabilidad es la intuición que funda "
                  "TODA la probabilidad y la estadística: es lo que permite estimar "
                  "probabilidades desconocidas repitiendo experimentos (la "
                  "definición frecuentista, e38), lo que la ley de los grandes "
                  "números formaliza (e64), y lo que hace que las muestras "
                  "'representen' a las poblaciones (e02). Y trae una advertencia "
                  "crucial: la estabilidad es de LARGO plazo. A corto plazo el azar "
                  "es caprichoso, y creer que 'tras cuatro caras seguidas toca "
                  "sello' —la falacia del jugador— es malentender por completo cómo "
                  "funciona: la moneda no tiene memoria, cada lanzamiento es "
                  "independiente (e41), y la ley de los grandes números no 'corrige' "
                  "los desvíos, simplemente los diluye con muchísimos ensayos más."),
        autores=("La probabilidad como estudio del azar regular: de los juegos de "
                 "dados (Cardano, s. XVI; Pascal y Fermat, 1654) a su formalización "
                 "(Kolmogórov, 1933) — menciones. Conocimiento estadístico general."),
        supuestos=[
            "El experimento es REPETIBLE en condiciones esencialmente iguales y sus ensayos son INDEPENDIENTES (e41): la moneda no tiene memoria.",
            "El resultado individual es impredecible pero el conjunto de resultados posibles (el espacio muestral, e35) se conoce.",
            "La regularidad es de LARGO plazo: a corto plazo la frecuencia es errática; la estabilización requiere muchas repeticiones.",
        ],
        ecuaciones=[
            Ecuacion("\\text{frecuencia relativa} = \\frac{\\#\\,\\text{éxitos}}{n}", "frecuencia relativa",
                     "la proporción de veces que ocurre el evento en n ensayos: caótica con n pequeño, "
                     "estable con n grande."),
            Ecuacion("\\frac{\\#\\,\\text{éxitos}}{n} \\longrightarrow P(A) \\;(n\\to\\infty)", "convergencia a la probabilidad",
                     "la frecuencia relativa se estabiliza en la probabilidad verdadera: la regularidad "
                     "oculta en el azar, base de toda la estadística."),
            Ecuacion("\\text{cada ensayo independiente (sin memoria)}", "no hay 'ley de promedios' de corto plazo",
                     "la moneda no recuerda las tiradas previas; la estabilización diluye los desvíos con más "
                     "ensayos, no los compensa — la falacia del jugador (e68)."),
        ],
        intuicion=("El experimento aleatorio encierra la idea más profunda y más "
                   "contraintuitiva de toda la estadística: que el azar tiene leyes. "
                   "Parece un oxímoron —si es azar, ¿cómo va a ser predecible?—, pero "
                   "la resolución es que la predictibilidad no está en el evento "
                   "individual sino en el AGREGADO. Es como un río: no puedes "
                   "predecir el camino de una gota, pero el caudal del río es "
                   "estable y medible. Esa dualidad —caos individual, orden "
                   "colectivo— es lo que permite que existan las casas de apuestas y "
                   "las aseguradoras (no saben si TÚ tendrás un accidente, pero saben "
                   "con precisión cuántos de sus millones de asegurados lo tendrán), "
                   "las encuestas (no saben cómo votarás tú, pero estiman el "
                   "resultado con una muestra), y la física estadística entera. La "
                   "trampa mental que hay que desarmar es la falacia del jugador: "
                   "creer que el azar 'se acuerda' y 'compensa'. No lo hace. Si "
                   "salieron diez caras seguidas, la probabilidad de cara en la "
                   "próxima sigue siendo 0.5 —la moneda no tiene memoria ni sentido "
                   "de justicia—. La frecuencia converge a 0.5 no porque los sellos "
                   "'apuren' para emparejar, sino porque diez caras extra se vuelven "
                   "insignificantes cuando el denominador llega a millones. Entender "
                   "esto —que la estabilidad es asintótica y sin memoria— es el "
                   "primer paso para pensar con probabilidad en vez de con "
                   "supersticiones."),
        equilibrio=("No hay equilibrio que resolver: hay convergencia. La frecuencia "
                    "relativa de un experimento aleatorio se estabiliza en su "
                    "probabilidad verdadera conforme crece el número de ensayos "
                    "independientes, sea cual sea esa probabilidad (0.5 para una "
                    "moneda justa, otra para una sesgada). La estabilidad es de largo "
                    "plazo; el corto plazo es errático."),
        limitaciones=[
            "La regularidad exige repetibilidad e independencia: experimentos que cambian las condiciones o cuyos ensayos se influyen (rachas reales, contagio) no convergen tan limpiamente.",
            "Es una intuición, no una demostración: que la frecuencia converge se prueba en la ley de los grandes números (e64), bajo supuestos precisos.",
            "No dice NADA del corto plazo: la frecuencia con pocos ensayos es engañosa, y confundir el largo con el corto plazo es la raíz de la falacia del jugador y de sobreinterpretar muestras pequeñas.",
        ],
        evolucion=("Abre la probabilidad estableciendo su objeto —el azar regular— y "
                   "su intuición central —la frecuencia converge a la probabilidad—. "
                   "De aquí se despliega la maquinaria: el espacio muestral (e35) y "
                   "los eventos (e36) formalizan los resultados; las definiciones "
                   "clásica (e37) y frecuentista (e38) dan valor a P; la convergencia "
                   "que aquí se ve se prueba en la ley de los grandes números (e64) y "
                   "se refina en el teorema central del límite (e67). La "
                   "independencia (e41) y la advertencia contra la falacia del "
                   "jugador quedan planteadas."),
    ),
    escenarios=[
        Escenario("moneda_justa", "moneda justa (p = 0.5)",
                  {"p": 0.5},
                  "con una moneda justa, la frecuencia de caras baila alrededor de "
                  "0.5 y se va calmando hacia ese valor: el caso simétrico, la "
                  "intuición básica del azar equilibrado.",
                  cadena=["moneda justa P(cara)=0.5", "cada lanzamiento impredecible",
                          "la frecuencia oscila y se estabiliza en 0.5", "orden colectivo del azar simétrico"]),
        Escenario("moneda_sesgada", "moneda sesgada (p = 0.8)",
                  {"p": 0.8},
                  "con una moneda cargada (80% caras), la frecuencia converge a 0.8, "
                  "no a 0.5: la estabilización es hacia la probabilidad VERDADERA, "
                  "sea cual sea. Repetir el experimento revela su ley oculta — la "
                  "base de estimar probabilidades desconocidas (e38).",
                  cadena=["moneda sesgada P(cara)=0.8", "cada lanzamiento sigue impredecible",
                          "la frecuencia converge a 0.8 (no a 0.5)", "el experimento revela su probabilidad verdadera"]),
    ],
    verificaciones=[
        Verificacion("la frecuencia se estabiliza en la probabilidad verdadera", _v_estabiliza_en_p),
        Verificacion("a corto plazo es errático (falacia del jugador, e68)", _v_corto_plazo_erratico),
        Verificacion("el error decrece con el número de ensayos", _v_error_decrece),
        Verificacion("una moneda sesgada converge a SU probabilidad", _v_sesgada_converge_a_su_p),
    ],
    notas="Experimento aleatorio: resultado individual impredecible, comportamiento colectivo estable. La frecuencia relativa converge a la probabilidad verdadera (base de e38 y de la LGN, e64). Estabilidad de LARGO plazo: el corto plazo es errático, y creer que 'toca' compensar es la falacia del jugador (moneda sin memoria, e41).",
)
