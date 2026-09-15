"""simuladores/estadistica/modelos/nivel_02/e27_varianza.py — varianza y desviación estándar (sección II, temas 27-28).

Cuánto se DISPERSAN los datos alrededor de su media. La varianza es el promedio
de las desviaciones al CUADRADO (elevar al cuadrado porque las desviaciones sin
cuadrar suman cero, e17); la desviación estándar es su raíz, que devuelve las
unidades originales. El modelo muestra dos cosas: la fórmula computacional
Var = E[X²]−μ², y —la joya— la CORRECCIÓN DE BESSEL: la varianza muestral con
n subestima σ² (sesgada baja), y solo dividir entre n−1 la corrige. Se ve por
simulación (como e02): miles de muestras, y s²ₙ₋₁ se centra en σ² mientras s²ₙ
se queda corta.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

# Población conocida (para Bessel) y un dataset chico (para las identidades).
_POB = np.random.default_rng(3).normal(50.0, 12.0, 120000)
_SIGMA2 = float(_POB.var())                          # varianza poblacional (ddof=0)
_SIGMA = float(np.sqrt(_SIGMA2))
_D = np.array([3, 5, 6, 8, 9, 11, 14], float)        # dataset chico para identidades


def _muestrear_s2(n, reps=6000, semilla=2024):
    """Para reps muestras de tamaño n: (s²ₙ sesgada, s²ₙ₋₁ corregida)."""
    rng = np.random.default_rng(semilla)
    idx = rng.integers(0, len(_POB), size=(reps, int(n)))
    m = _POB[idx]
    s2_n = m.var(axis=1, ddof=0)                      # divide entre n
    s2_n1 = m.var(axis=1, ddof=1)                     # divide entre n-1 (Bessel)
    return s2_n, s2_n1


def _densidad(datos, rango, bins=60):
    d, b = np.histogram(datos, bins=bins, range=rango, density=True)
    return (b[:-1] + b[1:]) / 2, d


def _curvas(p):
    n = int(p["n"])
    s2_n, s2_n1 = _muestrear_s2(n)
    rango = (0, _SIGMA2 * 2.4)
    xn, yn = _densidad(s2_n, rango)
    x1, y1 = _densidad(s2_n1, rango)
    return {"lineas": {f"s²ₙ (entre n) — sesgada baja": (xn, yn, config.ROJO),
                       f"s²ₙ₋₁ (entre n−1) — corregida": (x1, y1, config.AZUL2)},
            "puntos": [(_SIGMA2, 0.0, f"σ² = {_SIGMA2:.0f}")],
            "anotacion": (f"σ² poblacional = {_SIGMA2:.0f}  (n = {n})\n"
                          f"E[s²ₙ] = {float(s2_n.mean()):.0f} < σ²  (subestima)\n"
                          f"E[s²ₙ₋₁] = {float(s2_n1.mean()):.0f} ≈ σ²  (Bessel corrige)")}


def _resultados(p):
    n = int(p["n"])
    s2_n, s2_n1 = _muestrear_s2(n)
    return {"σ² poblacional": _SIGMA2,
            "σ (desviación estándar)": _SIGMA,
            "E[s²ₙ] (dividiendo entre n)": float(s2_n.mean()),
            "E[s²ₙ₋₁] (Bessel, entre n−1)": float(s2_n1.mean()),
            "sesgo de s²ₙ: E[s²ₙ]/σ²": float(s2_n.mean()) / _SIGMA2,
            "factor teórico (n−1)/n": (n - 1) / n}


def _ecuaciones_calibradas(p):
    n = int(p["n"])
    return [f"\\sigma^2 = \\frac{{1}}{{N}}\\sum (x_i-\\mu)^2 \\qquad \\sigma = \\sqrt{{\\sigma^2}}\\ \\text{{(unidades originales)}}",
            f"s^2 = \\frac{{1}}{{n-1}}\\sum (x_i-\\bar x)^2\\ \\text{{(insesgada, Bessel: }}n-1\\text{{)}}"]


_P0 = {"n": 5}


def _v_definicion():
    var = float(np.mean((_D - _D.mean()) ** 2))
    desv = float(np.sqrt(var))
    return abs(var - _D.var()) < 1e-9 and abs(desv - _D.std()) < 1e-9, \
        (f"la varianza es el promedio de las desviaciones al cuadrado (={var:.2f}) y la desviación estándar su "
         f"raíz (={desv:.2f}): elevar al cuadrado evita que se cancelen (Σ(xᵢ−x̄)=0, e17); la raíz devuelve las unidades")


def _v_formula_computacional():
    # Var = E[X²] − (E[X])²  (identidad de König-Huygens)
    var_directa = float(_D.var())
    var_formula = float(np.mean(_D ** 2) - _D.mean() ** 2)
    return abs(var_directa - var_formula) < 1e-9, \
        (f"fórmula computacional: Var = E[X²]−μ² = {np.mean(_D**2):.2f}−{_D.mean()**2:.2f} = {var_formula:.2f}, "
         "igual que la definición — la 'media de los cuadrados menos el cuadrado de la media' (König-Huygens)")


def _v_bessel():
    n = 5
    s2_n, s2_n1 = _muestrear_s2(n)
    sesgo_n = float(s2_n.mean()) / _SIGMA2
    ok_n1 = abs(float(s2_n1.mean()) - _SIGMA2) / _SIGMA2 < 0.03
    ok_n = abs(sesgo_n - (n - 1) / n) < 0.03
    return ok_n1 and ok_n, \
        (f"CORRECCIÓN DE BESSEL: dividir entre n subestima (E[s²ₙ]/σ²={sesgo_n:.2f}≈(n−1)/n={(n-1)/n:.2f}); "
         f"dividir entre n−1 corrige (E[s²ₙ₋₁]={float(s2_n1.mean()):.0f}≈σ²={_SIGMA2:.0f}) — por eso la varianza muestral usa n−1")


def _v_escala():
    c = 3.0
    return abs(float((c * _D).var()) - c ** 2 * float(_D.var())) < 1e-6, \
        (f"escala: multiplicar los datos por c={c:.0f} multiplica la VARIANZA por c²={c**2:.0f} y la desviación "
         "por |c| — la dispersión hereda las unidades (por eso la desviación, no la varianza, es comparable con la media)")


MODELO = Modelo(
    id="e27", nivel=2,
    nombre="Varianza y desviación estándar",
    xlabel="valor de la varianza muestral  s²", ylabel="densidad",
    parametros=[
        Parametro("n", _P0["n"], 2, 40, 1, "Tamaño de muestra n",
                  grupo="descriptiva", definicion="con n chico el sesgo de dividir entre n es grande; con n grande, desaparece"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo se mide cuánto se dispersan los datos — y por qué la varianza muestral se divide entre n−1 y no entre n?",
        variables=[("σ², σ", "varianza y desviación estándar POBLACIONALES (parámetros)"),
                   ("s²", "varianza muestral (con n−1: insesgada)"),
                   ("xᵢ−x̄", "desviaciones respecto a la media"),
                   ("(n−1)/n", "factor por el que s²ₙ subestima σ²")],
        derivacion=["\\sigma^2 = \\tfrac{1}{N}\\sum (x_i-\\mu)^2 \\quad(\\text{promedio de desviaciones}^2)",
                    "\\sigma = \\sqrt{\\sigma^2} \\quad(\\text{devuelve las unidades originales})",
                    "\\text{fórmula: } \\sigma^2 = E[X^2] - \\mu^2",
                    "\\text{muestral insesgada: } E\\!\\left[\\tfrac{1}{n-1}\\sum (x_i-\\bar x)^2\\right] = \\sigma^2 \\;(\\text{Bessel})"],
        contexto=("La media dice dónde está el centro; la varianza dice cuán "
                  "APIÑADOS o DISPERSOS están los datos a su alrededor —y dos "
                  "conjuntos con la misma media pueden ser completamente distintos si "
                  "uno está concentrado y el otro esparcido—. La idea natural sería "
                  "promediar las desviaciones respecto a la media, pero eso da "
                  "siempre cero (las desviaciones se cancelan, e17). La solución es "
                  "elevarlas al CUADRADO antes de promediar: así todas son "
                  "positivas y, de paso, las desviaciones grandes pesan mucho más "
                  "—la varianza castiga los datos lejanos—. El resultado, la "
                  "varianza, queda en unidades al cuadrado (soles², cm²), poco "
                  "intuitivas; por eso se toma su raíz, la DESVIACIÓN ESTÁNDAR, que "
                  "vuelve a las unidades originales y es directamente comparable con "
                  "la media. Hay una fórmula equivalente muy útil, Var = E[X²]−μ² "
                  "(la media de los cuadrados menos el cuadrado de la media), que "
                  "aparecerá una y otra vez. Y hay una sutileza famosa que confunde "
                  "a todo estudiante: al estimar la varianza de una POBLACIÓN a "
                  "partir de una MUESTRA, dividir entre n subestima "
                  "sistemáticamente el verdadero σ². La razón intuitiva: usamos la "
                  "media MUESTRAL x̄ (no la poblacional μ) como referencia, y x̄ "
                  "está —por construcción— más cerca de sus propios datos que μ, así "
                  "que las desviaciones respecto a x̄ salen artificialmente "
                  "pequeñas. La corrección de Bessel divide entre n−1 en vez de n, y "
                  "el laboratorio lo demuestra por simulación: sobre miles de "
                  "muestras, s²ₙ₋₁ se centra exactamente en σ² mientras que s²ₙ se "
                  "queda corta por el factor (n−1)/n. Con n grande la diferencia es "
                  "trivial; con n pequeño, importa mucho."),
        autores=("La varianza y la desviación estándar: Karl Pearson acuñó "
                 "'desviación estándar' (1893); la corrección n−1: Friedrich Bessel "
                 "/ teoría de estimación insesgada — menciones. Conocimiento "
                 "estadístico general."),
        supuestos=[
            "Datos cuantitativos: la dispersión al cuadrado exige distancias con sentido (no aplica a categorías).",
            "σ² poblacional se conoce SOLO aquí (para comparar); en la práctica se estima con s² —y por eso importa que sea insesgada (n−1)—.",
            "La media es la referencia (dispersión respecto al centro de e17); usar la media muestral en vez de la poblacional es justo lo que obliga a la corrección de Bessel.",
        ],
        ecuaciones=[
            Ecuacion("\\sigma^2 = \\tfrac{1}{N}\\sum (x_i-\\mu)^2", "varianza",
                     "promedio de las desviaciones al cuadrado; se elevan al cuadrado para que no se "
                     "cancelen (Σ(xᵢ−x̄)=0) y para castigar más lo lejano."),
            Ecuacion("\\sigma = \\sqrt{\\sigma^2}", "desviación estándar",
                     "la raíz de la varianza: devuelve las unidades originales, así que es comparable con "
                     "la media (la varianza queda en unidades²)."),
            Ecuacion("s^2 = \\tfrac{1}{n-1}\\sum (x_i-\\bar x)^2 \\;\\Rightarrow\\; E[s^2]=\\sigma^2", "corrección de Bessel",
                     "usar x̄ (no μ) subestima la dispersión; dividir entre n−1 en lugar de n corrige el "
                     "sesgo — la varianza muestral insesgada."),
        ],
        intuicion=("La desviación estándar es la 'regla' natural de los datos: dice, "
                   "en las mismas unidades que la media, cuánto se aparta "
                   "típicamente una observación del centro. En una normal, ~68% de "
                   "los datos caen a ±1 desviación de la media y ~95% a ±2 —la regla "
                   "empírica que hace de σ una unidad de medida universal—. Por eso "
                   "la desviación (no la varianza) es la que se reporta y la que "
                   "alimenta el coeficiente de variación (e29, dispersión relativa) "
                   "y los puntajes z. Sobre Bessel, la intuición que lo desmitifica: "
                   "cuando calculas s² usando x̄, estás midiendo la dispersión "
                   "respecto al punto que MINIMIZA esa dispersión (e17) —haces "
                   "trampa a tu favor sin querer—, así que el resultado sale "
                   "demasiado pequeño; dividir entre n−1 (un dato menos, el 'grado "
                   "de libertad' que gastaste al estimar la media) lo compensa "
                   "exactamente. No es una convención arbitraria: es la única "
                   "manera de que, en promedio sobre todas las muestras posibles, "
                   "aciertes σ². Y la moraleja para leer datos: la media sin la "
                   "desviación es media verdad —'el vuelo promedio se retrasa 10 "
                   "minutos' significa cosas muy distintas si la desviación es 2 "
                   "minutos o 40—."),
        equilibrio=("La varianza es única (promedio de desviaciones²) y no negativa; "
                    "cero solo si todos los datos son iguales. La versión muestral "
                    "con n−1 es insesgada (E[s²]=σ²); con n es sesgada baja por el "
                    "factor (n−1)/n, que → 1 cuando n → ∞. Escala: Var(cX)=c²Var(X)."),
        limitaciones=[
            "NO es robusta: como la media, se apoya en el cuadrado de las desviaciones, así que un outlier la dispara (su versión robusta es la MAD, e32).",
            "Unidades al cuadrado: la varianza no es directamente interpretable; hay que usar la desviación (√) para comparar con la media o entre variables.",
            "Bessel corrige el sesgo de s² (la varianza), pero s (la desviación, su raíz) sigue siendo levemente sesgada —la raíz es no lineal—; en la práctica se ignora salvo con n muy pequeño.",
        ],
        evolucion=("Da la segunda dimensión de todo dato —dispersión, tras el centro "
                   "de e17/e18—. Alimenta el coeficiente de variación (e29, "
                   "dispersión relativa), la asimetría y curtosis (e30-31, momentos "
                   "superiores), y es la base del error estándar σ/√n (e02) que "
                   "sostiene la inferencia. Su fragilidad ante atípicos motiva la "
                   "MAD y las medidas robustas (e32). Y el 'grado de libertad' de "
                   "Bessel reaparece en toda la teoría de estimación (t de Student "
                   "e62, regresión e135)."),
    ),
    escenarios=[
        Escenario("n_pequeno", "muestra pequeña (n = 3): Bessel importa mucho",
                  {"n": 3},
                  "con n=3, dividir entre n subestima σ² en un tercio (factor "
                  "2/3): s²ₙ se queda muy corta y solo n−1 la corrige. Con muestras "
                  "chicas, usar n en vez de n−1 es un error grave.",
                  cadena=["n = 3 (muestra chica)", "factor de sesgo (n−1)/n = 2/3 (grande)",
                          "s²ₙ subestima σ² en un tercio", "n−1 corrige: E[s²ₙ₋₁] = σ²"]),
        Escenario("n_grande", "muestra grande (n = 40): Bessel casi no importa",
                  {"n": 40},
                  "con n=40 el factor (n−1)/n = 0.975: el sesgo de dividir entre n "
                  "es trivial. La corrección de Bessel importa con muestras "
                  "pequeñas; con muchas, n y n−1 dan casi lo mismo.",
                  cadena=["n = 40 (muestra grande)", "factor (n−1)/n = 0.975 ≈ 1",
                          "s²ₙ y s²ₙ₋₁ casi iguales", "el sesgo se desvanece con n"]),
    ],
    verificaciones=[
        Verificacion("varianza = media de desviaciones²; desv = √varianza", _v_definicion),
        Verificacion("fórmula computacional: Var = E[X²] − μ²", _v_formula_computacional),
        Verificacion("corrección de Bessel: n−1 da E[s²]=σ² (n subestima)", _v_bessel),
        Verificacion("escala: Var(cX) = c²·Var(X)", _v_escala),
    ],
    notas="Varianza = promedio de desviaciones² (se cuadra para no cancelar y castigar lo lejano); desviación = √varianza (unidades originales). Bessel: la muestral usa n−1 para ser insesgada (usar x̄ subestima). No robusta (→ MAD, e32).",
)
