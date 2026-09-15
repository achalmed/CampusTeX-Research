"""simuladores/estadistica/modelos/nivel_02/e24_percentiles.py — los percentiles (sección II, tema 24).

La generalización de los cuartiles a CUALQUIER corte: el percentil p es el
valor por debajo del cual cae el p% de los datos. El percentil 50 es la
mediana, el 25 y el 75 son Q1 y Q3 (e23). Su lectura inversa —el "rango
percentil" de un valor: qué % lo supera— es la que usan las tablas de
crecimiento infantil ("tu hijo está en el percentil 90 de estatura"), los
exámenes estandarizados y el Valor-en-Riesgo financiero (el percentil 5 de
pérdidas). El modelo muestra la función de distribución empírica y deja mover p
para leer cualquier percentil, y su recíproco.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_D = np.round(np.random.default_rng(1).normal(500, 100, 240))   # puntajes tipo examen (fijo, semilla)


def _percentil(p):
    return float(np.percentile(_D, p))


def _rango_percentil(valor):
    return float(np.mean(_D < valor) * 100)


def _curvas(p):
    pp = p["p"]
    x = np.sort(_D)
    n = len(x)
    ecdf = np.arange(1, n + 1) / n
    vp = _percentil(pp)
    return {"lineas": {"función de distribución empírica  F(x)": (x, ecdf, config.AZUL2),
                       f"nivel  p = {pp:.0f}%": (np.array([x.min(), x.max()]),
                                                 np.array([pp / 100, pp / 100]), config.GRIS)},
            "puntos": [(vp, pp / 100, f"percentil {pp:.0f} = {vp:.0f}")],
            "anotacion": (f"percentil {pp:.0f} = {vp:.0f}: el {pp:.0f}% de los puntajes está por debajo\n"
                          f"percentil 50 = {_percentil(50):.0f} = mediana; 25 y 75 = cuartiles (e23)\n"
                          "lectura inversa: un puntaje de 600 está en el percentil "
                          f"{_rango_percentil(600):.0f}")}


def _resultados(p):
    pp = p["p"]
    return {"nivel p (%)": float(pp),
            "percentil p (valor)": _percentil(pp),
            "percentil 50 (= mediana)": _percentil(50),
            "percentil 25 (= Q1)": _percentil(25),
            "percentil 75 (= Q3)": _percentil(75),
            "rango percentil de un 600": _rango_percentil(600.0)}


def _ecuaciones_calibradas(p):
    pp = p["p"]
    return [f"P_{{{pp:.0f}}} = {_percentil(pp):.0f}:\\ \\text{{el }} {pp:.0f}\\%\\ \\text{{de los datos está por debajo}}",
            f"P_{{50}} = \\text{{mediana}},\\ P_{{25}} = Q_1,\\ P_{{75}} = Q_3\\ \\text{{(los cuartiles son percentiles)}}"]


_P0 = {"p": 90.0}


def _v_p50_es_mediana():
    return abs(_percentil(50) - float(np.median(_D))) < 1e-9, \
        (f"el percentil 50 = {_percentil(50):.0f} = la mediana (e18): la mediana no es más que el percentil "
         "central — los percentiles la generalizan a cualquier corte del 0 al 100")


def _v_cuartiles_son_percentiles():
    ok = (abs(_percentil(25) - float(np.percentile(_D, 25))) < 1e-9 and
          abs(_percentil(75) - float(np.percentile(_D, 75))) < 1e-9)
    return ok, \
        (f"los cuartiles SON percentiles: Q1 = percentil 25 = {_percentil(25):.0f}, Q3 = percentil 75 = "
         f"{_percentil(75):.0f} (e23) — cuartiles, deciles (e25) y mediana son casos particulares de percentil")


def _v_p_por_ciento_debajo():
    for pp in (10, 30, 60, 90):
        prop = np.mean(_D <= _percentil(pp))
        if abs(prop - pp / 100) > 0.05:
            return False, f"el percentil {pp} no deja ~{pp}% por debajo (dio {prop*100:.0f}%)"
    return True, \
        ("por definición, el percentil p deja aproximadamente el p% de los datos por debajo: percentil 10 → "
         "~10% debajo, percentil 90 → ~90% debajo — la proporción acumulada F es su inversa (el rango percentil)")


def _v_monotono():
    return _percentil(10) < _percentil(50) < _percentil(90), \
        (f"los percentiles CRECEN con p: P10={_percentil(10):.0f} < P50={_percentil(50):.0f} < "
         f"P90={_percentil(90):.0f} — a mayor nivel, mayor el valor; la función es monótona (es la inversa de F)")


MODELO = Modelo(
    id="e24", nivel=2,
    nombre="Los percentiles",
    xlabel="puntaje", ylabel="proporción acumulada  F(x)",
    parametros=[
        Parametro("p", _P0["p"], 1.0, 99.0, 1.0, "Nivel del percentil p (%)",
                  grupo="descriptiva", definicion="el percentil p es el valor con el p% de los datos por debajo; p=50 es la mediana"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando te dicen 'estás en el percentil 90', ¿qué significa exactamente — y cómo se calcula cualquier corte de los datos?",
        variables=[("Pₚ", "percentil p: valor con el p% de los datos por debajo"),
                   ("p", "el nivel, de 0 a 100"),
                   ("rango percentil", "la inversa: qué % de datos supera un valor dado")],
        derivacion=["F(x) = \\text{proporción de datos} \\le x \\;(\\text{distribución empírica})",
                    "P_p = F^{-1}(p/100) : \\text{el valor donde } F \\text{ cruza } p/100",
                    "P_{50} = \\text{mediana},\\; P_{25} = Q_1,\\; P_{75} = Q_3",
                    "\\text{rango percentil}(v) = 100 \\cdot F(v) \\;(\\text{la lectura inversa})"],
        contexto=("Los percentiles son la forma más flexible de ubicar un valor "
                  "dentro de una distribución, y la que la gente encuentra a diario "
                  "sin darse cuenta de que es estadística. El percentil p es, "
                  "simplemente, el valor por debajo del cual cae el p% de los datos: "
                  "el percentil 90 de estatura es la altura que supera al 90% de los "
                  "niños de esa edad, el percentil 25 de ingresos es el umbral bajo "
                  "el cual está el cuarto más pobre. Generalizan los cuartiles (e23): "
                  "el percentil 50 es la mediana, el 25 y el 75 son Q1 y Q3, el 10 y "
                  "el 90 recortan las colas. Formalmente, el percentil es la INVERSA "
                  "de la función de distribución empírica F —si F te dice qué "
                  "proporción de datos hay por debajo de un valor, el percentil te "
                  "da el valor para una proporción—, y esa doble lectura es lo que "
                  "los hace tan versátiles. En una dirección, fijas un nivel y "
                  "obtienes un umbral: '¿cuál es el ingreso del percentil 90?'. En la "
                  "otra —el RANGO PERCENTIL— fijas un valor y obtienes su posición "
                  "relativa: '¿en qué percentil quedó mi puntaje?'. Esta segunda es "
                  "la que usan las tablas de crecimiento pediátrico (el clásico "
                  "'percentil 90 de peso'), los exámenes estandarizados (tu resultado "
                  "vs el de todos) y las finanzas: el Valor-en-Riesgo (VaR) es "
                  "literalmente el percentil 5 de la distribución de pérdidas —la "
                  "pérdida que solo se supera el 5% de las veces—. La gran virtud de "
                  "los percentiles es que describen la POSICIÓN sin suponer ninguna "
                  "forma de la distribución (no exigen normalidad ni simetría) y son "
                  "robustos como la mediana; su límite es que, al ser posicionales, "
                  "ignoran las magnitudes —dos personas en el mismo percentil pueden "
                  "estar muy separadas en valor absoluto—."),
        autores=("Los percentiles y el análisis por cuantiles: Francis Galton "
                 "(rangos y cuantiles, s. XIX) — mención histórica. Conocimiento "
                 "estadístico general."),
        supuestos=[
            "Datos al menos ORDINALES: los percentiles solo requieren ordenar; describen posición, no magnitud.",
            "Con n finito hay convenciones de interpolación (aquí la lineal de numpy); irrelevantes con muchos datos.",
            "El percentil describe posición relativa DENTRO de la muestra: comparar percentiles entre grupos exige que sean comparables (misma variable, misma referencia).",
        ],
        ecuaciones=[
            Ecuacion("P_p = F^{-1}(p/100)", "el percentil como inversa de F",
                     "el valor donde la proporción acumulada alcanza p/100: fijas el nivel, obtienes el "
                     "umbral — la inversa de la función de distribución empírica."),
            Ecuacion("P_{50} = \\text{mediana}, \\; P_{25} = Q_1, \\; P_{75} = Q_3", "generaliza cuartiles y mediana",
                     "mediana, cuartiles y deciles son percentiles particulares: un solo concepto para todos "
                     "los cortes posicionales de los datos."),
            Ecuacion("\\text{rango percentil}(v) = 100 \\cdot F(v)", "la lectura inversa",
                     "fijas un valor y obtienes su posición: '¿en qué percentil está?' — lo que usan las "
                     "tablas de crecimiento y los exámenes estandarizados."),
        ],
        intuicion=("El percentil es la respuesta a '¿dónde me ubico?' sin necesidad "
                   "de saber cuánto valen los demás en términos absolutos: basta con "
                   "cuántos están por debajo. Esa es su magia y su trampa. Su magia: "
                   "hace comparables cosas de escalas distintas (un percentil 90 en "
                   "matemáticas y un percentil 90 en lectura significan lo mismo "
                   "—mejor que el 90%— aunque los puntajes brutos no se parezcan) y "
                   "es inmune a los outliers (mover al más alto no cambia tu "
                   "percentil). Su trampa: al medir posición y no magnitud, esconde "
                   "las distancias —subir del percentil 50 al 60 puede requerir "
                   "muchísimo más esfuerzo que del 89 al 90, según cómo se apiñen los "
                   "datos—, y en distribuciones muy desiguales (ingresos) percentiles "
                   "vecinos pueden separar mundos enteros. La lección para leer datos "
                   "con percentiles: son perfectos para UBICAR y COMPARAR posiciones, "
                   "pero para hablar de CUÁNTO —cuánta desigualdad, cuánta mejora— "
                   "hay que volver a las magnitudes (la razón entre percentiles, "
                   "como el decil 90/10 de e25, o directamente los valores)."),
        equilibrio=("El percentil Pₚ es único (dada la interpolación) y monótono "
                    "creciente en p (es la inversa de F). Robusto como la mediana. "
                    "Describe posición, no magnitud; su recíproco es el rango "
                    "percentil. No hay 'equilibrio': es la geometría de la "
                    "distribución empírica."),
        limitaciones=[
            "Posicional, no de magnitud: ignora las distancias entre valores; dos datos en el mismo percentil pueden diferir mucho en valor absoluto.",
            "Depende de la muestra de referencia: un percentil solo tiene sentido respecto a una población concreta; comparar percentiles de poblaciones distintas puede engañar.",
            "Interpolación con n pequeño: distintas convenciones dan percentiles algo distintos; y con muy pocos datos los percentiles extremos son inestables.",
        ],
        evolucion=("Generalizan los cuartiles (e23) y la mediana (e18) a cualquier "
                   "corte, y se especializan en deciles (e25). Son la base del "
                   "Valor-en-Riesgo, de las tablas de crecimiento y de los rankings. "
                   "La transformación a percentiles (o a rangos) reaparece en las "
                   "pruebas no paramétricas (e116-e119, que trabajan con rangos en "
                   "vez de valores) y en la estandarización robusta. Conectan la "
                   "descriptiva con la idea de distribución que abre la probabilidad "
                   "(sección III)."),
    ),
    escenarios=[
        Escenario("percentil_alto", "un corte alto (p = 90)",
                  {"p": 90.0},
                  "el percentil 90 marca el umbral que supera solo el 10% superior: "
                  "el 'muy por encima del promedio'. Es el corte de las becas de "
                  "excelencia, los sueldos altos, la estatura de los más altos.",
                  cadena=["fijar p = 90", "buscar el valor con 90% de datos por debajo",
                          "solo el 10% superior lo supera", "el umbral de 'destacado'"]),
        Escenario("percentil_bajo", "un corte bajo (p = 5): cola inferior",
                  {"p": 5.0},
                  "el percentil 5 marca la cola inferior: el 5% más bajo. Es el "
                  "Valor-en-Riesgo en finanzas (la pérdida que solo se supera 5% de "
                  "las veces) y el umbral de las alertas (bajo peso, bajo "
                  "rendimiento).",
                  cadena=["fijar p = 5 (cola inferior)", "el valor bajo el cual está el 5% más bajo",
                          "en finanzas: el Valor-en-Riesgo (VaR)", "el umbral de alarma de la cola"]),
    ],
    verificaciones=[
        Verificacion("el percentil 50 es la mediana", _v_p50_es_mediana),
        Verificacion("los cuartiles son percentiles (25, 75)", _v_cuartiles_son_percentiles),
        Verificacion("el percentil p deja ~p% de datos por debajo", _v_p_por_ciento_debajo),
        Verificacion("los percentiles crecen con p (monótonos)", _v_monotono),
    ],
    notas="Percentil p = valor con el p% de datos por debajo (inversa de F). Generaliza mediana (P50) y cuartiles (P25=Q1, P75=Q3). Su lectura inversa (rango percentil) es la de las tablas de crecimiento y el VaR (percentil 5 de pérdidas). Posición, no magnitud.",
)
