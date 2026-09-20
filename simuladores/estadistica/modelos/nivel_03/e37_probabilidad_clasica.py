"""simuladores/estadistica/modelos/nivel_03/e37_probabilidad_clasica.py — la probabilidad clásica (sección III, tema 37).

La primera definición de probabilidad (Laplace): cuando todos los resultados
del espacio muestral (e35) son IGUALMENTE probables, la probabilidad de un
evento es el cociente casos favorables / casos totales. Simple, pero exige dos
condiciones fuertes: Ω finito y equiprobabilidad. Su aplicación estrella —y una
de las más contraintuitivas de toda la estadística— es la PARADOJA DEL
CUMPLEAÑOS: basta con 23 personas para que la probabilidad de que dos compartan
cumpleaños supere el 50%. El modelo la calcula (contando, vía complemento) y la
contrasta con simulación, mostrando que la intuición humana es pésima para la
probabilidad de coincidencias.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _p_comparten(n):
    """P(al menos dos de n personas comparten cumpleaños) — clásica, vía complemento."""
    n = int(n)
    if n > 365:
        return 1.0
    p_distintos = 1.0
    for i in range(n):
        p_distintos *= (365 - i) / 365
    return 1.0 - p_distintos


def _p_simulada(n, reps=20000, semilla=2024):
    rng = np.random.default_rng(semilla)
    b = rng.integers(0, 365, size=(reps, int(n)))
    comparten = np.array([len(set(fila)) < int(n) for fila in b])
    return float(comparten.mean())


def _curvas(p):
    n = int(p["n"])
    ns = np.arange(1, 61)
    ps = np.array([_p_comparten(k) for k in ns])
    return {"lineas": {"P(dos comparten cumpleaños)": (ns, ps, config.AZUL2),
                       "umbral 50%": (np.array([1, 60]), np.array([0.5, 0.5]), config.GRIS)},
            "puntos": [(23, _p_comparten(23), f"n=23 → {_p_comparten(23)*100:.0f}% (¡>50%!)"),
                       (n, _p_comparten(n), f"n={n} → {_p_comparten(n)*100:.0f}%")],
            "anotacion": (f"P = casos favorables / casos totales (todos equiprobables)\n"
                          f"con {n} personas: P(coincidencia) = {_p_comparten(n)*100:.1f}%\n"
                          "basta con 23 para pasar el 50%: la intuición se equivoca con coincidencias")}


def _resultados(p):
    n = int(p["n"])
    return {"número de personas n": float(n),
            "P(al menos dos comparten) — clásica": _p_comparten(n),
            "P — simulada (frecuentista, e38)": _p_simulada(n),
            "P(23 personas) — la paradoja": _p_comparten(23),
            "P(57 personas) — casi seguro": _p_comparten(57),
            "P(todos distintos) = 1 − P(comparten)": 1 - _p_comparten(n)}


def _ecuaciones_calibradas(p):
    n = int(p["n"])
    return [f"P(A) = \\frac{{\\text{{casos favorables}}}}{{\\text{{casos totales}}}}\\ \\text{{(si equiprobables, Laplace)}}",
            f"P(\\text{{coincidencia}}, n{{=}}{n}) = 1 - \\prod_{{i=0}}^{{{n-1}}}\\frac{{365-i}}{{365}} = {_p_comparten(n):.2f}"]


_P0 = {"n": 23}


def _v_favorable_sobre_total():
    # P(sacar un corazón de una baraja) = 13/52 = 1/4 (casos favorables/totales)
    return abs(13 / 52 - 0.25) < 1e-12, \
        ("probabilidad clásica = casos favorables / casos totales: P(corazón) = 13/52 = 1/4, P(as) = 4/52 = 1/13. "
         "Cuando todos los resultados son equiprobables, basta CONTAR — la definición de Laplace")


def _v_paradoja_23():
    return _p_comparten(23) > 0.5, \
        (f"la PARADOJA DEL CUMPLEAÑOS: con solo 23 personas, P(dos comparten cumpleaños) = {_p_comparten(23)*100:.1f}% "
         "> 50% — contraintuitivo (hay 253 PARES posibles entre 23 personas, muchas más chances de coincidir de las que uno imagina)")


def _v_casi_seguro_57():
    return _p_comparten(57) > 0.99, \
        (f"con 57 personas la coincidencia es casi segura ({_p_comparten(57)*100:.1f}%): la probabilidad crece "
         "rapidísimo porque el número de PARES crece con n² — la intuición lineal falla ante lo cuadrático")


def _v_clasica_coincide_frecuentista():
    n = 23
    return abs(_p_comparten(n) - _p_simulada(n)) < 0.02, \
        (f"la probabilidad CLÁSICA (contando: {_p_comparten(n)*100:.1f}%) coincide con la FRECUENTISTA (simulando "
         f"20000 grupos: {_p_simulada(n)*100:.1f}%): contar los casos y repetir el experimento dan lo mismo (e38) — dos caras de la probabilidad")


MODELO = Modelo(
    id="e37", nivel=3,
    nombre="La probabilidad clásica (paradoja del cumpleaños)",
    xlabel="número de personas  n", ylabel="P(dos comparten cumpleaños)",
    parametros=[
        Parametro("n", _P0["n"], 2, 60, 1, "Número de personas",
                  grupo="probabilidad", definicion="P(coincidencia) cruza el 50% en n=23 y llega a ~99% en n=57"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuántas personas hacen falta para que sea más probable que no que dos compartan cumpleaños? (Sorpresa: 23.)",
        variables=[("casos favorables", "resultados en los que ocurre el evento"),
                   ("casos totales", "todos los resultados posibles (|Ω|, e35)"),
                   ("P(A)", "favorables / totales, si todos son equiprobables")],
        derivacion=["\\text{si todos los resultados son equiprobables:}",
                    "P(A) = \\frac{|A|}{|\\Omega|} = \\frac{\\text{casos favorables}}{\\text{casos totales}}",
                    "\\text{cumpleaños: } P(\\text{todos distintos}) = \\prod_{i=0}^{n-1}\\frac{365-i}{365}",
                    "P(\\text{coincidencia}) = 1 - P(\\text{todos distintos}) \\;(\\text{complemento, e36})"],
        contexto=("La probabilidad clásica es la definición más antigua y más "
                  "intuitiva, la de Laplace: si un experimento tiene un número "
                  "finito de resultados y todos son igualmente probables, la "
                  "probabilidad de un evento es simplemente el cociente entre los "
                  "casos FAVORABLES (los que cumplen el evento) y los casos TOTALES "
                  "(todos los del espacio muestral). Sacar un corazón de una baraja: "
                  "13 favorables sobre 52 totales, 1/4. Sacar par con un dado: 3 "
                  "sobre 6, 1/2. Su enorme virtud es que reduce la probabilidad a "
                  "CONTAR, y su enorme limitación es que exige equiprobabilidad —una "
                  "condición que hay que justificar, no suponer— y un espacio "
                  "finito. Pero incluso dentro de sus límites, la probabilidad "
                  "clásica esconde resultados que desafían por completo la "
                  "intuición, y ninguno tan famoso como la PARADOJA DEL CUMPLEAÑOS: "
                  "¿cuántas personas hacen falta en una sala para que sea más "
                  "probable que no que al menos dos compartan cumpleaños? La "
                  "intuición grita 'muchísimas, quizás cientos' —hay 365 días—. La "
                  "respuesta es 23. Con 23 personas la probabilidad ya supera el "
                  "50%, y con 57 es prácticamente segura (99%). La forma de "
                  "calcularlo es un ejemplo perfecto de probabilidad clásica más el "
                  "truco del complemento (e36): en vez de contar todas las maneras "
                  "en que puede haber una coincidencia (un enredo), se cuenta la "
                  "probabilidad de que TODOS tengan cumpleaños distintos —el primero "
                  "cualquiera (365/365), el segundo distinto (364/365), el tercero "
                  "(363/365)…— y se resta de 1. La razón de que 23 baste es que lo "
                  "que importa no es el número de PERSONAS sino el número de PARES "
                  "de personas, y entre 23 personas hay 253 pares —253 oportunidades "
                  "de coincidir—. La intuición falla porque piensa linealmente (23 "
                  "vs 365) cuando el fenómeno es cuadrático (253 pares). La paradoja "
                  "del cumpleaños no es solo un truco de fiesta: es la base de "
                  "ataques criptográficos (las 'colisiones' de hash son mucho más "
                  "probables de lo que parece) y una lección permanente de que la "
                  "intuición humana para las coincidencias es pésima —por eso vemos "
                  "'milagros' y patrones donde solo hay azar con muchos pares—."),
        autores=("La definición clásica: Pierre-Simon Laplace (Théorie analytique "
                 "des probabilités, 1812); la paradoja del cumpleaños: Richard von "
                 "Mises (1939) la popularizó — menciones. Conocimiento estadístico "
                 "general."),
        supuestos=[
            "TODOS los resultados del espacio muestral son EQUIPROBABLES: es la condición central de la definición clásica; sin ella, contar no da la probabilidad (hay que usar la frecuentista, e38).",
            "El espacio muestral es FINITO: la definición clásica no aplica a resultados continuos (infinitos), donde cada punto tiene probabilidad 0.",
            "En el cumpleaños se supone que los 365 días son igualmente probables y las personas independientes (aproximación razonable; los nacimientos reales tienen ligeras estacionalidades que no cambian la conclusión).",
        ],
        ecuaciones=[
            Ecuacion("P(A) = \\frac{\\text{casos favorables}}{\\text{casos totales}}", "definición clásica (Laplace)",
                     "cuando todos los resultados son equiprobables, la probabilidad es el cociente de "
                     "conteos: contar favorables sobre totales."),
            Ecuacion("P(\\text{todos distintos}) = \\prod_{i=0}^{n-1}\\frac{365-i}{365}", "cumpleaños distintos",
                     "el primero cualquiera, el segundo distinto (364/365), etc.: el producto de las "
                     "probabilidades de ir esquivando los cumpleaños ya usados."),
            Ecuacion("P(\\text{coincidencia}) = 1 - P(\\text{distintos})", "el complemento",
                     "es mucho más fácil calcular 'todos distintos' y restar de 1 que contar todas las "
                     "coincidencias posibles — el truco del complemento (e36)."),
        ],
        intuicion=("La probabilidad clásica enseña que, cuando el terreno es "
                   "equiprobable, la probabilidad es pura combinatoria: contar bien. "
                   "Y la paradoja del cumpleaños enseña algo más profundo y "
                   "perturbador: que nuestra intuición para las coincidencias está "
                   "rota. Vemos coincidencias como milagrosas —'¡qué casualidad que "
                   "nos encontráramos!', '¡soñé con esto y pasó!'— porque contamos "
                   "mal el número de oportunidades. En una sala de 23 hay 253 pares; "
                   "en una vida de millones de momentos hay billones de pares de "
                   "cosas que podrían coincidir, así que las coincidencias "
                   "asombrosas no solo son posibles: son INEVITABLES. La lección que "
                   "un estadístico se lleva es la 'ley de los números verdaderamente "
                   "grandes': con suficientes oportunidades, hasta lo improbable "
                   "ocurre rutinariamente, y confundir 'improbable en un caso' con "
                   "'improbable en general' es la raíz de la superstición, de creer "
                   "en videntes (que aciertan por azar entre miles de intentos) y de "
                   "sobreinterpretar patrones en los datos (el 'p-hacking', e103). La "
                   "paradoja del cumpleaños es, en pequeño, toda una filosofía: no te "
                   "impresiones por una coincidencia sin preguntarte primero cuántas "
                   "oportunidades hubo de que ocurriera alguna."),
        equilibrio=("La probabilidad clásica P=favorable/total requiere Ω finito y "
                    "equiprobable. En el cumpleaños, P(coincidencia) crece con n² (por "
                    "los pares): cruza 0.5 en n=23 y 0.99 en n=57. Coincide con la "
                    "frecuentista (e38) al simular. No hay 'equilibrio': es conteo "
                    "sobre un espacio equiprobable."),
        limitaciones=[
            "Exige EQUIPROBABILIDAD: si los resultados no son igualmente probables (un dado cargado, una ruleta sesgada), contar da la respuesta equivocada — hay que estimar por frecuencia (e38).",
            "Solo para espacios FINITOS: no aplica a variables continuas (infinitos resultados), donde se usan densidades (e47).",
            "Contar puede ser durísimo: en problemas grandes, el número de casos favorables/totales exige combinatoria avanzada, y a veces solo la simulación (e38, Monte Carlo, e176) resuelve.",
        ],
        evolucion=("Da la primera definición operativa de probabilidad (favorable/"
                   "total sobre Ω, e35), usando complemento y operaciones de eventos "
                   "(e36). Su límite —exigir equiprobabilidad— motiva la definición "
                   "FRECUENTISTA (e38), que estima P repitiendo el experimento; ambas "
                   "coinciden cuando aplican (verificado por simulación). La paradoja "
                   "del cumpleaños ilustra por qué la simulación (e176) y el "
                   "escepticismo ante coincidencias son esenciales, y adelanta la "
                   "'ley de los números grandes' (e64). El conteo combinatorio que "
                   "exige es la base de las distribuciones discretas (binomial, e50)."),
    ),
    escenarios=[
        Escenario("paradoja", "la paradoja (23 personas): >50%",
                  {"n": 23},
                  "con 23 personas, P(coincidencia)=50.7%: más probable que no. El "
                  "resultado que casi nadie adivina, porque hay 253 pares de "
                  "personas —253 chances de coincidir—, no 23.",
                  cadena=["23 personas en una sala", "hay 253 PARES de personas (no 23)",
                          "muchas más chances de coincidir de lo que parece", "P(coincidencia)=50.7% (>50%): la paradoja"]),
        Escenario("casi_seguro", "grupo grande (57 personas): ~99%",
                  {"n": 57},
                  "con 57 personas la coincidencia es casi segura (99%): la "
                  "probabilidad se dispara porque los pares crecen con n². Con 70 es "
                  "prácticamente 100% —y aún estamos lejos de 365—.",
                  cadena=["57 personas", "1596 pares posibles (crece con n²)",
                          "casi imposible que todos sean distintos", "P(coincidencia)≈99%: casi seguro"]),
    ],
    verificaciones=[
        Verificacion("probabilidad clásica = favorables / totales", _v_favorable_sobre_total),
        Verificacion("paradoja del cumpleaños: n=23 → P>50%", _v_paradoja_23),
        Verificacion("n=57 → P>99% (crece con los pares, n²)", _v_casi_seguro_57),
        Verificacion("clásica (contar) = frecuentista (simular)", _v_clasica_coincide_frecuentista),
    ],
    notas="Probabilidad clásica (Laplace): P=casos favorables/casos totales, si todos equiprobables. Paradoja del cumpleaños: con 23 personas P(coincidencia)>50% (hay 253 PARES, crece con n²) — la intuición falla con coincidencias. Se calcula por complemento (1−P(todos distintos)). Coincide con la frecuentista (e38).",
)
