"""simuladores/estadistica/modelos/nivel_02/e17_media_aritmetica.py — la media aritmética (sección II, tema 17).

El primer estadístico descriptivo, y más profundo de lo que parece. La media
no es "la fórmula de sumar y dividir": es el CENTRO DE MASA de los datos (las
desviaciones a un lado y otro se cancelan exactamente, Σ(xᵢ−x̄)=0) y el punto
que MINIMIZA la suma de errores al cuadrado (x̄ = argmin_a Σ(xᵢ−a)²). Esta
segunda propiedad es la semilla de los mínimos cuadrados y de toda la regresión
(sec. XI): la media es la "regresión sin predictores". El modelo deja mover un
candidato de centro `a` y ver que el error cuadrático es mínimo justo en x̄.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_DATOS = np.array([3, 5, 6, 8, 9, 11, 14], float)   # n=7, suma=56, x̄=8.0 (media limpia)
_XBAR = float(_DATOS.mean())
_N = len(_DATOS)


def _sse(a):
    return float(np.sum((_DATOS - a) ** 2))


def _curvas(p):
    a = p["a"]
    grid = np.linspace(_XBAR - 6, _XBAR + 6, 120)
    sse = np.array([_sse(x) for x in grid])
    return {"lineas": {"error cuadrático total  $\\sum (x_i-a)^2$": (grid, sse, config.AZUL2)},
            "puntos": [(_XBAR, _sse(_XBAR), f"mínimo en x̄ = {_XBAR:.1f}"),
                       (a, _sse(a), f"tu a = {a:.1f}")]
                      + [(float(x), 0.0, "") for x in _DATOS],
            "anotacion": (f"datos: {', '.join(str(int(x)) for x in _DATOS)}   →   x̄ = {_XBAR:.1f}\n"
                          f"$\\sum (x_i-\\bar x) = 0$ (centro de masa)\n"
                          f"x̄ MINIMIZA el error cuadrático: SSE(x̄)={_sse(_XBAR):.0f} ≤ SSE(a)={_sse(a):.0f}")}


def _resultados(p):
    a = p["a"]
    return {"media x̄": _XBAR,
            "n": float(_N),
            "suma Σxᵢ": float(_DATOS.sum()),
            "n·x̄ (= Σxᵢ)": float(_N * _XBAR),
            "Σ(xᵢ−x̄) (desviaciones)": float(np.sum(_DATOS - _XBAR)),
            "SSE en tu a: Σ(xᵢ−a)²": _sse(a),
            "SSE en x̄ (mínimo)": _sse(_XBAR)}


def _ecuaciones_calibradas(p):
    return [f"\\bar x = \\frac{{1}}{{{_N}}}\\sum x_i = \\frac{{{int(_DATOS.sum())}}}{{{_N}}} = {_XBAR:.1f}",
            f"\\sum (x_i-\\bar x) = 0 \\qquad \\bar x = \\arg\\min_a \\sum (x_i-a)^2\\ \\text{{(mínimos cuadrados)}}"]


_P0 = {"a": 8.0}


def _v_desviaciones_cero():
    s = float(np.sum(_DATOS - _XBAR))
    return abs(s) < 1e-9, \
        (f"la suma de las desviaciones respecto a la media es EXACTAMENTE cero (Σ(xᵢ−x̄)={s:.2e}): "
         "la media es el CENTRO DE MASA — lo que sobra a un lado falta al otro, se equilibra")


def _v_suma():
    return abs(float(_DATOS.sum()) - _N * _XBAR) < 1e-9, \
        (f"Σxᵢ = n·x̄ (={int(_DATOS.sum())} = {_N}×{_XBAR:.1f}): la media reparte el total por igual entre las "
         "n observaciones — es el 'valor equitativo' que todos tendrían si el total se repartiera parejo")


def _v_minimiza_sse():
    # x̄ es el argmin de Σ(xᵢ−a)²: SSE sube a ambos lados
    mejor = _sse(_XBAR)
    peor_izq, peor_der = _sse(_XBAR - 0.5), _sse(_XBAR + 0.5)
    grid = np.linspace(_XBAR - 6, _XBAR + 6, 2401)
    argmin = grid[int(np.argmin([_sse(x) for x in grid]))]
    return mejor < peor_izq and mejor < peor_der and abs(argmin - _XBAR) < 0.01, \
        (f"la media MINIMIZA la suma de errores al cuadrado: argmin_a Σ(xᵢ−a)² = {argmin:.2f} = x̄ = {_XBAR:.1f}. "
         "Es la semilla de los mínimos cuadrados y la regresión (sec. XI): la media es la regresión sin predictores")


def _v_sensible_atipico():
    # añadir un dato extremo mueve la media (x̄' = (Σx + z)/(n+1)); 0% de robustez
    z = 100.0
    x_nuevo = float((_DATOS.sum() + z) / (_N + 1))
    predicho = float((_DATOS.sum() + z) / (_N + 1))
    return x_nuevo > _XBAR + 5 and abs(x_nuevo - predicho) < 1e-9, \
        (f"un solo dato extremo (100) arrastra la media de {_XBAR:.1f} a {x_nuevo:.1f}: la media NO es robusta "
         "(punto de ruptura 0%) — un outlier la mueve sin límite. Por eso existe la mediana (e18) y las medidas robustas (e32)")


MODELO = Modelo(
    id="e17", nivel=2,
    nombre="La media aritmética",
    xlabel="candidato de centro  a", ylabel="error cuadrático total",
    parametros=[
        Parametro("a", _P0["a"], 2.0, 14.0, 0.5, "Candidato de centro a",
                  grupo="descriptiva", definicion="valor de prueba; el error cuadrático Σ(xᵢ−a)² es mínimo en a=x̄"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Qué es exactamente 'el promedio' — y por qué es el mejor resumen de un conjunto de datos… salvo cuando no lo es?",
        variables=[("x₁,…,xₙ", "los datos"),
                   ("x̄", "media aritmética = suma / n"),
                   ("a", "un candidato cualquiera de 'centro' (para compararlo con x̄)"),
                   ("Σ(xᵢ−a)²", "error cuadrático total respecto a a")],
        derivacion=["\\bar x = \\frac{1}{n}\\sum_{i=1}^n x_i",
                    "\\text{minimizar } S(a)=\\sum (x_i-a)^2 \\Rightarrow S'(a) = -2\\sum (x_i-a) = 0",
                    "\\Rightarrow \\sum x_i - n a = 0 \\Rightarrow a = \\frac{1}{n}\\sum x_i = \\bar x",
                    "\\text{y en el óptimo } \\sum (x_i-\\bar x) = 0 \\;(\\text{desviaciones se cancelan})"],
        contexto=("La media aritmética es el estadístico más antiguo y más usado, y "
                  "su historia está ligada a un problema práctico: los astrónomos de "
                  "los siglos XVIII-XIX tomaban varias mediciones de la posición de "
                  "un astro —todas ligeramente distintas por el error de "
                  "observación— y necesitaban UN número que fuera la 'mejor "
                  "estimación' del valor verdadero. Promediarlas resultó ser esa "
                  "mejor estimación, y entender POR QUÉ llevó a uno de los "
                  "resultados más fértiles de la matemática aplicada. La media tiene "
                  "dos propiedades que la definen mucho mejor que 'sumar y dividir'. "
                  "La primera: es el CENTRO DE MASA de los datos. Si uno imagina "
                  "cada dato como un peso sobre una regla, la media es el punto donde "
                  "la regla se equilibra —las desviaciones hacia la izquierda "
                  "cancelan exactamente las de la derecha, Σ(xᵢ−x̄)=0—. La segunda, "
                  "más profunda: la media es el valor que MINIMIZA la suma de los "
                  "errores al CUADRADO. De todos los números que uno podría proponer "
                  "como 'centro', x̄ es el que deja el menor Σ(xᵢ−a)². Esto no es una "
                  "curiosidad: es la semilla de los MÍNIMOS CUADRADOS de Gauss y "
                  "Legendre, y por lo tanto de toda la regresión (sec. XI). De "
                  "hecho, la media es literalmente 'la regresión sin variables "
                  "explicativas': el mejor pronóstico constante de una variable, en "
                  "el sentido de mínimo error cuadrático, es su media. Pero esa "
                  "misma virtud —usar el cuadrado del error— es su talón de Aquiles: "
                  "un solo dato extremo, elevado al cuadrado, pesa muchísimo, y "
                  "arrastra la media lejos del grueso de los datos. La media no es "
                  "ROBUSTA (un outlier la mueve sin límite), y de esa fragilidad "
                  "nacen la mediana (e18) y las medidas robustas (e32)."),
        autores=("La media como estimación del 'valor verdadero': astronomía de "
                 "observación (s. XVIII); la propiedad de mínimos cuadrados: "
                 "Legendre (1805) y Gauss (1809) — menciones históricas. El centro "
                 "de masa y la minimización: cálculo y estadística descriptiva "
                 "(conocimiento general)."),
        supuestos=[
            "Datos numéricos (cuantitativos) en escala de intervalo o razón: promediar exige que las distancias tengan sentido (no se promedian categorías, e05).",
            "Todas las observaciones pesan igual (media SIMPLE); si pesaran distinto sería la media ponderada (e20).",
            "El interés es un resumen de tendencia central bajo pérdida CUADRÁTICA: minimizar el error al cuadrado es una elección (bajo error absoluto, el óptimo es la mediana, e18).",
        ],
        ecuaciones=[
            Ecuacion("\\bar x = \\tfrac{1}{n}\\sum_{i=1}^n x_i", "la media",
                     "la suma de los datos repartida entre n: el 'valor equitativo' que cada observación "
                     "tendría si el total se distribuyera por igual."),
            Ecuacion("\\sum_{i=1}^n (x_i - \\bar x) = 0", "centro de masa",
                     "las desviaciones respecto a la media suman cero exactamente: lo que sobra de un lado "
                     "falta del otro — la media es el punto de equilibrio de los datos."),
            Ecuacion("\\bar x = \\arg\\min_a \\sum (x_i - a)^2", "mínimos cuadrados",
                     "de todos los centros posibles, la media es el que minimiza el error cuadrático total: "
                     "la raíz de la regresión (sec. XI) — la media es la regresión sin predictores."),
        ],
        intuicion=("Dos imágenes fijan la media. La primera es un balancín: los "
                   "datos son niños sentados a distintas distancias del centro, y la "
                   "media es el punto donde el balancín queda horizontal —el peso a "
                   "un lado equilibra al del otro—. Por eso Σ(xᵢ−x̄)=0 no es un "
                   "accidente algebraico: es la condición de equilibrio. La segunda "
                   "imagen es la de un blanco: si uno tuviera que apostar UN número "
                   "y lo penalizaran por el CUADRADO de lo lejos que quede de cada "
                   "dato, la apuesta óptima es la media. Cambiar la regla del juego "
                   "cambia la respuesta: si lo penalizaran por la distancia ABSOLUTA "
                   "(no al cuadrado), la apuesta óptima sería la MEDIANA (e18) —por "
                   "eso mean y median resuelven problemas distintos, no son dos "
                   "recetas para lo mismo—. Y la lección de fondo, que se repetirá "
                   "en todo el laboratorio: elevar al cuadrado premia el consenso "
                   "pero castiga con brutalidad los valores extremos, así que la "
                   "media es exquisitamente sensible a los outliers. Es el mejor "
                   "resumen cuando los datos son razonablemente simétricos y sin "
                   "atípicos; cuando no, engaña —el ingreso 'promedio' de una sala "
                   "con diez personas normales y un multimillonario no describe a "
                   "nadie—."),
        equilibrio=("La media es la solución única de dos problemas: el equilibrio "
                    "(Σ(xᵢ−x̄)=0) y la minimización del error cuadrático "
                    "(x̄=argmin Σ(xᵢ−a)²). Ambos dan el mismo punto porque la "
                    "condición de primer orden del segundo ES el primero. Su punto "
                    "de ruptura es 0%: un solo outlier la mueve sin cota."),
        limitaciones=[
            "NO es robusta: un único valor extremo la arrastra sin límite (punto de ruptura 0%) — por el peso del cuadrado. Con outliers o asimetría fuerte, engaña (usar la mediana, e18).",
            "Exige datos cuantitativos con distancias significativas: no tiene sentido para variables ordinales o nominales (e04-e05).",
            "Resume, y al resumir OCULTA: dos conjuntos muy distintos pueden tener la misma media; hay que acompañarla de una medida de dispersión (varianza, e27) y mirar la forma.",
        ],
        evolucion=("Abre la estadística descriptiva. La mediana (e18) responde al "
                   "mismo problema bajo error absoluto y es robusta; la moda (e19) "
                   "para lo más frecuente; la media ponderada (e20) cuando los pesos "
                   "difieren. Su fragilidad ante atípicos motiva las medidas "
                   "robustas (e32-e33). Y su propiedad de mínimos cuadrados reaparece "
                   "como el corazón de la regresión (e131+, β̂ minimiza Σ de "
                   "residuos al cuadrado) — la media es el caso más simple de esa "
                   "idea."),
    ),
    escenarios=[
        Escenario("centro_alto", "probar un centro demasiado alto (a = 11)",
                  {"a": 11.0},
                  "con a=11 el error cuadrático sube respecto al mínimo: proponer un "
                  "centro por encima de la media deja más error total. La parábola "
                  "SSE(a) sube a ambos lados de x̄.",
                  cadena=["elegir a = 11 (> x̄)", "las desviaciones ya no se cancelan (Σ(xᵢ−a)<0)",
                          "el error cuadrático Σ(xᵢ−a)² aumenta", "solo a = x̄ lo minimiza"]),
        Escenario("centro_bajo", "probar un centro demasiado bajo (a = 5)",
                  {"a": 5.0},
                  "con a=5 (por debajo de x̄) el error cuadrático también sube: el "
                  "mínimo está exactamente en la media, no antes ni después.",
                  cadena=["elegir a = 5 (< x̄)", "las desviaciones no se cancelan (Σ(xᵢ−a)>0)",
                          "el error cuadrático aumenta", "confirma que x̄ es el único mínimo"]),
    ],
    verificaciones=[
        Verificacion("las desviaciones suman cero: Σ(xᵢ−x̄)=0", _v_desviaciones_cero),
        Verificacion("Σxᵢ = n·x̄ (reparto equitativo)", _v_suma),
        Verificacion("x̄ minimiza el error cuadrático (mínimos cuadrados)", _v_minimiza_sse),
        Verificacion("la media NO es robusta (un outlier la arrastra)", _v_sensible_atipico),
    ],
    notas="La media es el centro de masa (Σ(xᵢ−x̄)=0) y el minimizador del error cuadrático (x̄=argmin Σ(xᵢ−a)²) — la semilla de la regresión. Pero punto de ruptura 0%: un outlier la arrastra (→ mediana e18, robustas e32).",
)
