# e29_coeficiente_variacion.py — el coeficiente de variación (sección II, tema 29).
#
# La dispersión RELATIVA. La desviación estándar (e27-e28) mide la dispersión en
# las unidades de los datos, así que NO permite comparar variables de escalas
# distintas: ¿qué varía más, el peso de los elefantes (σ enorme) o el de los
# ratones (σ minúsculo)? Comparar sus desviaciones no tiene sentido. El
# coeficiente de variación CV = σ/μ (a menudo ×100 como %) resuelve esto:
# expresa la desviación como FRACCIÓN de la media, sin unidades, y es INVARIANTE
# A LA ESCALA. El modelo escala los datos y muestra que σ crece pero el CV no se
# mueve — por eso el CV, no la desviación, compara dispersión entre variables.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_BASE = np.array([42, 48, 50, 51, 55, 47, 53, 49, 46, 52], float)   # datos base (μ≈49.3)


def _cv(x):
    return float(x.std() / x.mean())


def _curvas(p):
    c = p["escala"]
    grid = np.linspace(0.2, 5.0, 160)
    sigmas = np.array([(_BASE * g).std() for g in grid])
    cvs = np.array([_cv(_BASE * g) for g in grid])
    return {"lineas": {"desviación estándar σ: CRECE con la escala": (grid, sigmas, config.ROJO),
                       "coeficiente de variación CV=σ/μ: INVARIANTE": (grid, cvs * 100, config.AZUL2)},
            "puntos": [(c, _cv(_BASE * c) * 100, f"escala ×{c:.1f} → CV {_cv(_BASE*c)*100:.1f}%")],
            "anotacion": (f"escalar los datos ×{c:.1f}: σ = {(_BASE*c).std():.1f} (cambia)\n"
                          f"CV = σ/μ = {_cv(_BASE*c)*100:.1f}% (NO cambia)\n"
                          "el CV es adimensional: compara dispersión entre escalas")}


def _resultados(p):
    c = p["escala"]
    x = _BASE * c
    return {"escala c": float(c),
            "media μ": float(x.mean()),
            "desviación σ (cambia con la escala)": float(x.std()),
            "coeficiente de variación CV = σ/μ (%)": _cv(x) * 100,
            "CV de los datos base (%)": _cv(_BASE) * 100,
            "¿CV invariante? (base vs escalado)": 1.0 if abs(_cv(x) - _cv(_BASE)) < 1e-9 else 0.0}


def _ecuaciones_calibradas(p):
    c = p["escala"]
    x = _BASE * c
    return [f"\\mathrm{{CV}} = \\frac{{\\sigma}}{{\\mu}} = \\frac{{{x.std():.1f}}}{{{x.mean():.1f}}} = {_cv(x)*100:.1f}\\%\\ \\text{{(dispersión relativa)}}",
            f"\\mathrm{{CV}}(cX) = \\mathrm{{CV}}(X)\\ \\text{{(invariante a la escala: adimensional)}}"]


_P0 = {"escala": 1.0}


def _v_definicion():
    cv = _cv(_BASE)
    return abs(cv - _BASE.std() / _BASE.mean()) < 1e-12, \
        (f"el coeficiente de variación es σ/μ = {_BASE.std():.1f}/{_BASE.mean():.1f} = {cv*100:.1f}%: la "
         "desviación expresada como fracción de la media — la dispersión RELATIVA al tamaño de lo que se mide")


def _v_invariante_escala():
    valores = [_cv(_BASE * c) for c in (0.5, 1, 2, 10)]
    return max(valores) - min(valores) < 1e-9, \
        (f"el CV es INVARIANTE a la escala: multiplicar todos los datos por cualquier c no lo cambia "
         f"({valores[0]*100:.1f}% en los cuatro casos) — porque σ y μ escalan igual, y su cociente se cancela")


def _v_compara_escalas():
    # elefantes (μ grande, σ grande) vs ratones (μ chico, σ chico): mismo CV si son proporcionales
    elefantes = _BASE * 100                            # ~kg
    ratones = _BASE * 0.5                              # ~g
    return abs(_cv(elefantes) - _cv(ratones)) < 1e-9, \
        (f"el CV compara ACROSS escalas: elefantes (σ={elefantes.std():.0f}) y ratones (σ={ratones.std():.1f}) "
         f"tienen desviaciones incomparables, pero el MISMO CV ({_cv(elefantes)*100:.1f}%) — igual de variables en términos relativos")


def _v_indefinido_media_cero():
    # si la media se acerca a 0, el CV explota / pierde sentido
    x = _BASE - _BASE.mean()                            # media 0
    cv_grande = abs(np.std(x) / (np.mean(x) + 1e-6))
    return cv_grande > 100, \
        ("el CV pierde sentido si μ ≈ 0 (explota) o μ < 0: solo es interpretable para variables POSITIVAS con "
         "media lejos de cero (pesos, precios, tiempos) — no para temperaturas en °C ni para diferencias centradas")


