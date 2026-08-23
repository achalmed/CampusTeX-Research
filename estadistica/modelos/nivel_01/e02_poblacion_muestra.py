# e02_poblacion_muestra.py — población y muestra (sección I, tema 2).
#
# EL modelo fundacional del laboratorio de estadística: toda la inferencia
# descansa en una idea — que una MUESTRA bien extraída lleva información sobre la
# POBLACIÓN entera. El modelo genera una población artificial (bimodal, NO
# normal, con μ y σ conocidos), extrae miles de muestras aleatorias de tamaño n,
# y muestra que la media muestral x̄ (1) se centra en μ (insesgada) y (2) se
# acerca a μ al crecer n (precisión ∝ σ/√n). Es la semilla del muestreo (sec. VI),
# del TCL (sec. V, e67) y de toda la inferencia (sec. VII).
#
# Aleatoriedad reproducible (semilla fija, convención del lab): las
# verificaciones dan el mismo número cada corrida.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

# --- Población artificial conocida (bimodal → claramente no normal) ---
_RNG_POB = np.random.default_rng(7)
_POBLACION = np.concatenate([
    _RNG_POB.normal(50, 8, 60000),      # grupo mayoritario
    _RNG_POB.normal(76, 6, 40000),      # segundo grupo → dos modas
])
_MU = float(_POBLACION.mean())          # parámetro poblacional (fijo, "desconocido")
_SIGMA = float(_POBLACION.std())
_RANGO = (_MU - 3.6 * _SIGMA, _MU + 3.6 * _SIGMA)


def _muestrear(n, reps=4000, semilla=2024):
    """Distribución muestral de x̄: `reps` medias de muestras aleatorias de n."""
    rng = np.random.default_rng(semilla)
    idx = rng.integers(0, len(_POBLACION), size=(reps, int(n)))
    return _POBLACION[idx].mean(axis=1)


def _densidad(datos, bins=70):
    d, bordes = np.histogram(datos, bins=bins, range=_RANGO, density=True)
    return (bordes[:-1] + bordes[1:]) / 2, d


def _curvas(p):
    n = int(p["n"])
    medias = _muestrear(n)
    xp, yp = _densidad(_POBLACION)
    xm, ym = _densidad(medias)
    se_teo = _SIGMA / np.sqrt(n)
    return {"lineas": {"población (bimodal, N grande)": (xp, yp, config.VERDE),
                       f"medias muestrales x̄ (n = {n})": (xm, ym, config.AZUL2)},
            "puntos": [(_MU, 0.0, f"μ = {_MU:.1f}")],
            "anotacion": (f"E[x̄] = {float(medias.mean()):.2f} ≈ μ = {_MU:.2f} (insesgada)\n"
                          f"SD(x̄) = {float(medias.std()):.2f} ≈ σ/√n = {se_teo:.2f}\n"
                          "más n → más estrecha (más precisa); ya casi normal (→ TCL, e67)")}


def _resultados(p):
    n = int(p["n"])
    medias = _muestrear(n)
    return {"μ poblacional (parámetro)": _MU,
            "σ poblacional": _SIGMA,
            "E[x̄]: media de las medias muestrales": float(medias.mean()),
            "SD(x̄): error estándar empírico": float(medias.std()),
            "σ/√n: error estándar teórico": _SIGMA / np.sqrt(n),
            "error medio |x̄− μ|": float(np.abs(medias - _MU).mean())}


def _ecuaciones_calibradas(p):
    n = int(p["n"])
    return [f"\\mu = {_MU:.1f}\\ \\text{{(parámetro, fijo)}}\\quad \\bar x\\ \\text{{(estadístico, varía)}}",
            f"E[\\bar x] = \\mu\\ \\text{{(insesgada)}}\\qquad SE(\\bar x) = \\sigma/\\sqrt{{n}} = {_SIGMA/np.sqrt(n):.2f}"]


_P0 = {"n": 30}


