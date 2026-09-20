"""simuladores/estadistica/modelos/nivel_02/e30_asimetria.py — la asimetría (sesgo / skewness) (sección II, tema 30).

La FORMA de la distribución más allá del centro y la dispersión: ¿es simétrica
o tiene una cola larga hacia un lado? La asimetría es el tercer momento
estandarizado, γ₁ = E[(X−μ)³]/σ³. Positiva = cola a la DERECHA (pocos valores
muy altos: ingresos, precios, tiempos de espera); negativa = cola a la
izquierda; cero = simétrica. Su huella práctica, ya vista en e18, es el orden
de las medidas de centro: con sesgo a la derecha, moda < mediana < media (la
media, arrastrada por la cola, es la mayor). El modelo genera datos con sesgo
controlable y muestra las tres medidas separándose al crecer la asimetría.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_RNG_SEMILLA = 9
_N = 60000


def _datos(k):
    """Gamma(forma=k): muy sesgada si k chico, ~simétrica si k grande. Asimetría = 2/√k."""
    rng = np.random.default_rng(_RNG_SEMILLA)
    return rng.gamma(float(k), 1.0, _N)


def _asimetria(x):
    z = (x - x.mean()) / x.std()
    return float(np.mean(z ** 3))


def _moda_aprox(x):
    c, b = np.histogram(x, bins=80)
    i = int(np.argmax(c))
    return float((b[i] + b[i + 1]) / 2)


def _densidad(x, bins=90):
    d, b = np.histogram(x, bins=bins, density=True)
    return (b[:-1] + b[1:]) / 2, d


def _curvas(p):
    x = _datos(p["k"])
    cx, cy = _densidad(x)
    media, mediana, moda = float(x.mean()), float(np.median(x)), _moda_aprox(x)
    g = _asimetria(x)
    return {"lineas": {"densidad (Gamma)": (cx, cy, config.AZUL2)},
            "puntos": [(moda, 0.0, f"moda≈{moda:.1f}"), (mediana, 0.0, f"mediana={mediana:.1f}"),
                       (media, 0.0, f"media={media:.1f}")],
            "anotacion": (f"asimetría γ₁ = {g:+.2f}  ({'cola a la DERECHA' if g > 0.1 else 'simétrica' if abs(g)<=0.1 else 'cola a la izquierda'})\n"
                          f"orden: moda ({moda:.1f}) < mediana ({mediana:.1f}) < media ({media:.1f})\n"
                          "la media se va tras la cola larga (por eso media≫mediana ⇒ sesgo derecho)")}


def _resultados(p):
    x = _datos(p["k"])
    return {"forma k (Gamma)": float(p["k"]),
            "asimetría γ₁ = E[(X−μ)³]/σ³": _asimetria(x),
            "asimetría teórica 2/√k": 2 / np.sqrt(p["k"]),
            "moda (aprox)": _moda_aprox(x),
            "mediana": float(np.median(x)),
            "media": float(x.mean()),
            "media − mediana (huella del sesgo)": float(x.mean() - np.median(x))}


def _ecuaciones_calibradas(p):
    x = _datos(p["k"])
    return [f"\\gamma_1 = \\frac{{E[(X-\\mu)^3]}}{{\\sigma^3}} = {_asimetria(x):+.2f}\\ \\text{{(3er momento estandarizado)}}",
            f"\\text{{sesgo derecho}}:\\ \\text{{moda}} < \\text{{mediana}} < \\text{{media}}\\ ({_moda_aprox(x):.1f} < {np.median(x):.1f} < {x.mean():.1f})"]


_P0 = {"k": 2.0}


def _v_signo_indica_cola():
    x = _datos(2.0)                                    # muy sesgada a la derecha
    return _asimetria(x) > 0.5, \
        (f"la asimetría de una Gamma(k=2) es {_asimetria(x):+.2f} > 0: POSITIVA = cola larga a la DERECHA "
         "(pocos valores muy altos, como los ingresos). El SIGNO indica hacia dónde se estira la distribución")


def _v_simetrica_cero():
    x = _datos(60.0)                                   # k grande → casi simétrica
    return abs(_asimetria(x)) < 0.35, \
        (f"al aumentar la forma (k=60), la Gamma se vuelve casi simétrica y la asimetría → 0 ({_asimetria(x):+.2f}): "
         "una distribución simétrica tiene sesgo cero (la normal, e58, es el caso perfecto)")


def _v_orden_medidas():
    x = _datos(2.0)
    moda, mediana, media = _moda_aprox(x), float(np.median(x)), float(x.mean())
    return moda < mediana < media, \
        (f"con sesgo a la derecha: moda ({moda:.1f}) < mediana ({mediana:.1f}) < media ({media:.1f}) — la media "
         "se va tras la cola larga (e17), la mediana resiste (e18): por eso media≫mediana DELATA el sesgo")


def _v_coincide_teorica():
    x = _datos(4.0)
    return abs(_asimetria(x) - 2 / np.sqrt(4.0)) < 0.1, \
        (f"la asimetría medida ({_asimetria(x):+.2f}) coincide con la teórica de la Gamma, 2/√k = {2/np.sqrt(4.0):+.2f}: "
         "el tercer momento estandarizado captura exactamente cuánto se estira una cola respecto a la otra")


MODELO = Modelo(
    id="e30", nivel=2,
    nombre="La asimetría (sesgo)",
    xlabel="valor", ylabel="densidad",
    parametros=[
        Parametro("k", _P0["k"], 1.0, 60.0, 1.0, "Forma de la distribución (k)",
                  grupo="descriptiva", definicion="k chico → muy sesgada a la derecha; k grande → casi simétrica (asimetría→0)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando la media es mucho mayor que la mediana, ¿qué le pasa a la forma de los datos — y por qué?",
        variables=[("γ₁", "asimetría = E[(X−μ)³]/σ³ (tercer momento estandarizado)"),
                   ("cola", "el lado hacia el que se estira la distribución"),
                   ("moda, mediana, media", "su orden delata el sesgo")],
        derivacion=["\\text{momentos centrales: } \\mu_r = E[(X-\\mu)^r]",
                    "\\text{estandarizar (sin unidades): } \\gamma_1 = \\mu_3/\\sigma^3",
                    "\\gamma_1 > 0 : \\text{cola derecha} \\;;\\; \\gamma_1 < 0 : \\text{cola izquierda}",
                    "\\text{sesgo derecho} \\Rightarrow \\text{moda} < \\text{mediana} < \\text{media}"],
        contexto=("La media y la desviación describen el centro y el ancho de una "
                  "distribución, pero no su FORMA —y dos distribuciones con la misma "
                  "media y desviación pueden verse completamente distintas—. La "
                  "asimetría es la primera medida de forma: dice si la distribución "
                  "es simétrica o si tiene una COLA más larga hacia un lado. "
                  "Formalmente es el tercer momento estandarizado, γ₁ = "
                  "E[(X−μ)³]/σ³: se elevan las desviaciones al CUBO (no al cuadrado "
                  "como en la varianza), y el cubo conserva el signo, así que las "
                  "desviaciones grandes de un lado no se cancelan con las del otro "
                  "—si hay más 'peso' lejos hacia la derecha, γ₁ sale positivo—. Una "
                  "asimetría positiva significa cola a la derecha: la mayoría de los "
                  "datos se apiña a la izquierda y unos pocos valores muy altos "
                  "estiran la distribución —el patrón de los ingresos, los precios "
                  "de vivienda, los tiempos de espera, los tamaños de ciudades—. Una "
                  "asimetría negativa es lo contrario (cola izquierda: notas de un "
                  "examen fácil, edad de mortalidad). Cero es simétrica (la normal, "
                  "e58). La consecuencia práctica más importante de la asimetría es "
                  "el orden de las medidas de centro, que ya asomó en e18: en una "
                  "distribución con sesgo a la derecha, la MODA (el pico) queda a la "
                  "izquierda, la MEDIANA en el medio, y la MEDIA a la derecha, "
                  "arrastrada por la cola larga. Por eso 'media mucho mayor que "
                  "mediana' es la señal inconfundible de sesgo a la derecha, y por "
                  "eso reportar solo la media de una variable sesgada engaña: el "
                  "ingreso 'promedio' de un país es siempre mayor que el ingreso de "
                  "la persona típica (la mediana), porque los muy ricos lo estiran. "
                  "La asimetría también importa para elegir métodos: muchas técnicas "
                  "suponen simetría o normalidad, y un sesgo fuerte obliga a "
                  "transformar los datos (el logaritmo, e142, es el remedio clásico "
                  "para el sesgo derecho, porque comprime la cola)."),
        autores=("Los momentos y la asimetría: Karl Pearson (sistema de curvas y "
                 "momentos, 1890s) — mención histórica. Conocimiento estadístico "
                 "general."),
        supuestos=[
            "Datos cuantitativos; la asimetría usa el tercer momento, que exige distancias y magnitudes.",
            "Es una medida GLOBAL de forma: resume la asimetría en un número, pero no localiza dónde (una distribución puede tener rasgos asimétricos que se compensen).",
            "No es robusta: el cubo de las desviaciones amplifica los extremos, así que la asimetría muestral es muy sensible a los outliers (hay versiones robustas basadas en cuantiles).",
        ],
        ecuaciones=[
            Ecuacion("\\gamma_1 = \\frac{E[(X-\\mu)^3]}{\\sigma^3}", "asimetría (3er momento estandarizado)",
                     "el promedio de las desviaciones al CUBO, estandarizado: el cubo conserva el signo, así "
                     "que mide si hay más peso lejos hacia un lado — positivo = cola derecha."),
            Ecuacion("\\gamma_1 > 0 \\Rightarrow \\text{cola derecha}", "el signo es la dirección",
                     "positivo estira a la derecha (ingresos, precios), negativo a la izquierda, cero "
                     "simétrica: el signo de la asimetría dice hacia dónde va la cola larga."),
            Ecuacion("\\text{sesgo derecho}: \\text{moda} < \\text{mediana} < \\text{media}", "el orden delata el sesgo",
                     "con cola derecha la media (arrastrada, e17) supera a la mediana (robusta, e18), que "
                     "supera a la moda (el pico): media≫mediana es la señal del sesgo."),
        ],
        intuicion=("La asimetría es la que explica por qué 'el promedio' engaña "
                   "tanto en el mundo real: casi todo lo que importa —ingresos, "
                   "precios, tiempos, tamaños— está sesgado a la derecha, con una "
                   "cola de valores enormes que jala la media muy por encima de lo "
                   "típico. Cuando lees que el sueldo 'promedio' de una industria es "
                   "X, y sospechas que casi nadie gana X, tu intuición está "
                   "detectando asimetría: unos pocos ejecutivos con sueldos "
                   "estratosféricos inflan el promedio, y la mediana (lo que gana la "
                   "persona del medio) es mucho menor. La regla mental es simple y "
                   "poderosa: si media > mediana, hay cola a la derecha, y la "
                   "mediana es la cifra honesta; si media < mediana, cola a la "
                   "izquierda. La asimetría también es una advertencia metodológica: "
                   "el sesgo fuerte rompe los supuestos de muchas herramientas (que "
                   "esperan simetría), y el remedio clásico es transformar —tomar "
                   "logaritmos comprime la cola derecha y a menudo devuelve la "
                   "simetría—, razón por la cual los economistas trabajan con el "
                   "'log del ingreso' y los biólogos con escalas logarítmicas. Ver "
                   "la forma antes de resumir, y elegir la medida y la transformación "
                   "según esa forma, es lo que distingue el análisis honesto del "
                   "automático."),
        equilibrio=("La asimetría γ₁ es cero para distribuciones simétricas, positiva "
                    "para cola derecha, negativa para izquierda. Determina el orden "
                    "moda-mediana-media (con sesgo derecho, en ese orden creciente). "
                    "No es robusta (el cubo amplifica outliers). No hay 'equilibrio': "
                    "es un descriptor de forma."),
        limitaciones=[
            "No robusta: el cubo de las desviaciones magnifica los extremos, así que un outlier puede dominar la asimetría muestral (hay versiones robustas por cuantiles).",
            "Medida global: un solo número no dice DÓNDE está la asimetría; distribuciones distintas pueden compartir γ₁.",
            "Sensible al tamaño de muestra: con pocos datos, la asimetría muestral es muy variable y poco fiable (los momentos altos necesitan muchos datos).",
        ],
        evolucion=("Añade la primera medida de FORMA (tras centro, e17-e19, y "
                   "dispersión, e27-e29), formalizando el orden moda-mediana-media "
                   "de e18. Su compañera es la CURTOSIS (e31, cuarto momento: colas "
                   "y pico). Motiva la transformación logarítmica (e142) y la "
                   "distribución lognormal (e59). La detección de asimetría es clave "
                   "para elegir entre media y mediana (e18), para leer distribuciones "
                   "de ingreso (e25) y para verificar supuestos de normalidad "
                   "(e122, Shapiro-Wilk) antes de aplicar métodos paramétricos."),
    ),
    escenarios=[
        Escenario("muy_sesgada", "fuerte sesgo a la derecha (k = 2)",
                  {"k": 2.0},
                  "con k=2 la distribución tiene una cola larga a la derecha "
                  "(asimetría ≈ +1.4): la mayoría de los datos abajo, unos pocos muy "
                  "altos. Media ≫ mediana ≫ moda — el patrón de los ingresos.",
                  cadena=["forma k=2 (muy sesgada)", "cola larga a la derecha (γ₁≈+1.4)",
                          "unos pocos valores muy altos estiran la media", "moda < mediana < media (ingresos)"]),
        Escenario("casi_simetrica", "casi simétrica (k = 50)",
                  {"k": 50.0},
                  "con k grande la Gamma se acerca a una normal: la asimetría → 0 y "
                  "las tres medidas de centro casi coinciden. Cuando media ≈ mediana "
                  "≈ moda, la distribución es simétrica y da igual cuál reportar.",
                  cadena=["forma k=50 (casi simétrica)", "asimetría → 0 (por el TCL, e67)",
                          "media ≈ mediana ≈ moda", "distribución simétrica — cualquier medida sirve"]),
    ],
    verificaciones=[
        Verificacion("el signo indica la cola (sesgo derecho → γ₁>0)", _v_signo_indica_cola),
        Verificacion("simétrica → asimetría ≈ 0", _v_simetrica_cero),
        Verificacion("sesgo derecho: moda < mediana < media", _v_orden_medidas),
        Verificacion("γ₁ coincide con la teórica (2/√k de la Gamma)", _v_coincide_teorica),
    ],
    notas="Asimetría γ₁=E[(X−μ)³]/σ³ (3er momento): +cola derecha (ingresos), −izquierda, 0 simétrica. El cubo conserva el signo. Huella: sesgo derecho ⇒ moda<mediana<media, así que media≫mediana lo delata. No robusta. Remedio: log (e142).",
)
