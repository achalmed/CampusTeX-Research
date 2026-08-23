# e28_desviacion_estandar.py — la desviación estándar en uso (sección II, tema 28).
#
# Si e27 construyó la varianza y la desviación, este modelo muestra para QUÉ
# sirve la desviación en la práctica: es la "unidad de medida" natural de la
# dispersión. Dos usos centrales. (1) La REGLA EMPÍRICA: en una distribución
# aproximadamente normal, ~68% de los datos caen a ±1σ de la media, ~95% a ±2σ y
# ~99.7% a ±3σ —la regla 68-95-99.7—. (2) El PUNTAJE Z (estandarización): z =
# (x−μ)/σ expresa cada dato en "número de desviaciones respecto a la media",
# haciendo comparables variables de escalas distintas. El modelo deja mover k y
# ver qué proporción cae dentro de ±kσ, contra la cota universal de Chebyshev.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_RNG = np.random.default_rng(8)
_DATOS = _RNG.normal(0.0, 1.0, 100000)               # normal estándar (μ=0, σ=1)


def _dentro(k):
    return float(np.mean(np.abs(_DATOS) <= k))       # proporción dentro de ±kσ


def _chebyshev(k):
    return max(0.0, 1.0 - 1.0 / k ** 2) if k >= 1 else 0.0


def _densidad_normal(x):
    return np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)


def _curvas(p):
    k = p["k"]
    xs = np.linspace(-4, 4, 400)
    ys = _densidad_normal(xs)
    dentro = _dentro(k)
    return {"lineas": {"densidad normal": (xs, ys, config.AZUL2),
                       f"límites ±{k:.1f}σ": (np.array([-k, k]), np.array([0.0, 0.0]), config.ROJO)},
            "puntos": [(-k, _densidad_normal(-k), f"−{k:.1f}σ"), (k, _densidad_normal(k), f"+{k:.1f}σ")],
            "anotacion": (f"dentro de ±{k:.1f}σ cae el {dentro*100:.1f}% de los datos\n"
                          f"regla empírica (normal): ±1σ→68%, ±2σ→95%, ±3σ→99.7%\n"
                          f"Chebyshev (cualquier distribución): al menos {_chebyshev(k)*100:.0f}%")}


def _resultados(p):
    k = p["k"]
    return {"k (número de desviaciones)": float(k),
            "proporción dentro de ±kσ (normal)": _dentro(k),
            "cota de Chebyshev (cualquier dist.)": _chebyshev(k),
            "dentro de ±1σ (regla: 68%)": _dentro(1),
            "dentro de ±2σ (regla: 95%)": _dentro(2),
            "dentro de ±3σ (regla: 99.7%)": _dentro(3)}


def _ecuaciones_calibradas(p):
    k = p["k"]
    return [f"z = \\frac{{x-\\mu}}{{\\sigma}}\\ \\text{{(desviaciones respecto a la media)}};\\ \\pm{k:.1f}\\sigma \\to {_dentro(k)*100:.0f}\\%",
            f"\\text{{regla empírica}}: \\pm 1\\sigma{{\\to}}68\\%,\\ \\pm 2\\sigma{{\\to}}95\\%,\\ \\pm 3\\sigma{{\\to}}99.7\\%"]


_P0 = {"k": 1.0}


def _v_regla_empirica():
    ok = (abs(_dentro(1) - 0.68) < 0.02 and abs(_dentro(2) - 0.95) < 0.02
          and abs(_dentro(3) - 0.997) < 0.005)
    return ok, \
        (f"la REGLA EMPÍRICA 68-95-99.7 en una normal: ±1σ contiene {_dentro(1)*100:.0f}%, ±2σ {_dentro(2)*100:.0f}%, "
         f"±3σ {_dentro(3)*100:.1f}% — por eso la desviación es la 'regla de medir' de la dispersión")


