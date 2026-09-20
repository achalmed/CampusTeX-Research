"""simuladores/estadistica/modelos/nivel_03/e38_probabilidad_frecuentista.py — la probabilidad frecuentista (sección III, tema 38).

La segunda definición de probabilidad, la que rescata los casos que la clásica
(e37) no puede: cuando los resultados NO son equiprobables o no se pueden
contar, se ESTIMA la probabilidad repitiendo el experimento muchas veces y
tomando la frecuencia relativa —P(A) = límite de #éxitos/n cuando n→∞ (e34)—.
Su poder práctico es la SIMULACIÓN DE MONTE CARLO: estimar cualquier
probabilidad (o área, o integral) tirando 'dardos' al azar. El modelo estima π
lanzando dardos a un cuadrado y contando los que caen en el cuarto de círculo,
y muestra la ley clave de la estimación por simulación: el error decrece como
1/√n —para reducirlo a la mitad hay que CUADRUPLICAR los ensayos—.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _estimar_pi(n, semilla=2024):
    """Estimación de π por Monte Carlo: 4 × fracción de dardos en el cuarto de círculo."""
    rng = np.random.default_rng(semilla)
    x = rng.random(int(n)); y = rng.random(int(n))
    dentro = (x ** 2 + y ** 2) <= 1.0
    frac = np.cumsum(dentro) / np.arange(1, int(n) + 1)
    return 4.0 * frac                                 # trayectoria de la estimación


def _curvas(p):
    N = int(p["n"])
    est = _estimar_pi(N)
    n = np.arange(1, N + 1)
    # banda de error ~ c/√n alrededor de π
    banda = 1.64 / np.sqrt(n)                          # aprox del error estándar × 4
    return {"lineas": {"estimación de π (Monte Carlo)": (n, est, config.AZUL2),
                       "π verdadero = 3.1416": (n, np.full(N, np.pi), config.ROJO),
                       "π + error ~1/√n": (n, np.pi + banda, config.GRIS)},
            "puntos": [(N, est[-1], f"n={N}: π≈{est[-1]:.3f}")],
            "anotacion": (f"P(dardo en el círculo) = área = π/4 (no equiprobable, no contable)\n"
                          f"se ESTIMA repitiendo: {N} dardos → π ≈ {est[-1]:.3f} (verdadero 3.1416)\n"
                          "el error decrece como 1/√n: cuadruplicar n lo reduce a la mitad")}


def _resultados(p):
    N = int(p["n"])
    est = _estimar_pi(N)
    # error estándar TEÓRICO del estimador: est = 4·p̂, p = π/4, Var(p̂)=p(1−p)/n
    se_teorico = 4.0 * np.sqrt((np.pi / 4) * (1 - np.pi / 4) / N)
    return {"número de dardos n": float(N),
            "estimación de π": float(est[-1]),
            "π verdadero": float(np.pi),
            "error |estimación − π| (esta corrida)": float(abs(est[-1] - np.pi)),
            "error estándar teórico  4√(p(1−p)/n)": float(se_teorico),
            "n necesario para 1 decimal más (×100)": float(N * 100),
            "P(dardo en el círculo) = π/4": float(np.pi / 4)}


def _ecuaciones_calibradas(p):
    N = int(p["n"])
    est = _estimar_pi(N)
    return [f"P(A) = \\lim_{{n\\to\\infty}} \\frac{{\\#\\,\\text{{éxitos}}}}{{n}}\\ \\text{{(definición frecuentista)}}",
            f"\\text{{error}} \\sim \\frac{{c}}{{\\sqrt{{n}}}}:\\ n{{=}}{N} \\Rightarrow \\hat\\pi = {est[-1]:.3f}\\ (\\text{{verdadero }} 3.1416)"]


_P0 = {"n": 5000}


def _v_estima_probabilidad():
    est = _estimar_pi(50000)
    return abs(est[-1] - np.pi) < 0.05, \
        (f"la probabilidad frecuentista ESTIMA por repetición: 50000 dardos dan π ≈ {est[-1]:.3f} (verdadero "
         "3.1416) — sin contar ni suponer equiprobabilidad, solo repitiendo el experimento y midiendo la frecuencia")


def _v_tasa_raiz_n():
    # la tasa 1/√n es sobre la MAGNITUD ESPERADA del error (RMS/error estándar), NO sobre
    # una corrida: el error de Monte Carlo es aleatorio y una realización aislada puede subir.
    # Se promedia sobre muchas corridas independientes y se comprueba que al cuadruplicar n
    # el error RMS se reduce ~a la mitad (factor √4 = 2).
    def rms_error(n, corridas=400, semilla=99):
        rng = np.random.default_rng(semilla)
        x = rng.random((corridas, n)); y = rng.random((corridas, n))
        est = 4.0 * ((x ** 2 + y ** 2) <= 1.0).mean(axis=1)   # una estimación por corrida
        return float(np.sqrt(np.mean((est - np.pi) ** 2)))    # error cuadrático medio
    e_n = rms_error(2500)
    e_4n = rms_error(10000)                                    # 4× los dardos
    ratio = e_n / e_4n                                         # debería ≈ 2 = √4
    return 1.6 < ratio < 2.5, \
        (f"el error decrece como 1/√n —sobre la magnitud ESPERADA, promediando 400 corridas, no una sola—: al "
         f"cuadruplicar n (2500→10000) el error RMS baja de {e_n:.4f} a {e_4n:.4f}, factor {ratio:.2f}× ≈ 2 = √4. "
         "La maldición de Monte Carlo: para UN dígito decimal más de precisión hacen falta ~100× más ensayos")


def _v_monte_carlo():
    # estimar P(suma de dos dados ≥ 10) por simulación, comparar con la clásica (6/36)
    rng = np.random.default_rng(7)
    d = rng.integers(1, 7, (100000, 2)).sum(axis=1)
    p_sim = float(np.mean(d >= 10))
    return abs(p_sim - 6 / 36) < 0.01, \
        (f"Monte Carlo estima CUALQUIER probabilidad: P(suma≥10) simulando = {p_sim:.3f} ≈ clásica 6/36 = {6/36:.3f}. "
         "Cuando contar es difícil o imposible, simular resuelve — el motor de la estadística computacional (e176)")


def _v_coincide_clasica():
    # P(dardo en el círculo) frecuentista ≈ π/4 clásica (probabilidad geométrica)
    est = _estimar_pi(50000)[-1] / 4                  # fracción en el círculo
    return abs(est - np.pi / 4) < 0.02, \
        (f"frecuentista y clásica coinciden: la fracción de dardos en el círculo ({est:.3f}) ≈ el área π/4 "
         f"({np.pi/4:.3f}) — la probabilidad geométrica (área favorable/área total) es la clásica en continuo, y la frecuencia la confirma")


MODELO = Modelo(
    id="e38", nivel=3,
    nombre="La probabilidad frecuentista (Monte Carlo)",
    xlabel="número de dardos  n", ylabel="estimación de π",
    parametros=[
        Parametro("n", _P0["n"], 100, 20000, 100, "Número de dardos (ensayos)",
                  grupo="probabilidad", definicion="más dardos, mejor estimación; el error decrece como 1/√n (lento)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando no se puede contar (resultados no equiprobables o infinitos), ¿cómo se obtiene una probabilidad?",
        variables=[("frecuencia relativa", "#éxitos / #ensayos"),
                   ("P(A)", "el límite de la frecuencia relativa cuando n→∞"),
                   ("error ~ 1/√n", "la lenta convergencia de la estimación por simulación")],
        derivacion=["\\text{clásica (e37) exige equiprobabilidad; frecuentista, no}",
                    "P(A) = \\lim_{n\\to\\infty} \\frac{\\#\\,\\text{éxitos}}{n} \\;(\\text{ley de los grandes números, e64})",
                    "\\text{estimador } \\hat P = \\frac{\\#\\,\\text{éxitos}}{n};\\ \\text{error} \\sim \\frac{1}{\\sqrt{n}}",
                    "\\text{Monte Carlo: estimar } P \\text{ (o área, integral) simulando}"],
        contexto=("La definición clásica (e37) es elegante pero frágil: se rompe en "
                  "cuanto los resultados no son equiprobables (un dado cargado, la "
                  "probabilidad de que llueva mañana, de que un paciente sane) o no "
                  "se pueden enumerar. La definición FRECUENTISTA rescata todos esos "
                  "casos con una idea sencilla y poderosa, la misma que vimos "
                  "estabilizarse en e34: la probabilidad de un evento es el valor al "
                  "que tiende su frecuencia relativa cuando el experimento se repite "
                  "indefinidamente, P(A) = lím (#éxitos / n). En la práctica no se "
                  "puede repetir infinitas veces, así que se ESTIMA con muchas: la "
                  "frecuencia observada en n ensayos es un estimador de la "
                  "probabilidad verdadera. Esta es la definición operativa que usan "
                  "las aseguradoras (estiman P(accidente) con millones de pólizas), "
                  "los epidemiólogos (P(complicación) con datos de pacientes) y "
                  "cualquiera que mida una probabilidad en el mundo real. Su "
                  "encarnación computacional es la SIMULACIÓN DE MONTE CARLO, una de "
                  "las herramientas más importantes de la ciencia moderna: para "
                  "estimar una probabilidad —o un área, o una integral, o el "
                  "resultado de un sistema complejo— se simula el experimento "
                  "miles o millones de veces y se cuenta. El modelo lo muestra "
                  "estimando π: se tiran dardos al azar en un cuadrado, y como la "
                  "probabilidad de caer dentro del cuarto de círculo inscrito es "
                  "exactamente su área, π/4, la fracción de dardos dentro, "
                  "multiplicada por 4, estima π —sin usar geometría, solo "
                  "contando—. Pero el modelo enseña también la gran LIMITACIÓN de "
                  "Monte Carlo, que hay que respetar: la convergencia es LENTA. El "
                  "error de la estimación decrece como 1/√n, lo que significa que "
                  "para DUPLICAR la precisión (un dígito más) hace falta CUADRUPLICAR "
                  "—en realidad, multiplicar por 100 para cada dígito decimal— el "
                  "número de simulaciones. Estimar π a tres decimales por Monte "
                  "Carlo requiere millones de dardos; a seis, sería inviable. Esta "
                  "tasa 1/√n no es un defecto del método sino una ley profunda —la "
                  "misma que gobierna el error estándar (e89) y el teorema central "
                  "del límite (e67)—: la precisión estadística es cara, y comprar "
                  "cada dígito extra cuesta cien veces más datos. Frecuentismo y "
                  "clasicismo no compiten: cuando ambos aplican, coinciden (la "
                  "fracción de dardos confirma el área π/4); el frecuentismo "
                  "simplemente extiende la probabilidad a donde contar no llega."),
        autores=("La definición frecuentista: John Venn (1866), Richard von Mises "
                 "(1919); Monte Carlo: Stanislaw Ulam y John von Neumann (Los "
                 "Álamos, 1940s), bautizado por el casino — menciones. Conocimiento "
                 "estadístico general."),
        supuestos=[
            "El experimento es repetible en condiciones iguales y los ensayos son independientes (e41): la frecuencia converge a la probabilidad (ley de los grandes números, e64).",
            "La estimación tiene error ~1/√n: es INSESGADA pero de convergencia LENTA; la precisión exige muchísimos ensayos (cada dígito, ~100× más).",
            "Monte Carlo requiere un buen generador de números aleatorios y saber traducir el problema a un experimento simulable (contar éxitos sobre ensayos).",
        ],
        ecuaciones=[
            Ecuacion("P(A) = \\lim_{n\\to\\infty} \\frac{\\#\\,\\text{éxitos}}{n}", "definición frecuentista",
                     "la probabilidad es el límite de la frecuencia relativa: se estima repitiendo el "
                     "experimento, sin necesidad de equiprobabilidad ni de contar."),
            Ecuacion("\\hat P = \\frac{\\#\\,\\text{éxitos}}{n}, \\quad \\text{error} \\sim \\frac{1}{\\sqrt{n}}", "estimación por simulación",
                     "la frecuencia observada estima P; el error decrece como 1/√n — lento: cada dígito extra "
                     "de precisión cuesta ~100 veces más ensayos."),
            Ecuacion("\\hat\\pi = 4 \\times \\frac{\\#\\,\\text{dardos en el círculo}}{n}", "Monte Carlo de π",
                     "como P(dardo en el círculo)=π/4, la fracción por 4 estima π: simular resuelve lo que "
                     "contar no puede — el motor de la estadística computacional."),
        ],
        intuicion=("La probabilidad frecuentista es la que le da los pies en la "
                   "tierra a la probabilidad: cuando no puedes razonar la respuesta, "
                   "la MIDES repitiendo. Es la definición del experimentador, del "
                   "actuario, del que corre simulaciones. Monte Carlo es su "
                   "superpoder: convierte problemas de matemática pura (¿cuánto vale "
                   "esta integral imposible? ¿cuál es la probabilidad de que este "
                   "sistema de mil piezas falle?) en algo tan simple como tirar "
                   "dardos y contar. Por eso es omnipresente en física, finanzas, "
                   "ingeniería e inteligencia artificial. Pero su lección más "
                   "honesta es la del costo: la tasa 1/√n es implacable. Estimar "
                   "algo a un decimal es barato; a dos, cien veces más caro; a tres, "
                   "diez mil veces. Esta 'maldición de la raíz de n' es una de las "
                   "verdades más importantes y menos apreciadas de la estadística, y "
                   "aparece en todas partes: es la razón por la que las encuestas "
                   "grandes no son mucho mejores que las medianas (duplicar la "
                   "muestra solo mejora el margen de error en un factor √2), por la "
                   "que el error estándar de la media es σ/√n (e89), y por la que la "
                   "estadística siempre tiene que elegir entre precisión y costo. "
                   "Entender que la información crece con la raíz del esfuerzo, no "
                   "linealmente, es entender por qué la certeza absoluta es "
                   "inalcanzable y por qué hay que aprender a decidir bajo "
                   "incertidumbre —de lo que trata el resto de la estadística—."),
        equilibrio=("La probabilidad frecuentista es el límite de la frecuencia "
                    "relativa (garantizado por la LGN, e64). El estimador #éxitos/n "
                    "es insesgado, con error ~1/√n (convergencia lenta). Monte Carlo "
                    "estima cualquier probabilidad/área/integral simulando. Coincide "
                    "con la clásica cuando ambas aplican. No hay 'equilibrio': es "
                    "estimación por repetición."),
        limitaciones=[
            "Convergencia LENTA (1/√n): cada dígito extra de precisión cuesta ~100× más simulaciones — Monte Carlo es versátil pero caro en precisión.",
            "Requiere repetibilidad e independencia: eventos únicos o irrepetibles (¿probabilidad de que este candidato gane esta elección específica?) no tienen frecuencia de largo plazo — ahí el enfoque bayesiano (e161) es más natural.",
            "La estimación es aleatoria: dos corridas dan resultados algo distintos; hay que reportar la incertidumbre de la propia estimación (intervalo de confianza, e92).",
        ],
        evolucion=("Formaliza la convergencia vista en e34 como DEFINICIÓN de "
                   "probabilidad y como método de ESTIMACIÓN (Monte Carlo), rescatando "
                   "los casos que la clásica (e37) no cubre. La tasa 1/√n anticipa el "
                   "error estándar (e89) y el TCL (e67). Monte Carlo es el motor de "
                   "toda la estadística computacional: bootstrap (e174), integración, "
                   "MCMC bayesiano (e170). El contraste frecuentista vs. la "
                   "probabilidad de eventos únicos abre, más adelante, el debate con "
                   "el enfoque bayesiano (e161)."),
    ),
    escenarios=[
        Escenario("pocos_dardos", "pocos dardos (n = 500): estimación burda",
                  {"n": 500},
                  "con 500 dardos, la estimación de π es aproximada y ruidosa "
                  "(puede dar 3.05 o 3.25): pocas repeticiones, mucho error. La "
                  "frecuentista necesita MUCHOS ensayos para ser precisa.",
                  cadena=["500 dardos (pocos)", "la fracción en el círculo es ruidosa",
                          "estimación de π burda (±0.1)", "el error ~1/√n aún es grande"]),
        Escenario("muchos_dardos", "muchos dardos (n = 20000): mejor, pero caro",
                  {"n": 20000},
                  "con 20000 dardos la estimación se acerca a π, pero fíjate cuánto "
                  "esfuerzo para pocos decimales: la tasa 1/√n hace que la precisión "
                  "sea cara. Para un decimal más habría que multiplicar por 100.",
                  cadena=["20000 dardos (40× más que antes)", "el error baja solo ~√40 ≈ 6×",
                          "estimación más precisa pero costosa", "la maldición de 1/√n: precisión cara"]),
    ],
    verificaciones=[
        Verificacion("estima la probabilidad repitiendo (π por Monte Carlo)", _v_estima_probabilidad),
        Verificacion("el error decrece como 1/√n (precisión cara)", _v_tasa_raiz_n),
        Verificacion("Monte Carlo estima cualquier probabilidad", _v_monte_carlo),
        Verificacion("frecuentista y clásica coinciden cuando ambas aplican", _v_coincide_clasica),
    ],
    notas="Probabilidad frecuentista: P(A)=límite de #éxitos/n (e34). Estima P repitiendo, sin equiprobabilidad. Monte Carlo: estima π (o cualquier P/área/integral) simulando. Ley clave: error ~1/√n — cada dígito extra cuesta ~100× más ensayos (precisión cara). Coincide con la clásica (e37) cuando ambas aplican.",
)
