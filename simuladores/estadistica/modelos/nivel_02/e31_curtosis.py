"""simuladores/estadistica/modelos/nivel_02/e31_curtosis.py — la curtosis (sección II, tema 31).

La segunda medida de forma: cuán PESADAS son las colas de la distribución —es
decir, cuán frecuentes son los valores extremos—. Es el cuarto momento
estandarizado, γ₂ = E[(X−μ)⁴]/σ⁴; se resta 3 (la curtosis de la normal) para
obtener el EXCESO de curtosis. Exceso > 0 = colas PESADAS (leptocúrtica: más
eventos extremos que la normal, los 'cisnes negros' de las finanzas); exceso
< 0 = colas ligeras (platicúrtica). La lección cara: los retornos financieros
tienen colas pesadas, así que los modelos que suponen normalidad SUBESTIMAN el
riesgo de catástrofe. El modelo compara una t de Student (colas ajustables)
contra la normal y cuenta cuántos eventos a >3σ aparecen.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_N = 200000


def _datos(df):
    """t de Student con df grados de libertad: colas MUY pesadas si df chico,
    → normal si df grande. Se estandariza a varianza 1."""
    rng = np.random.default_rng(11)
    t = rng.standard_t(float(df), _N)
    return t / t.std()                               # varianza 1 para comparar formas


def _curtosis(x):
    z = (x - x.mean()) / x.std()
    return float(np.mean(z ** 4))                    # curtosis (normal = 3)


def _densidad_normal(x):
    return np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)


def _densidad(x, bins=200, rango=(-6, 6)):
    d, b = np.histogram(x, bins=bins, range=rango, density=True)
    return (b[:-1] + b[1:]) / 2, d


def _curvas(p):
    x = _datos(p["df"])
    cx, cy = _densidad(x)
    nx = np.linspace(-6, 6, 300)
    exceso = _curtosis(x) - 3
    p_extremo = float(np.mean(np.abs(x) > 3))
    return {"lineas": {"t de Student (colas pesadas)": (cx, cy, config.AZUL2),
                       "normal (referencia, curtosis 3)": (nx, _densidad_normal(nx), config.GRIS)},
            "puntos": [(3.0, _densidad_normal(3.0), "±3σ"), (-3.0, _densidad_normal(-3.0), "")],
            "anotacion": (f"curtosis = {_curtosis(x):.1f} (exceso {exceso:+.1f})\n"
                          f"eventos a más de 3σ: {p_extremo*100:.1f}%  (normal: 0.27%)\n"
                          "colas pesadas = más 'cisnes negros' que lo que la normal predice")}


def _resultados(p):
    x = _datos(p["df"])
    return {"grados de libertad (df)": float(p["df"]),
            "curtosis γ₂ = E[(X−μ)⁴]/σ⁴": _curtosis(x),
            "exceso de curtosis (γ₂ − 3)": _curtosis(x) - 3,
            "P(|z| > 3) en estos datos (%)": float(np.mean(np.abs(x) > 3) * 100),
            "P(|z| > 3) en una normal (%)": 0.27,
            "veces más eventos extremos que la normal": float(np.mean(np.abs(x) > 3) / 0.0027)}


def _ecuaciones_calibradas(p):
    x = _datos(p["df"])
    return [f"\\gamma_2 = \\frac{{E[(X-\\mu)^4]}}{{\\sigma^4}} = {_curtosis(x):.1f}\\ \\text{{(4º momento; normal}}=3)",
            f"\\text{{exceso}} = {_curtosis(x)-3:+.1f} > 0 \\Rightarrow \\text{{colas PESADAS (más eventos extremos)}}"]


_P0 = {"df": 4.0}


def _v_normal_curtosis_tres():
    x = _datos(200.0)                                  # df grande → normal
    return abs(_curtosis(x) - 3.0) < 0.4, \
        (f"con df grande (200) la t → normal y la curtosis → 3 ({_curtosis(x):.1f}): la NORMAL es la referencia "
         "(curtosis 3, exceso 0). Por eso se resta 3: el 'exceso' mide cuánto MÁS pesadas son las colas que en una normal")


def _v_colas_pesadas():
    x = _datos(3.0)                                    # df chico → colas muy pesadas
    return _curtosis(x) - 3 > 1.0, \
        (f"con df=3 las colas son PESADAS: exceso de curtosis = {_curtosis(x)-3:+.1f} > 0 (leptocúrtica). Los "
         "valores extremos son mucho más frecuentes que en una normal — el patrón de los retornos financieros")


def _v_mas_eventos_extremos():
    x = _datos(3.0)
    p_ext = float(np.mean(np.abs(x) > 3))
    return p_ext > 0.01, \
        (f"colas pesadas = más catástrofes: a más de 3σ hay {p_ext*100:.1f}% de los datos, contra 0.27% en una "
         f"normal ({p_ext/0.0027:.0f}× más). Un modelo que supone normalidad SUBESTIMA el riesgo de eventos extremos (cisnes negros)")


def _v_cuarto_momento():
    # la curtosis eleva a la CUARTA: castiga los extremos aún más que la varianza (cuadrado)
    x = _datos(4.0)
    z = (x - x.mean()) / x.std()
    return abs(_curtosis(x) - float(np.mean(z ** 4))) < 1e-6, \
        (f"la curtosis es el 4º momento estandarizado (={_curtosis(x):.1f}): elevar a la CUARTA amplifica los "
         "valores lejanos aún más que el cuadrado de la varianza (e27), por eso mide el peso de las colas")


MODELO = Modelo(
    id="e31", nivel=2,
    nombre="La curtosis (colas pesadas)",
    xlabel="valor (en desviaciones)", ylabel="densidad",
    parametros=[
        Parametro("df", _P0["df"], 2.5, 200.0, 0.5, "Grados de libertad de la t (colas)",
                  grupo="descriptiva", definicion="df chico → colas muy pesadas (curtosis alta); df grande → normal (curtosis 3)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Dos distribuciones con la misma media y desviación, ¿pueden diferir en algo peligroso? (Sí: en cuántos extremos producen.)",
        variables=[("γ₂", "curtosis = E[(X−μ)⁴]/σ⁴ (cuarto momento estandarizado)"),
                   ("exceso", "γ₂ − 3: cuánto más pesadas que la normal"),
                   ("colas", "pesadas (leptocúrtica) o ligeras (platicúrtica)")],
        derivacion=["\\gamma_2 = \\frac{E[(X-\\mu)^4]}{\\sigma^4} \\;(\\text{4º momento estandarizado})",
                    "\\text{normal: } \\gamma_2 = 3 \\Rightarrow \\text{exceso} = \\gamma_2 - 3",
                    "\\text{exceso} > 0 : \\text{colas PESADAS (más extremos)}",
                    "\\text{exceso} < 0 : \\text{colas ligeras}"],
        contexto=("La curtosis mide algo que ni el centro, ni la dispersión, ni la "
                  "asimetría capturan: cuán PESADAS son las colas de la "
                  "distribución, es decir, con qué frecuencia aparecen valores "
                  "extremos. Es el cuarto momento estandarizado, γ₂ = E[(X−μ)⁴]/σ⁴; "
                  "elevar las desviaciones a la CUARTA potencia amplifica los "
                  "valores lejanos todavía más que el cuadrado de la varianza, de "
                  "modo que la curtosis está dominada por lo que pasa en los "
                  "extremos. La distribución normal tiene curtosis exactamente 3, y "
                  "por eso se define el EXCESO de curtosis como γ₂ − 3: mide cuánto "
                  "más (o menos) pesadas son las colas comparadas con las de una "
                  "normal. Un exceso positivo (distribución LEPTOCÚRTICA) significa "
                  "colas pesadas: los eventos extremos son mucho más frecuentes de "
                  "lo que la normal predice. Un exceso negativo (platicúrtica) "
                  "significa colas ligeras, casi acotadas (la uniforme es el "
                  "ejemplo). Y aquí está la lección más cara de toda la estadística "
                  "aplicada: los retornos financieros tienen colas PESADAS. Los "
                  "crashes, las crisis, los días de −20% ocurren muchísimo más "
                  "seguido que lo que un modelo gaussiano supone —un movimiento que "
                  "la normal declara imposible una vez cada varios milenios ocurre "
                  "cada pocos años—. Los modelos de riesgo que asumieron normalidad "
                  "(y subestimaron las colas) están detrás de desastres como el "
                  "colapso de LTCM (1998) y la crisis de 2008: no vieron venir los "
                  "'cisnes negros' porque sus modelos los declaraban casi "
                  "imposibles. La curtosis es, entonces, la medida del riesgo de "
                  "catástrofe, y la razón por la que en finanzas y en gestión de "
                  "riesgo se usan distribuciones de colas pesadas (t de Student, "
                  "leyes de potencia) en lugar de la cómoda normal. Nota importante: "
                  "la curtosis mide colas, NO 'picudez' —un mito común es que mide "
                  "cuán puntiaguda es la distribución; en realidad, colas y pico "
                  "están relacionados, pero lo que la curtosis captura es el peso de "
                  "los extremos—."),
        autores=("Los momentos y la curtosis: Karl Pearson (quien acuñó "
                 "'curtosis', 1905); la crítica a la normalidad en finanzas y las "
                 "colas pesadas: Mandelbrot (1963), Taleb (cisnes negros) — "
                 "menciones. Conocimiento estadístico general."),
        supuestos=[
            "Datos cuantitativos; la curtosis usa el cuarto momento, dominado por los extremos, así que necesita MUCHOS datos para estimarse con fiabilidad.",
            "El exceso se define respecto a la normal (curtosis 3): 'colas pesadas' significa 'más pesadas que una gaussiana', no en abstracto.",
            "La curtosis mide el peso de las COLAS (frecuencia de extremos), no la 'picudez' del centro (un malentendido común); ambas cosas correlacionan pero no son lo mismo.",
        ],
        ecuaciones=[
            Ecuacion("\\gamma_2 = \\frac{E[(X-\\mu)^4]}{\\sigma^4}", "curtosis (4º momento estandarizado)",
                     "el promedio de las desviaciones a la CUARTA, estandarizado: la cuarta potencia amplifica "
                     "los extremos, así que γ₂ mide el peso de las colas."),
            Ecuacion("\\text{exceso} = \\gamma_2 - 3", "exceso sobre la normal",
                     "se resta la curtosis de la normal (3): el exceso mide cuánto más pesadas son las colas "
                     "que en una gaussiana — positivo = más eventos extremos."),
            Ecuacion("\\text{exceso} > 0 \\Rightarrow \\text{cisnes negros}", "colas pesadas = riesgo",
                     "colas pesadas significan que los extremos ocurren mucho más seguido que lo que la normal "
                     "predice: el riesgo de catástrofe que los modelos gaussianos subestiman."),
        ],
        intuicion=("La curtosis es la medida de 'lo que puede salir muy mal'. Dos "
                   "inversiones con el mismo retorno promedio y la misma volatilidad "
                   "(desviación) pueden ser radicalmente distintas si una tiene "
                   "colas pesadas: esa producirá, de vez en cuando, un desastre que "
                   "la otra nunca vería. La desviación estándar te dice cómo se "
                   "mueven las cosas en un día normal; la curtosis te advierte sobre "
                   "los días ANORMALES. La gran lección —aprendida a golpes por el "
                   "sistema financiero— es que el mundo real tiene colas mucho más "
                   "gordas que la cómoda campana de Gauss: los terremotos, las "
                   "crisis, las pandemias, los éxitos virales y los fraudes viven en "
                   "las colas, y un modelo que las supone finas está ciego "
                   "justamente ante lo que más importa. Por eso Nassim Taleb "
                   "popularizó los 'cisnes negros': eventos que los modelos declaran "
                   "casi imposibles pero que definen la historia. La estadística "
                   "madura respeta las colas: usa distribuciones de colas pesadas "
                   "cuando corresponde, no confía en la normalidad por comodidad, y "
                   "recuerda que la curtosis muestral es traicionera —depende de "
                   "unos pocos extremos, así que con pocos datos puede engañar en "
                   "cualquier dirección—. Ver la curtosis es, en el fondo, tener "
                   "humildad ante lo raro: aceptar que lo que no ha pasado todavía "
                   "puede pasar, y más seguido de lo que la campana promete."),
        equilibrio=("La curtosis γ₂ es 3 para la normal (exceso 0); mayor para colas "
                    "pesadas (leptocúrtica: t de Student, retornos financieros), "
                    "menor para colas ligeras (platicúrtica: uniforme). Domina por "
                    "los extremos (cuarta potencia). No es robusta y necesita muchos "
                    "datos. No hay 'equilibrio': es un descriptor del peso de las "
                    "colas."),
        limitaciones=[
            "Muy poco robusta y ávida de datos: al elevar a la cuarta, unos pocos outliers dominan la curtosis muestral, que con n pequeño es sumamente inestable.",
            "Mide colas, no 'picudez': interpretarla como cuán puntiaguda es la distribución es un error común; captura el peso de los extremos.",
            "Un solo número global: no distingue si las colas pesadas están a la izquierda, a la derecha o en ambas (para eso, mirar la distribución completa y la asimetría e30).",
        ],
        evolucion=("Completa las medidas de FORMA con la asimetría (e30): asimetría "
                   "(3er momento) para la dirección de la cola, curtosis (4º momento) "
                   "para su peso. Motiva las distribuciones de colas pesadas frente "
                   "a la normal (e58): la t de Student (e62), las leyes de potencia, "
                   "y toda la gestión de riesgo. Su lección —no confiar en la "
                   "normalidad— reaparece en las pruebas de normalidad (e120-e122) y "
                   "en el riesgo financiero (VaR, e24, y sus fallos). Con e30-e31, la "
                   "descriptiva describe la distribución completa: centro, "
                   "dispersión, forma y rarezas — lista para la probabilidad (sección III)."),
    ),
    escenarios=[
        Escenario("colas_pesadas", "colas muy pesadas (df = 3): riesgo de cisne negro",
                  {"df": 3.0},
                  "con df=3, la t tiene colas gordísimas: exceso de curtosis alto y "
                  "muchos más eventos a >3σ que una normal. Es el patrón de los "
                  "retornos financieros — los crashes ocurren mucho más seguido de "
                  "lo que la campana predice.",
                  cadena=["df = 3 (colas muy pesadas)", "exceso de curtosis alto (leptocúrtica)",
                          "muchos eventos extremos (>3σ)", "riesgo de catástrofe subestimado por la normal"]),
        Escenario("casi_normal", "colas normales (df = 100)",
                  {"df": 100.0},
                  "con df grande la t es casi una normal: curtosis ≈ 3, exceso ≈ 0, "
                  "y los eventos a >3σ vuelven a ser raros (0.27%). Cuando las colas "
                  "son normales, la campana de Gauss es un buen modelo — y solo "
                  "entonces.",
                  cadena=["df = 100 (colas normales)", "curtosis → 3 (exceso → 0)",
                          "eventos a >3σ vuelven a ser raros (0.27%)", "la normal es buen modelo — solo aquí"]),
    ],
    verificaciones=[
        Verificacion("la normal tiene curtosis 3 (exceso 0)", _v_normal_curtosis_tres),
        Verificacion("colas pesadas → exceso de curtosis > 0", _v_colas_pesadas),
        Verificacion("colas pesadas → muchos más eventos extremos", _v_mas_eventos_extremos),
        Verificacion("curtosis = cuarto momento estandarizado", _v_cuarto_momento),
    ],
    notas="Curtosis γ₂=E[(X−μ)⁴]/σ⁴ (4º momento): peso de las COLAS. Normal=3; exceso=γ₂−3. Exceso>0 = colas pesadas (leptocúrtica): más eventos extremos ('cisnes negros'). Los retornos financieros tienen colas pesadas → los modelos gaussianos subestiman el riesgo de catástrofe. Mide colas, no picudez.",
)