def _v_z_estandariza():
    z = (_DATOS - _DATOS.mean()) / _DATOS.std()
    return abs(z.mean()) < 1e-6 and abs(z.std() - 1.0) < 1e-6, \
        (f"estandarizar z=(x−μ)/σ da media 0 y desviación 1 (dio media {z.mean():.0e}, desv {z.std():.3f}): "
         "convierte cualquier variable a 'número de desviaciones', haciendo comparables cosas de escalas distintas (notas, alturas, precios)")


def _v_chebyshev():
    # para CUALQUIER distribución, al menos 1−1/k² cae dentro de ±kσ; la normal supera esa cota
    ok = all(_dentro(k) >= _chebyshev(k) - 1e-9 for k in (1.5, 2, 3))
    return ok, \
        (f"cota de Chebyshev (sin suponer normalidad): al menos 1−1/k² dentro de ±kσ — a ±2σ, ≥75% en CUALQUIER "
         f"distribución (la normal da {_dentro(2)*100:.0f}%, más ajustado). La desviación acota la dispersión siempre")


def _v_unidades():
    c = 5.0
    return abs(float((c * _DATOS).std()) - c * float(_DATOS.std())) < 1e-6, \
        (f"la desviación está en las UNIDADES de los datos (escalar por c la multiplica por |c|): por eso —y no "
         "la varianza, en unidades²— es comparable con la media y sirve como unidad de medida (la regla empírica)")