def _v_insesgada():
    medias = _muestrear(30)
    err = abs(float(medias.mean()) - _MU)
    return err < 0.15 * _SIGMA, \
        (f"la media de las medias muestrales E[x̄]={float(medias.mean()):.2f} coincide con μ={_MU:.2f} "
         f"(error {err:.3f} ≪ σ): x̄ es un estimador INSESGADO de μ — no se equivoca en promedio")


def _v_error_estandar():
    n = 30
    medias = _muestrear(n)
    se_emp, se_teo = float(medias.std()), _SIGMA / np.sqrt(n)
    return abs(se_emp - se_teo) / se_teo < 0.08, \
        (f"la dispersión de x̄ (SD={se_emp:.3f}) coincide con σ/√n={se_teo:.3f}: el ERROR ESTÁNDAR "
         "mide cuánto varía la media muestral de muestra a muestra — la fórmula clave de la precisión")


def _v_mas_n_mas_preciso():
    se_n = float(_muestrear(30).std())
    se_4n = float(_muestrear(120).std())    # 4× el tamaño → mitad del error
    razon = se_n / se_4n
    return 1.8 < razon < 2.2, \
        (f"cuadruplicar n (30→120) reduce el error estándar a la MITAD (razón {razon:.2f}≈2): la precisión "
         "crece con √n — para el doble de precisión hacen falta 4× datos (rendimientos decrecientes)")


def _v_representatividad():
    # con n grande, una sola muestra ya representa muy bien a la población
    una_muestra_media = float(_muestrear(500, reps=1, semilla=99)[0])
    return abs(una_muestra_media - _MU) < 0.15 * _SIGMA, \
        (f"con n=500 una SOLA muestra da x̄={una_muestra_media:.2f}, casi igual a μ={_MU:.2f}: una muestra "
         "grande y aleatoria REPRESENTA a la población — probar la sopa con una cucharada (bien revuelta)")


