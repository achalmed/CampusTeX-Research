"""simuladores/estadistica/modelos/nivel_02/e21_media_geometrica.py — la media geométrica (sección II, tema 21).

El promedio correcto para tasas de crecimiento, factores y razones. La media
aritmética (e17) suma; la geométrica MULTIPLICA: GM = (∏xᵢ)^{1/n} = exp(media
de los logaritmos). Su caso estrella es el crecimiento compuesto: +50% seguido
de −50% NO deja igual (la media aritmética diría 0% de cambio), deja una
PÉRDIDA del 13.4% —y la media geométrica lo acierta—. El modelo muestra la
"drag" de la volatilidad: subir y bajar lo mismo cada período deja siempre por
debajo (GM ≤ AM, la desigualdad de las medias), y el hueco crece con la
volatilidad.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _factores(r):
    return np.array([1.0 + r, 1.0 - r])              # +r y −r cada período


def _gm(x):
    return float(np.exp(np.mean(np.log(x))))         # exp(media de logs) = (∏x)^{1/n}


def _curvas(p):
    r = p["r"]
    grid = np.linspace(0.0, 0.9, 180)
    gm = np.array([_gm(_factores(rr)) for rr in grid])
    return {"lineas": {"media aritmética de los factores (= 1)": (grid, np.ones(len(grid)), config.GRIS),
                       "media geométrica (crecimiento real)": (grid, gm, config.AZUL2)},
            "puntos": [(r, _gm(_factores(r)), f"volatilidad ±{r*100:.0f}% → GM {_gm(_factores(r)):.3f}")],
            "anotacion": (f"factores [1+{r:.2f}, 1−{r:.2f}]: media aritmética = 1 (¿sin cambio?)\n"
                          f"media geométrica = √((1+r)(1−r)) = {_gm(_factores(r)):.3f} < 1 (hay pérdida)\n"
                          "GM ≤ AM (desigualdad de medias); el hueco es la 'drag' de la volatilidad")}


def _resultados(p):
    r = p["r"]
    x = _factores(r)
    gm = _gm(x)
    return {"volatilidad ±r": r,
            "media aritmética de factores": float(x.mean()),
            "media geométrica de factores": gm,
            "crecimiento compuesto real por período (%)": (gm - 1) * 100,
            "hueco AM − GM (volatility drag)": float(x.mean()) - gm,
            "resultado tras 2 períodos (∏ factores)": float(np.prod(x))}


def _ecuaciones_calibradas(p):
    r = p["r"]
    x = _factores(r)
    return [f"\\mathrm{{GM}} = \\left(\\prod x_i\\right)^{{1/n}} = \\exp\\!\\big(\\overline{{\\ln x}}\\big) = {_gm(x):.3f}",
            f"\\mathrm{{GM}} \\leq \\mathrm{{AM}}:\\ {_gm(x):.3f} \\leq {float(x.mean()):.2f}\\ \\text{{(igualdad solo si no hay volatilidad)}}"]


_P0 = {"r": 0.5}


def _v_formula_log():
    x = _factores(0.5)
    gm_prod = float(np.prod(x) ** (1 / len(x)))
    gm_log = _gm(x)
    return abs(gm_prod - gm_log) < 1e-12, \
        (f"la media geométrica = (∏xᵢ)^(1/n) = exp(media de los logs) = {gm_log:.3f}: multiplicar y sacar raíz "
         "n-ésima equivale a promediar en escala logarítmica — por eso es el promedio natural de razones y tasas")


def _v_am_mayor_gm():
    valores = [(float(_factores(r).mean()), _gm(_factores(r))) for r in (0.0, 0.3, 0.6, 0.9)]
    ok = all(am >= gm - 1e-12 for am, gm in valores) and valores[0][0] == valores[0][1]
    return ok, \
        (f"AM ≥ GM SIEMPRE (desigualdad de las medias), con igualdad solo si todos los valores son iguales "
         f"(r=0): {valores[-1][0]:.2f} ≥ {valores[-1][1]:.3f} — la volatilidad SIEMPRE cuesta (drag)")


def _v_compuesto():
    r = 0.5
    x = _factores(r)
    return abs(_gm(x) ** len(x) - float(np.prod(x))) < 1e-12, \
        (f"la GM da el crecimiento COMPUESTO correcto: GM^n = ∏factores = {float(np.prod(x)):.3f}. Crecer al "
         "ritmo constante GM cada período llega al mismo lugar que la secuencia real — lo que la AM no cumple")


def _v_ejemplo_50():
    x = _factores(0.5)                                # +50% y −50%
    am, gm = float(x.mean()), _gm(x)
    return abs(am - 1.0) < 1e-9 and gm < 0.9, \
        (f"+50% y luego −50%: la media aritmética de los factores es {am:.2f} (¡parece 'sin cambio'!), pero la "
         f"geométrica es {gm:.3f} — una PÉRDIDA del {(1-gm)*100:.1f}%. Subir y bajar lo mismo deja abajo, y la GM lo sabe")


MODELO = Modelo(
    id="e21", nivel=2,
    nombre="La media geométrica",
    xlabel="volatilidad por período  (±r)", ylabel="factor de crecimiento",
    parametros=[
        Parametro("r", _P0["r"], 0.0, 0.9, 0.05, "Volatilidad por período (±r)",
                  grupo="descriptiva", definicion="subir y bajar ±r cada período; a más volatilidad, mayor la brecha AM−GM"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si algo sube 50% y luego baja 50%, ¿volviste al inicio? (No.) ¿Cuál es el promedio correcto de tasas de crecimiento?",
        variables=[("xᵢ", "factores de crecimiento (1+tasa), razones, índices"),
                   ("GM", "media geométrica = (∏xᵢ)^{1/n} = exp(media de logs)"),
                   ("AM − GM", "la 'drag': cuánto cuesta la volatilidad")],
        derivacion=["\\text{crecer } n \\text{ períodos multiplica: } \\text{total} = \\prod x_i",
                    "\\text{tasa constante equivalente } g: \\; g^n = \\prod x_i",
                    "\\Rightarrow g = \\left(\\prod x_i\\right)^{1/n} = \\mathrm{GM}",
                    "= \\exp\\!\\left(\\tfrac{1}{n}\\sum \\ln x_i\\right)\\;(\\text{media aritmética de los logs})"],
        contexto=("La media geométrica es el promedio que la aritmética no puede "
                  "dar: el de las cosas que se MULTIPLICAN en vez de sumarse —tasas "
                  "de crecimiento, factores, razones, rendimientos compuestos—. El "
                  "ejemplo que lo hace evidente es brutal: si una inversión sube "
                  "50% un año y baja 50% al siguiente, la media aritmética de "
                  "'+50% y −50%' da 0%, sugiriendo que quedaste igual. Pero no: 100 "
                  "sube a 150, y 150 baja a 75 —perdiste el 25%—. La media "
                  "aritmética miente porque el crecimiento se COMPONE (multiplica), "
                  "no se acumula (suma). La media geométrica, GM = (∏xᵢ)^{1/n}, "
                  "captura esto: es la tasa constante que, aplicada cada período, "
                  "llega al mismo lugar que la secuencia real. Equivale a promediar "
                  "en escala logarítmica (GM = exp de la media de los logaritmos), "
                  "porque el logaritmo convierte multiplicación en suma —por eso los "
                  "rendimientos financieros se analizan en 'log-returns'—. De aquí "
                  "sale un resultado profundo, la DESIGUALDAD DE LAS MEDIAS: la "
                  "geométrica nunca supera a la aritmética (GM ≤ AM), con igualdad "
                  "solo si todos los valores son idénticos. La diferencia AM − GM es "
                  "el costo de la VOLATILIDAD: cuanto más oscilan los factores, más "
                  "se aleja el crecimiento real (GM) del promedio ingenuo (AM). Es "
                  "la 'volatility drag' que hace que dos inversiones con la misma "
                  "rentabilidad promedio pero distinta volatilidad terminen en "
                  "lugares muy distintos —la más volátil, peor—. Por eso en finanzas "
                  "el rendimiento que importa es el geométrico (CAGR), no el "
                  "aritmético, y por eso la estabilidad tiene valor propio."),
        autores=("La media geométrica y la desigualdad AM-GM: matemática clásica "
                 "(Cauchy formalizó la desigualdad, 1821); su uso en crecimiento "
                 "compuesto y finanzas (CAGR) — menciones. Conocimiento general."),
        supuestos=[
            "Datos POSITIVOS (xᵢ > 0): la media geométrica exige valores positivos (hay logaritmos y raíces); no aplica a datos con ceros o negativos.",
            "Apropiada para cantidades MULTIPLICATIVAS (tasas, factores, razones): para cantidades aditivas, la media correcta es la aritmética.",
            "Los factores son de la forma (1 + tasa): un crecimiento de +r es el factor 1+r, una caída de −r es 1−r.",
        ],
        ecuaciones=[
            Ecuacion("\\mathrm{GM} = \\left(\\prod_{i=1}^n x_i\\right)^{1/n}", "media geométrica",
                     "la raíz n-ésima del producto: la tasa constante que reproduce el crecimiento total — el "
                     "promedio correcto de factores multiplicativos."),
            Ecuacion("\\mathrm{GM} = \\exp\\!\\left(\\tfrac{1}{n}\\sum \\ln x_i\\right)", "= media de los logs",
                     "promediar en escala logarítmica: el log convierte multiplicar en sumar, así que la GM "
                     "es la AM de los logaritmos — por eso los retornos se analizan en log."),
            Ecuacion("\\mathrm{GM} \\le \\mathrm{AM}", "desigualdad de las medias",
                     "la geométrica nunca supera a la aritmética, con igualdad solo si todos los valores son "
                     "iguales; la brecha es el costo de la volatilidad (drag)."),
        ],
        intuicion=("La imagen es la del interés compuesto al revés: así como ganar "
                   "poco cada año se convierte en mucho al componerse, oscilar "
                   "mucho cada año se convierte en pérdida al componerse. La media "
                   "geométrica es la que 've' la composición; la aritmética la "
                   "ignora y por eso engaña con tasas. La lección práctica más cara "
                   "de ignorar esto está en las finanzas: un fondo que gana 'en "
                   "promedio 10% anual' (aritmético) pero con años de +40% y −20% "
                   "rinde, compuesto, bastante menos que 10% —y menos que un fondo "
                   "estable al 8%—. La volatilidad no es solo riesgo psicológico: se "
                   "come el retorno real, matemáticamente. De ahí la sabiduría de "
                   "'lo importante no es cuánto ganas los buenos años, sino cuánto "
                   "no pierdes los malos', y de por qué la media geométrica (el "
                   "CAGR) es la única honesta para comparar inversiones. La misma "
                   "idea aparece cada vez que algo se multiplica período a período: "
                   "poblaciones, precios, contagios (el R₀ de una epidemia es "
                   "multiplicativo, m81 del macro-lab)."),
        equilibrio=("La media geométrica es única (para datos positivos) y siempre "
                    "≤ la aritmética, con igualdad solo si todos los valores "
                    "coinciden. GM^n reproduce el producto total (crecimiento "
                    "compuesto exacto). El hueco AM − GM crece monótonamente con la "
                    "dispersión de los factores — el costo de la volatilidad."),
        limitaciones=[
            "Solo para datos positivos: los ceros o negativos la indefinen (logaritmos) — no sirve para variables que pueden ser negativas.",
            "Menos intuitiva y menos usada por desconocimiento: mucha gente reporta el promedio aritmético de tasas (incorrecto) por costumbre.",
            "Como todas las medias, resume: no dice nada de la trayectoria ni del riesgo por sí sola (aunque la brecha AM−GM ya informa de la volatilidad).",
        ],
        evolucion=("Completa la familia de promedios con la media aritmética (e17, "
                   "para sumar) y la armónica (e22, para razones inversas), unidas "
                   "por la desigualdad HM ≤ GM ≤ AM. Su escala logarítmica anticipa "
                   "la transformación log (e142, para linealizar y estabilizar "
                   "varianza) y la distribución lognormal (e59). En economía es el "
                   "CAGR y el crecimiento compuesto (m26, m64 del macro-lab); en "
                   "epidemiología, el ritmo multiplicativo del contagio."),
    ),
    escenarios=[
        Escenario("estable", "sin volatilidad (r = 0): GM = AM",
                  {"r": 0.0},
                  "sin oscilación, todos los factores son iguales (1) y la "
                  "geométrica coincide con la aritmética: la desigualdad GM ≤ AM se "
                  "vuelve igualdad. La volatilidad cero no tiene costo.",
                  cadena=["volatilidad r = 0 (factores constantes)", "todos los factores iguales",
                          "GM = AM (igualdad en la desigualdad de medias)", "sin volatilidad, sin drag"]),
        Escenario("volatil", "mucha volatilidad (r = 0.8): gran drag",
                  {"r": 0.8},
                  "con oscilaciones de ±80%, la media aritmética sigue diciendo 1 "
                  "('sin cambio'), pero la geométrica cae a 0.6: subir y bajar 80% "
                  "cada período destruye el 40% del capital. La volatilidad extrema "
                  "es carísima.",
                  cadena=["volatilidad r = 0.8 (±80% por período)", "AM de factores = 1 (engaña)",
                          "GM = √(1−0.64) = 0.6 (pérdida del 40%)", "la volatilidad se come el retorno (drag)"]),
    ],
    verificaciones=[
        Verificacion("GM = (∏xᵢ)^(1/n) = exp(media de logs)", _v_formula_log),
        Verificacion("AM ≥ GM siempre (desigualdad de las medias)", _v_am_mayor_gm),
        Verificacion("GM^n reproduce el crecimiento compuesto", _v_compuesto),
        Verificacion("+50%/−50%: AM engaña (1), GM acierta (pérdida)", _v_ejemplo_50),
    ],
    notas="Media geométrica GM=(∏xᵢ)^(1/n)=exp(media de logs): el promedio de tasas/factores multiplicativos. +50%/−50% no vuelve al inicio (pierde 13.4%); la GM lo acierta, la AM no. GM≤AM (desigualdad de medias); la brecha es la 'drag' de la volatilidad. Solo datos positivos.",
)