MODELO = Modelo(
    id="e28", nivel=2,
    nombre="La desviación estándar en uso: regla empírica y puntaje z",
    xlabel="desviaciones respecto a la media  (x en unidades de σ)", ylabel="densidad",
    parametros=[
        Parametro("k", _P0["k"], 0.5, 3.5, 0.1, "Número de desviaciones ±kσ",
                  grupo="descriptiva", definicion="cuántas desviaciones alrededor de la media; ±1σ→68%, ±2σ→95%, ±3σ→99.7% (normal)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si te dicen que un dato está 'a 2 desviaciones de la media', ¿qué tan raro es? ¿Y cómo comparo cosas de escalas distintas?",
        variables=[("σ", "la desviación estándar: la 'unidad de medida' de la dispersión"),
                   ("z = (x−μ)/σ", "puntaje z: cuántas desviaciones separan a x de la media"),
                   ("±kσ", "banda de k desviaciones alrededor de la media")],
        derivacion=["\\sigma \\text{ está en las unidades de los datos} \\Rightarrow \\text{sirve de escala}",
                    "z = \\frac{x-\\mu}{\\sigma} : \\text{estandariza (media } 0, \\text{ desv } 1)",
                    "\\text{normal: } P(|z| \\le 1)\\approx 0.68,\\ P(|z|\\le 2)\\approx 0.95,\\ P(|z|\\le 3)\\approx 0.997",
                    "\\text{cualquiera (Chebyshev): } P(|z| \\le k) \\ge 1 - 1/k^2"],
        contexto=("La desviación estándar no es solo un número que resume la "
                  "dispersión (eso lo hizo e27): es la UNIDAD DE MEDIDA natural con "
                  "la que se juzga cuán lejos está un dato de lo normal, y este "
                  "modelo muestra sus dos usos que aparecen en todas partes. El "
                  "primero es la REGLA EMPÍRICA, o regla 68-95-99.7: en cualquier "
                  "distribución aproximadamente normal (y muchísimas lo son, por el "
                  "teorema central del límite, e67), alrededor del 68% de los datos "
                  "caen a menos de una desviación estándar de la media, el 95% a "
                  "menos de dos, y el 99.7% a menos de tres. Esto convierte a σ en "
                  "una regla graduada: un dato a 1σ es común, a 2σ es notable (solo "
                  "5% está más lejos), a 3σ es raro (0.3%), y a 5σ o 6σ es "
                  "prácticamente imposible por azar —de ahí que la física exija '5 "
                  "sigmas' para anunciar un descubrimiento y la industria hable de "
                  "'six sigma' para la calidad casi perfecta—. El segundo uso es la "
                  "ESTANDARIZACIÓN o puntaje z: z = (x − μ)/σ expresa cada dato como "
                  "el número de desviaciones que lo separan de la media, sin "
                  "unidades. Su poder es hacer COMPARABLES cosas incomparables: un "
                  "puntaje z permite decir si estuviste mejor en el examen de "
                  "matemáticas (donde sacaste 80 sobre media 60, desv 10, z=+2) o en "
                  "el de lenguaje (85 sobre media 82, desv 5, z=+0.6) —en "
                  "matemáticas, mucho mejor—, aunque las escalas brutas no se "
                  "parezcan. Es la operación que subyace a los tests "
                  "estandarizados, a la normalización de datos en machine learning "
                  "(e227) y a toda la inferencia (los estadísticos de prueba son "
                  "puntajes z, e106). Y para los escépticos de la normalidad, la "
                  "COTA DE CHEBYSHEV da una garantía universal, sin suponer forma "
                  "alguna: en CUALQUIER distribución, al menos 1 − 1/k² de los datos "
                  "caen dentro de ±kσ (al menos 75% a ±2σ, 89% a ±3σ) —más floja que "
                  "la regla empírica, pero siempre cierta—. En ambos casos, la "
                  "desviación estándar es la vara: sin ella, 'lejos de la media' no "
                  "significa nada."),
        autores=("La estandarización y la regla empírica: Gauss y la distribución "
                 "normal (s. XIX); la desigualdad de Chebyshev (1867), que acota sin "
                 "suponer normalidad — menciones. Conocimiento estadístico general."),
        supuestos=[
            "La REGLA EMPÍRICA (68-95-99.7) supone distribución aproximadamente NORMAL; en distribuciones muy sesgadas o de colas pesadas no aplica (ahí vale la cota de Chebyshev, universal pero más floja).",
            "El puntaje z usa la media y la desviación, así que hereda su NO robustez: un outlier infla σ y distorsiona los z (la versión robusta usa mediana y MAD, e32).",
            "Estandarizar hace comparables las POSICIONES relativas dentro de cada distribución, no las magnitudes absolutas.",
        ],
        ecuaciones=[
            Ecuacion("z = \\frac{x - \\mu}{\\sigma}", "puntaje z / estandarización",
                     "cuántas desviaciones separan a x de la media: convierte cualquier variable a una escala "
                     "sin unidades (media 0, desv 1), haciendo comparables cosas de escalas distintas."),
            Ecuacion("P(|z| \\le 1,2,3) \\approx 0.68,\\ 0.95,\\ 0.997", "regla empírica (normal)",
                     "en una normal, la desviación gradúa la rareza: a 1σ común, a 2σ notable, a 3σ raro — la "
                     "regla 68-95-99.7 que hace de σ una vara de medir."),
            Ecuacion("P(|z| \\le k) \\ge 1 - 1/k^2", "cota de Chebyshev (universal)",
                     "sin suponer normalidad, al menos 1−1/k² cae dentro de ±kσ en CUALQUIER distribución: una "
                     "garantía siempre válida, aunque más floja que la regla empírica."),
        ],
        intuicion=("La desviación estándar es la que le da sentido a la palabra "
                   "'raro'. Sin ella, saber que alguien mide 190 cm o ganó 200 no "
                   "dice nada —¿es mucho? ¿poco?—; con ella, saber que está a 2.5 "
                   "desviaciones de la media lo dice todo: está en el 1% superior. "
                   "Esa es la magia de estandarizar: traduce cualquier medida a un "
                   "idioma común —'desviaciones respecto a lo normal'— en el que "
                   "todo es comparable. Un jugador de básquet muy alto y un jugador "
                   "de fútbol muy rápido pueden compararse por su z: quién es más "
                   "excepcional en su disciplina. La regla 68-95-99.7 es la tabla de "
                   "conversión mental que todo estadístico lleva puesta: 1σ, "
                   "normalito; 2σ, ceja levantada; 3σ, esto merece explicación; 5σ, "
                   "descubrimiento o error. Y la cota de Chebyshev es la red de "
                   "seguridad para cuando no puedes suponer normalidad: aunque no "
                   "sepas nada de la forma, la desviación te garantiza que la mayoría "
                   "de los datos no puede estar muy lejos de la media —matemáticamente, "
                   "no por fe—. Toda la inferencia estadística que viene después "
                   "(pruebas de hipótesis, intervalos) es, en el fondo, aplicar esta "
                   "idea: medir qué tan lejos está lo observado de lo esperado, en "
                   "unidades de desviación (el error estándar, e89)."),
        equilibrio=("La desviación estándar es la escala de la dispersión: en una "
                    "normal, ±1/2/3σ contienen 68/95/99.7%; en cualquier "
                    "distribución, ±kσ contiene al menos 1−1/k² (Chebyshev). El "
                    "puntaje z estandariza a media 0 y desviación 1. No 'converge' a "
                    "otra cosa: es la unidad de medida de lo típico."),
        limitaciones=[
            "La regla 68-95-99.7 SOLO vale para distribuciones ~normales: con sesgo o colas pesadas engaña (ahí, Chebyshev, universal pero flojo).",
            "No robusta: el puntaje z usa μ y σ, que un outlier distorsiona (infla σ y aplasta los z) — la detección robusta usa mediana y MAD (e32).",
            "Estandarizar borra las unidades y las magnitudes: dos datos con el mismo z pueden ser muy distintos en valor absoluto; el z habla de posición relativa, no de cantidad.",
        ],
        evolucion=("Pone en uso la desviación de e27 como unidad de medida (regla "
                   "empírica) y herramienta de comparación (puntaje z), apoyándose "
                   "en la normal (e58) y anticipando por qué tantas cosas son "
                   "normales (el TCL, e67). El coeficiente de variación (e29) lleva "
                   "esta idea a la dispersión RELATIVA. La estandarización es la base "
                   "de la inferencia (los estadísticos de prueba son puntajes z, "
                   "e106) y del preprocesamiento en machine learning (e227)."),
    ),
    escenarios=[
        Escenario("una_sigma", "±1σ: lo común (regla del 68%)",
                  {"k": 1.0},
                  "dentro de ±1 desviación de la media cae ~68% de los datos: la "
                  "mayoría, lo 'normal'. Estar a menos de 1σ de la media es "
                  "estadísticamente ordinario.",
                  cadena=["mirar la banda ±1σ", "en una normal contiene ~68% de los datos",
                          "es la zona de lo común", "estar a <1σ = ordinario"]),
        Escenario("dos_sigma", "±2σ: el umbral de 'notable' (95%)",
                  {"k": 2.0},
                  "±2σ contiene ~95%: solo el 5% de los datos está más lejos. Un "
                  "dato a más de 2σ es 'notable' —el umbral clásico de significancia "
                  "(e101)—, y a 3σ ya es raro (0.3%).",
                  cadena=["mirar la banda ±2σ", "contiene ~95% (solo 5% más lejos)",
                          "un dato a >2σ es notable (raro)", "el umbral de la significancia estadística (e101)"]),
    ],
    verificaciones=[
        Verificacion("regla empírica 68-95-99.7 (normal)", _v_regla_empirica),
        Verificacion("el puntaje z estandariza (media 0, desviación 1)", _v_z_estandariza),
        Verificacion("cota de Chebyshev: ≥1−1/k² en cualquier distribución", _v_chebyshev),
        Verificacion("la desviación está en las unidades de los datos", _v_unidades),
    ],
    notas="La desviación es la 'vara' de la dispersión. Regla empírica (normal): ±1σ→68%, ±2σ→95%, ±3σ→99.7%. Puntaje z=(x−μ)/σ estandariza (media 0, desv 1) y hace comparables escalas distintas. Chebyshev: ≥1−1/k² dentro de ±kσ en CUALQUIER distribución. No robusta (usa μ, σ).",
)