MODELO = Modelo(
    id="e29", nivel=2,
    nombre="El coeficiente de variación",
    xlabel="escala de los datos  (×c)", ylabel="σ  y  CV(%)",
    parametros=[
        Parametro("escala", _P0["escala"], 0.2, 5.0, 0.1, "Escala de los datos (×c)",
                  grupo="descriptiva", definicion="multiplica todos los datos; σ cambia pero el CV (dispersión relativa) no"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Qué varía más: el peso de los elefantes o el de los ratones? (Comparar sus desviaciones no sirve — ¿entonces?)",
        variables=[("CV", "coeficiente de variación = σ/μ (dispersión relativa, sin unidades)"),
                   ("σ", "desviación estándar (absoluta, con unidades)"),
                   ("μ", "la media (la escala respecto a la que se relativiza)")],
        derivacion=["\\sigma \\text{ está en las unidades de los datos} \\Rightarrow \\text{no compara escalas}",
                    "\\mathrm{CV} = \\frac{\\sigma}{\\mu} : \\text{dispersión como fracción de la media}",
                    "\\text{adimensional} \\Rightarrow \\mathrm{CV}(cX) = \\mathrm{CV}(X) \\;(\\text{invariante})",
                    "\\text{compara variables de escalas y unidades distintas}"],
        contexto=("El coeficiente de variación resuelve un problema que la "
                  "desviación estándar no puede: comparar la dispersión de cosas "
                  "medidas en escalas distintas. La desviación del peso de los "
                  "elefantes será de cientos de kilos, y la del peso de los ratones "
                  "de unos pocos gramos —comparar esos dos números es absurdo, no "
                  "porque los elefantes 'varíen más', sino porque son más grandes en "
                  "todo—. Lo que tiene sentido es preguntar por la variabilidad "
                  "RELATIVA al tamaño típico: ¿se aparta el peso de un elefante de "
                  "su media, en proporción, más o menos que el de un ratón? Eso es "
                  "el CV = σ/μ, la desviación estándar expresada como fracción "
                  "(o porcentaje) de la media. Al dividir dos cantidades en las "
                  "mismas unidades, el CV queda ADIMENSIONAL —un número puro— y, por "
                  "lo tanto, INVARIANTE A LA ESCALA: si mides las mismas cosas en "
                  "gramos o en kilos, en soles o en dólares, la desviación cambia "
                  "pero el CV no. Esa invariancia es exactamente lo que lo hace "
                  "comparable entre variables. Se usa para todo lo que exige comparar "
                  "variabilidades: en finanzas, para comparar el riesgo relativo de "
                  "activos de distinto precio (el CV de los retornos, primo del "
                  "ratio de Sharpe); en control de calidad, para comparar la "
                  "precisión de procesos que producen piezas de tamaños distintos; "
                  "en biología, para comparar cuán variable es un rasgo entre "
                  "especies. Un CV bajo (digamos <10%) indica un proceso o rasgo "
                  "MUY consistente; uno alto, muy variable. Pero el CV tiene una "
                  "trampa importante: solo tiene sentido para variables POSITIVAS "
                  "con media lejos de cero. Si la media se acerca a cero, el CV "
                  "explota (dividir por casi nada); si la variable puede ser "
                  "negativa o su cero es arbitrario (temperaturas en Celsius, "
                  "diferencias, retornos que pueden ser negativos), el CV pierde "
                  "sentido —relativizar a una media que no es un 'tamaño' genuino no "
                  "significa nada—. Usado donde corresponde (pesos, precios, "
                  "tiempos, conteos), es la medida correcta de 'cuán disperso "
                  "relativo a su tamaño'."),
        autores=("El coeficiente de variación: Karl Pearson (1896), quien lo "
                 "introdujo como medida de dispersión relativa — mención histórica. "
                 "Conocimiento estadístico general."),
        supuestos=[
            "Variable POSITIVA con media claramente mayor que cero y con un cero ABSOLUTO significativo (razón/ratio scale, e05): pesos, precios, tiempos, conteos — no temperaturas en °C ni diferencias centradas.",
            "Se compara dispersión RELATIVA: dos variables con el mismo CV son 'igual de variables' en proporción a su tamaño, aunque sus desviaciones absolutas difieran.",
            "Hereda la no robustez de σ y μ (e32): outliers distorsionan tanto el numerador como el denominador.",
        ],
        ecuaciones=[
            Ecuacion("\\mathrm{CV} = \\frac{\\sigma}{\\mu}", "coeficiente de variación",
                     "la desviación como fracción de la media: dispersión relativa al tamaño típico, sin "
                     "unidades — a menudo expresada como porcentaje (×100)."),
            Ecuacion("\\mathrm{CV}(cX) = \\mathrm{CV}(X)", "invariante a la escala",
                     "escalar los datos multiplica σ y μ por igual, y su cociente se cancela: por eso el CV "
                     "es comparable entre variables de escalas y unidades distintas."),
            Ecuacion("\\mu \\to 0 \\Rightarrow \\mathrm{CV} \\to \\infty", "solo para media positiva",
                     "si la media se acerca a cero el CV explota, y si la variable puede ser negativa pierde "
                     "sentido: solo aplica a variables positivas con cero absoluto (pesos, precios)."),
        ],
        intuicion=("El coeficiente de variación es la respuesta a '¿mucho respecto a "
                   "qué?'. Una desviación de 10 es enorme si la media es 20 (CV=50%, "
                   "los datos están por todos lados) e insignificante si la media es "
                   "10.000 (CV=0.1%, un proceso de relojería). El CV pone la "
                   "dispersión en perspectiva de tamaño, que es como el mundo real "
                   "la juzga: un error de un centímetro es catastrófico al fabricar "
                   "un chip y trivial al construir una carretera. Por eso es la "
                   "medida correcta para preguntas de CONSISTENCIA relativa: qué "
                   "proceso es más preciso, qué activo es más arriesgado por unidad "
                   "de valor, qué rasgo es más estable entre especies. Su lección "
                   "más útil es también su advertencia: solo funciona cuando "
                   "'relativo a la media' significa algo, es decir, cuando la media "
                   "es un tamaño genuino y positivo. Aplicarlo a temperaturas en "
                   "Celsius (donde el cero es arbitrario) o a retornos que pueden ser "
                   "negativos da números sin sentido —el CV de una variable centrada "
                   "en cero explota o cambia con solo mover el origen—. Saber cuándo "
                   "una medida aplica y cuándo no es, en el fondo, la competencia "
                   "central de la estadística: no hay medida universal, hay medidas "
                   "correctas para preguntas concretas."),
        equilibrio=("El CV = σ/μ es adimensional e invariante a la escala "
                    "(CV(cX)=CV(X)), lo que lo hace comparable entre variables. "
                    "Explota si μ→0 y pierde sentido si la variable puede ser "
                    "negativa o su cero es arbitrario. Bajo = consistente; alto = "
                    "muy variable. Solo para variables positivas de razón."),
        limitaciones=[
            "Solo para variables positivas con cero absoluto: sin sentido para temperaturas en °C, retornos que pueden ser negativos, o diferencias centradas (donde μ puede ser 0 o el origen es arbitrario).",
            "Inestable si la media es pequeña: al dividir por μ, un μ cercano a cero dispara el CV, volviéndolo poco fiable.",
            "No robusto: usa σ y μ, que los outliers distorsionan; para dispersión relativa robusta se usaría MAD/mediana.",
        ],
        evolucion=("Lleva la dispersión (desviación, e27-e28) a su forma RELATIVA e "
                   "invariante a la escala, permitiendo comparar variabilidad entre "
                   "variables distintas —lo que la desviación absoluta no puede—. Es "
                   "primo del ratio de Sharpe (riesgo por unidad de retorno) y del "
                   "índice D9/D1 (e25, desigualdad relativa). Junto con la "
                   "estandarización (e28, que relativiza cada dato) completa la idea "
                   "de 'dispersión en contexto'. Sigue la FORMA de la distribución: "
                   "asimetría (e30) y curtosis (e31)."),
    ),
    escenarios=[
        Escenario("escala_original", "escala original (×1)",
                  {"escala": 1.0},
                  "en la escala base, σ y CV toman sus valores originales. El CV "
                  "resume la dispersión relativa a la media: la referencia contra la "
                  "que se comparará al reescalar.",
                  cadena=["datos en su escala original", "σ y μ en las unidades base",
                          "CV = σ/μ (dispersión relativa)", "la referencia adimensional"]),
        Escenario("reescalado", "cambiar de unidades (×3)",
                  {"escala": 3.0},
                  "al multiplicar los datos por 3 (p.ej. cambiar de unidades), la "
                  "desviación se triplica pero el CV NO cambia: la variabilidad "
                  "relativa es la misma, solo cambió la vara. Esa invariancia es "
                  "todo el punto del CV.",
                  cadena=["multiplicar los datos ×3 (cambio de unidades)", "σ se triplica (cambia con la escala)",
                          "μ también se triplica", "CV = σ/μ NO cambia (invariante)"]),
    ],
    verificaciones=[
        Verificacion("CV = σ/μ (dispersión relativa)", _v_definicion),
        Verificacion("el CV es invariante a la escala (CV(cX)=CV(X))", _v_invariante_escala),
        Verificacion("el CV compara variables de escalas distintas", _v_compara_escalas),
        Verificacion("el CV pierde sentido si μ ≈ 0 o μ < 0", _v_indefinido_media_cero),
    ],
    notas="CV=σ/μ: dispersión RELATIVA, adimensional, invariante a la escala (CV(cX)=CV(X)). Compara variabilidad entre variables de escalas distintas (elefantes vs ratones) que las desviaciones no pueden. Solo para variables positivas con media lejos de 0; explota si μ→0.",
)