MODELO = Modelo(
    id="e02", nivel=1,
    nombre="Población y muestra",
    xlabel="valor", ylabel="densidad",
    parametros=[
        Parametro("n", _P0["n"], 5, 500, 5, "Tamaño de muestra n",
                  grupo="muestreo", definicion="cuántas observaciones se extraen; la precisión crece con √n"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Una muestra pequeña puede representar a toda una población — y cuánto nos equivocamos al usar la parte por el todo?",
        variables=[("N, μ, σ", "población: su tamaño y sus PARÁMETROS (fijos, desconocidos)"),
                   ("n", "tamaño de la muestra"),
                   ("x̄, s", "ESTADÍSTICOS de la muestra (aleatorios: cambian con cada muestra)"),
                   ("SE = σ/√n", "error estándar: cuánto varía x̄ de muestra a muestra")],
        derivacion=["\\text{población } \\{x_1,\\dots,x_N\\} \\text{ con media } \\mu, \\text{ desv. } \\sigma",
                    "\\text{muestra aleatoria de } n \\;\\Rightarrow\\; \\bar x = \\tfrac{1}{n}\\sum_{i=1}^{n} x_i",
                    "E[\\bar x] = \\mu \\quad (\\text{insesgada})",
                    "\\mathrm{Var}(\\bar x) = \\dfrac{\\sigma^2}{n} \\;\\Rightarrow\\; \\mathrm{SE}(\\bar x) = \\dfrac{\\sigma}{\\sqrt n}"],
        contexto=("Toda la estadística inferencial nace de una idea audaz: que no "
                  "hace falta medir a TODOS para saber algo confiable sobre el "
                  "conjunto — que una MUESTRA bien extraída lleva información sobre "
                  "la POBLACIÓN entera. Durante siglos, conocer una población "
                  "significó censarla (contar a cada uno), una tarea cara y lenta. "
                  "El giro llegó cuando se entendió que una parte, si se elige SIN "
                  "SESGO (al azar), es un espejo fiel del todo. Laplace ya estimó la "
                  "población de Francia en 1786 a partir de una muestra de "
                  "parroquias; un siglo después, Anders Kiaer formalizó el "
                  "'muestreo representativo' y desató la revolución del muestreo que "
                  "hizo posibles las encuestas modernas. Este modelo lo muestra con "
                  "una población artificial que conocemos por completo: es BIMODAL "
                  "(dos grupos, claramente NO normal), con media μ y desviación σ "
                  "conocidas. De ella extraemos miles de muestras aleatorias de "
                  "tamaño n y observamos la media muestral x̄. Aparecen dos hechos "
                  "que fundan todo lo que sigue. Primero, x̄ se CENTRA en μ: en "
                  "promedio, la muestra no se equivoca (es INSESGADA). Segundo, x̄ "
                  "no es exacta —cada muestra da un valor algo distinto—, pero su "
                  "variabilidad es medible y CONOCIDA: el error estándar σ/√n, que "
                  "encoge al crecer n. Con n pequeño, x̄ baila mucho alrededor de μ; "
                  "con n grande, se pega a μ. La distinción central que hay que "
                  "grabar: μ es un PARÁMETRO (fijo, propio de la población, que casi "
                  "nunca conocemos) y x̄ es un ESTADÍSTICO (que calculamos de la "
                  "muestra y que ESTIMA a μ). Confundirlos es el error conceptual "
                  "más común de la estadística. Y un adelanto hermoso: aunque la "
                  "población sea bimodal, la distribución de x̄ ya se ve acampanada "
                  "—el Teorema Central del Límite (e67) asomando—."),
        autores=("Pierre-Simon Laplace (estimación por muestreo, 1786); Anders "
                 "Kiaer (muestreo representativo, 1895); Jerzy Neyman (teoría del "
                 "muestreo, 1934) — menciones históricas, no citas de página. La "
                 "distinción parámetro/estadístico y el error estándar: teoría del "
                 "muestreo (conocimiento estadístico general)."),
        supuestos=[
            "Muestreo ALEATORIO simple: cada unidad de la población tiene la misma probabilidad de ser elegida (sin sesgo de selección).",
            "La población es fija y conocida SOLO en este laboratorio (para poder comparar x̄ con μ); en la práctica μ y σ son desconocidos — por eso se estiman.",
            "Las observaciones se extraen de forma independiente; el tamaño de la población es mucho mayor que n (muestreo con reemplazo ≈ sin reemplazo).",
        ],
        ecuaciones=[
            Ecuacion("\\bar x = \\tfrac{1}{n}\\sum_{i=1}^n x_i", "media muestral (estadístico)",
                     "el promedio de la muestra; VARÍA de una muestra a otra — es una variable aleatoria, "
                     "a diferencia de μ, que es un número fijo de la población."),
            Ecuacion("E[\\bar x] = \\mu", "insesgadez",
                     "en promedio, sobre todas las muestras posibles, la media muestral acierta el "
                     "parámetro: x̄ no se equivoca sistemáticamente hacia arriba ni hacia abajo."),
            Ecuacion("SE(\\bar x) = \\sigma/\\sqrt{n}", "error estándar",
                     "cuánto se dispersa x̄ alrededor de μ; encoge con √n — la ley cuantitativa de que "
                     "más datos dan más precisión (pero con rendimientos decrecientes)."),
        ],
        intuicion=("La imagen es la de probar una olla de sopa: si está BIEN "
                   "REVUELTA, una sola cucharada basta para saber si le falta sal —no "
                   "hace falta tomarse toda la olla—. 'Bien revuelta' es la clave, y "
                   "significa ALEATORIA: si la cuchara siempre toma del mismo rincón "
                   "(muestreo sesgado), la cucharada engaña por más grande que sea. "
                   "El laboratorio hace visible lo que la intuición sospecha: una "
                   "muestra aleatoria es un espejo del todo, imperfecto pero honesto. "
                   "El error estándar σ/√n pone número a esa imperfección, y su "
                   "forma —dividir por √n, no por n— tiene una consecuencia práctica "
                   "enorme: para DUPLICAR la precisión no basta el doble de datos, "
                   "hacen falta CUATRO veces más. Por eso una encuesta nacional bien "
                   "hecha de 1.200 personas puede describir a un país de millones con "
                   "un margen de error de ±3%: no es magia, es σ/√n. Y por eso el "
                   "tamaño de la muestra importa muchísimo hasta cierto punto y "
                   "después poco: pasar de 100 a 400 encuestados vale la pena; de "
                   "10.000 a 40.000, casi nunca. Grabar la diferencia entre el "
                   "PARÁMETRO que buscamos (μ) y el ESTADÍSTICO que calculamos (x̄) "
                   "es el primer paso de todo pensamiento estadístico serio."),
        equilibrio=("No hay equilibrio: hay convergencia. La media muestral x̄ es "
                    "insesgada (E[x̄]=μ) y su error estándar σ/√n → 0 cuando n → ∞; "
                    "es decir, x̄ converge a μ (ley de los grandes números, e64). La "
                    "distribución de x̄ además tiende a la normal (TCL, e67)."),
        limitaciones=[
            "Todo se apoya en la ALEATORIEDAD del muestreo: un muestreo sesgado (no aleatorio) rompe la insesgadez —x̄ deja de estimar μ— sin importar cuán grande sea n (sesgo de selección, sec. VI).",
            "μ y σ son conocidos SOLO aquí (para poder comparar); en la práctica se estiman de la propia muestra, lo que añade incertidumbre (la 's' en vez de σ lleva a la t de Student, e62).",
            "El error estándar σ/√n mide variabilidad aleatoria, NO sesgo: reduce el error por azar, jamás el error por mala medición o por una muestra torcida.",
        ],
        evolucion=("Es la raíz del laboratorio. La sec. II (descriptiva, e17+) "
                   "calcula x̄, s y compañía; la sec. V (e64 LGN, e67 TCL) explica "
                   "POR QUÉ x̄ converge a μ y por qué se vuelve normal; la sec. VI "
                   "(muestreo) estudia cómo extraer bien la muestra; y la sec. VII "
                   "(inferencia) usa el error estándar para construir intervalos de "
                   "confianza y pruebas de hipótesis. Todo cuelga de aquí."),
    ),
    escenarios=[
        Escenario("muestra_pequena", "muestra pequeña (n = 10): x̄ baila mucho",
                  {"n": 10},
                  "con n=10 la distribución de x̄ es ancha: cada muestra puede caer "
                  "bastante lejos de μ. Poca información, mucha incertidumbre — el "
                  "error estándar σ/√n es grande.",
                  cadena=["n pequeño (10)", "error estándar σ/√n grande",
                          "x̄ varía mucho de muestra a muestra", "una sola muestra puede engañar"]),
        Escenario("muestra_grande", "muestra grande (n = 200): x̄ se pega a μ",
                  {"n": 200},
                  "con n=200 la distribución de x̄ es estrecha y acampanada, muy "
                  "concentrada en μ: la muestra representa fielmente a la población. "
                  "El error estándar cayó por el factor √n.",
                  cadena=["n grande (200)", "error estándar σ/√n pequeño",
                          "x̄ se concentra en μ (representativa)", "poca incertidumbre — y ya casi normal (TCL)"]),
    ],
    verificaciones=[
        Verificacion("x̄ es insesgada: E[x̄] = μ", _v_insesgada),
        Verificacion("error estándar SD(x̄) = σ/√n", _v_error_estandar),
        Verificacion("cuadruplicar n reduce el error a la mitad (√n)", _v_mas_n_mas_preciso),
        Verificacion("una muestra grande representa a la población", _v_representatividad),
    ],
    notas="El modelo fundacional: x̄ estima μ, es insesgada (E[x̄]=μ) y su precisión es σ/√n. Parámetro (μ, fijo) ≠ estadístico (x̄, aleatorio). Todo el resto del currículo cuelga de aquí.",
)
