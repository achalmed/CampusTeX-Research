"""simuladores/estadistica/modelos/nivel_02/e23_cuartiles.py — los cuartiles y el rango intercuartílico (sección II, tema 23).

Los cuartiles parten los datos ordenados en CUATRO partes iguales: Q1 (25% por
debajo), Q2 (= la mediana, 50%) y Q3 (75%). Su diferencia, el rango
intercuartílico IQR = Q3 − Q1, mide la dispersión del 50% CENTRAL de los datos
—ignorando las colas—, y por eso es una medida de dispersión ROBUSTA (la prima
de la mediana, e18), inmune a los atípicos. Son la base del diagrama de caja
(e15) y de la regla 1.5·IQR para detectar atípicos (e33). El modelo muestra la
función de distribución empírica con Q1/Q2/Q3 marcados y deja mover un atípico
para ver que el IQR no se inmuta (mientras el rango explota).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_BASE = np.array([2, 4, 5, 6, 6, 7, 8, 9, 11, 13], float)   # 10 datos "normales"


def _con_outlier(o):
    return np.append(_BASE, o)


def _cuartiles(x):
    return [float(np.percentile(x, q)) for q in (25, 50, 75)]


def _curvas(p):
    x = np.sort(_con_outlier(p["outlier"]))
    n = len(x)
    ecdf_y = (np.arange(1, n + 1)) / n
    q1, q2, q3 = _cuartiles(_con_outlier(p["outlier"]))
    return {"lineas": {"función de distribución empírica  F(x)": (x, ecdf_y, config.AZUL2),
                       "cuartos: 25% · 50% · 75%": (np.array([x.min(), x.max()]),
                                                    np.array([0.25, 0.25]), config.GRIS)},
            "puntos": [(q1, 0.25, f"Q1={q1:.1f}"), (q2, 0.50, f"Q2={q2:.1f} (mediana)"),
                       (q3, 0.75, f"Q3={q3:.1f}")],
            "anotacion": (f"IQR = Q3 − Q1 = {q3:.1f} − {q1:.1f} = {q3-q1:.1f} (dispersión del 50% central)\n"
                          f"rango = {x.max()-x.min():.1f} (se lo lleva el atípico)\n"
                          "el IQR es ROBUSTO: ignora las colas")}


def _resultados(p):
    x = _con_outlier(p["outlier"])
    q1, q2, q3 = _cuartiles(x)
    return {"Q1 (primer cuartil, 25%)": q1,
            "Q2 (mediana, 50%)": q2,
            "Q3 (tercer cuartil, 75%)": q3,
            "IQR = Q3 − Q1 (robusto)": q3 - q1,
            "rango = máx − mín (NO robusto)": float(x.max() - x.min()),
            "mediana de _BASE (comparación)": float(np.median(_BASE))}


def _ecuaciones_calibradas(p):
    x = _con_outlier(p["outlier"])
    q1, q2, q3 = _cuartiles(x)
    return [f"Q1={q1:.1f}\\ (25\\%),\\ Q2={q2:.1f}\\ (\\text{{mediana}}),\\ Q3={q3:.1f}\\ (75\\%)",
            f"\\mathrm{{IQR}} = Q_3 - Q_1 = {q3-q1:.1f}\\ \\text{{(dispersión robusta del 50\\% central)}}"]


_P0 = {"outlier": 13.0}


def _v_q2_es_mediana():
    x = _con_outlier(13.0)
    q1, q2, q3 = _cuartiles(x)
    return abs(q2 - float(np.median(x))) < 1e-9, \
        (f"Q2 = {q2:.1f} = la mediana (e18): el segundo cuartil es exactamente el valor central, el que deja el "
         "50% a cada lado — los cuartiles generalizan la mediana a cortes de 25%")


def _v_parten_en_cuartos():
    x = _con_outlier(13.0)
    q1, q2, q3 = _cuartiles(x)
    debajo_q1 = np.mean(x < q1)
    debajo_q3 = np.mean(x < q3)
    return debajo_q1 <= 0.30 and 0.70 <= debajo_q3 <= 0.80, \
        (f"los cuartiles parten en cuatro: ~25% de los datos por debajo de Q1 ({q1:.1f}) y ~75% por debajo de "
         f"Q3 ({q3:.1f}) — cada cuarto tiene la misma cantidad de observaciones")


def _v_iqr_robusto():
    q1a, _, q3a = _cuartiles(_con_outlier(13.0))
    q1b, _, q3b = _cuartiles(_con_outlier(100.0))
    return abs((q3a - q1a) - (q3b - q1b)) < 1e-9, \
        (f"el IQR es ROBUSTO: llevar el atípico de 13 a 100 NO cambia el IQR (sigue {q3a-q1a:.1f}) — mide el 50% "
         "central e ignora las colas, como la mediana (e18); el rango, en cambio, se dispara")


def _v_iqr_menor_que_rango():
    x = _con_outlier(100.0)
    q1, q2, q3 = _cuartiles(x)
    return (q3 - q1) < (x.max() - x.min()), \
        (f"con un atípico, el IQR ({q3-q1:.1f}) es muchísimo menor que el rango ({x.max()-x.min():.0f}): el IQR "
         "describe la dispersión típica; el rango, la máxima — y el rango se lo come el outlier")


MODELO = Modelo(
    id="e23", nivel=2,
    nombre="Los cuartiles y el rango intercuartílico",
    xlabel="valor", ylabel="proporción acumulada  F(x)",
    parametros=[
        Parametro("outlier", _P0["outlier"], 5.0, 100.0, 1.0, "Valor del dato extremo",
                  grupo="descriptiva", definicion="al alejarlo, el IQR (50% central) no se mueve; el rango sí"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo se mide la dispersión de los datos sin que un atípico la arruine — y qué es el 50% central?",
        variables=[("Q1, Q2, Q3", "primer cuartil (25%), mediana (50%), tercer cuartil (75%)"),
                   ("IQR", "rango intercuartílico = Q3 − Q1, dispersión del 50% central"),
                   ("F(x)", "función de distribución empírica: proporción de datos ≤ x")],
        derivacion=["\\text{ordenar los datos y acumular: } F(x) = \\tfrac{\\#\\{x_i \\le x\\}}{n}",
                    "Q_k = \\text{el valor donde } F \\text{ cruza } k/4 \\;(k=1,2,3)",
                    "Q_2 = \\text{mediana} \\;;\\; \\mathrm{IQR} = Q_3 - Q_1",
                    "\\mathrm{IQR} \\text{ mide el 50\\% central} \\Rightarrow \\text{robusto (ignora colas)}"],
        contexto=("Los cuartiles responden a la misma necesidad que la mediana "
                  "—describir los datos sin que los extremos manden— pero con más "
                  "resolución: en lugar de partir en dos mitades, parten en cuatro "
                  "cuartos iguales. El primer cuartil Q1 deja el 25% de los datos "
                  "por debajo; el segundo Q2 es exactamente la mediana (50%); el "
                  "tercero Q3, el 75%. Su diferencia, el rango intercuartílico IQR = "
                  "Q3 − Q1, es una de las medidas de dispersión más útiles de toda "
                  "la estadística, porque mide la extensión del 50% CENTRAL de los "
                  "datos —del cuarto al tercer cuartil— e ignora por completo las "
                  "colas. Eso lo hace ROBUSTO: es a la dispersión lo que la mediana "
                  "es al centro. Mientras el rango (máximo − mínimo) y la desviación "
                  "estándar (e27) se disparan con un solo atípico, el IQR ni se "
                  "inmuta: puedes llevar el dato más alto al infinito y el IQR sigue "
                  "igual, porque solo le importa dónde caen los cuartiles del medio. "
                  "Los cuartiles son, además, la materia prima del DIAGRAMA DE CAJA "
                  "(boxplot, e15) —la caja va de Q1 a Q3, con la mediana adentro, y "
                  "los 'bigotes' se extienden hasta 1.5·IQR—, y de la regla estándar "
                  "para detectar atípicos (e33): un dato es sospechoso si cae por "
                  "debajo de Q1 − 1.5·IQR o por encima de Q3 + 1.5·IQR. Toda esta "
                  "familia —cuartiles, IQR, boxplot, regla 1.5·IQR— viene de John "
                  "Tukey y comparte una filosofía: resumir y visualizar la forma de "
                  "los datos con estadísticos que los outliers no puedan secuestrar. "
                  "La lección práctica: cuando reportes dispersión de datos que "
                  "podrían tener extremos (ingresos, tiempos, precios), el IQR dice "
                  "la verdad; el rango y la desviación, a medias."),
        autores=("Los cuartiles, el IQR y el boxplot: John Tukey (Exploratory Data "
                 "Analysis, 1977) — mención histórica. Conocimiento estadístico "
                 "general."),
        supuestos=[
            "Datos al menos ORDINALES: los cuartiles solo requieren ordenar (como la mediana), no distancias.",
            "Hay varias convenciones para interpolar cuartiles con n pequeño (aquí se usa la de numpy, lineal); las diferencias son menores y desaparecen con n grande.",
            "El IQR describe el 50% central; NO informa de las colas (para eso están el rango, e26, o los percentiles extremos, e24) — es robusto justamente porque las ignora.",
        ],
        ecuaciones=[
            Ecuacion("Q_1, Q_2, Q_3 : \\; F(Q_k) = k/4", "los tres cuartiles",
                     "los valores donde la proporción acumulada cruza 25%, 50% y 75%: parten los datos "
                     "ordenados en cuatro cuartos con igual número de observaciones."),
            Ecuacion("\\mathrm{IQR} = Q_3 - Q_1", "rango intercuartílico",
                     "la extensión del 50% central de los datos: una medida de dispersión ROBUSTA, inmune a "
                     "los atípicos porque ignora las colas."),
            Ecuacion("Q_2 = \\text{mediana}", "el segundo cuartil es la mediana",
                     "los cuartiles generalizan la mediana (e18): Q2 es el corte del 50%, y Q1/Q3 son las "
                     "medianas de cada mitad."),
        ],
        intuicion=("La imagen es la de repartir a los datos ordenados en cuatro "
                   "filas del mismo tamaño: los cuartiles son las tres líneas que "
                   "las separan, y el IQR es el ancho de las dos filas del medio. "
                   "Ese 'ancho del medio' es una idea poderosa: describe cómo de "
                   "dispersos están los datos TÍPICOS, sin dejarse impresionar por "
                   "el más rico, el más lento o el más caro. Por eso, cuando quieres "
                   "saber si dos grupos son parecidos, comparar sus cajas (Q1, "
                   "mediana, Q3) dice mucho más que comparar sus promedios: revela "
                   "el centro, la dispersión y la asimetría de un vistazo, y aguanta "
                   "los outliers. La regla 1.5·IQR de Tukey es la formalización de "
                   "'¿qué tan lejos es demasiado lejos?': un dato a más de una vez y "
                   "media el ancho de la caja fuera de ella es, estadísticamente, "
                   "sospechoso —candidato a investigar (e33)—. Toda la caja de "
                   "herramientas robusta —mediana, IQR, MAD (e32), boxplot— comparte "
                   "el mismo espíritu que hace grande al análisis exploratorio de "
                   "datos: mirar la forma antes de calcular un número, y usar "
                   "estadísticos que la realidad sucia no pueda engañar."),
        equilibrio=("Los cuartiles son únicos (dada una convención de "
                    "interpolación); Q2 = mediana. El IQR = Q3 − Q1 es robusto "
                    "(punto de ruptura 25%): inmune a los atípicos de las colas, a "
                    "diferencia del rango (e26) y la desviación (e27). Es la "
                    "dispersión del 50% central."),
        limitaciones=[
            "El IQR ignora las colas por diseño: es su fuerza (robustez) y su límite (no dice nada de los extremos, que a veces son lo importante — un fraude, una crisis).",
            "Convención de interpolación: con muestras muy pequeñas, distintos métodos dan cuartiles algo distintos; irrelevante con n grande.",
            "Menos tratable algebraicamente que la desviación estándar: los cuartiles no tienen fórmulas suaves, lo que complica su teoría de muestreo (aunque hay resultados robustos).",
        ],
        evolucion=("Generalizan la mediana (e18) a cortes de 25% y dan la dispersión "
                   "robusta (IQR), complemento del rango (e26, no robusto) y la "
                   "desviación (e27, no robusta). Se extienden a percentiles (e24) y "
                   "deciles (e25). Son la base del diagrama de caja (e15) y de la "
                   "regla 1.5·IQR para detectar atípicos (e33), cerrando el arco de "
                   "la estadística robusta con la mediana (e18) y la MAD (e32)."),
    ),
    escenarios=[
        Escenario("sin_outlier", "dato extremo moderado (13, dentro del patrón)",
                  {"outlier": 13.0},
                  "con el dato en 13 (el máximo natural), el IQR y el rango son "
                  "razonables y parecidos en escala. Datos sin atípicos: todas las "
                  "medidas de dispersión concuerdan.",
                  cadena=["dato extremo en 13 (dentro del patrón)", "cuartiles Q1, Q2, Q3 bien espaciados",
                          "IQR ≈ dispersión típica", "rango también razonable — datos limpios"]),
        Escenario("con_outlier", "dato extremo lejano (100)",
                  {"outlier": 100.0},
                  "al llevar el dato a 100, el rango se dispara a ~98 pero el IQR no "
                  "se mueve: el 50% central sigue igual. El IQR describe la "
                  "dispersión honesta; el rango, secuestrado por el outlier, engaña.",
                  cadena=["dato extremo en 100 (lejano)", "el rango salta a ~98 (lo secuestra el outlier)",
                          "pero el IQR no cambia (ignora las colas)", "el IQR es la dispersión robusta"]),
    ],
    verificaciones=[
        Verificacion("Q2 es la mediana (los cuartiles la generalizan)", _v_q2_es_mediana),
        Verificacion("los cuartiles parten los datos en cuartos (25%/75%)", _v_parten_en_cuartos),
        Verificacion("el IQR es robusto (el atípico no lo mueve)", _v_iqr_robusto),
        Verificacion("con atípico, IQR ≪ rango", _v_iqr_menor_que_rango),
    ],
    notas="Cuartiles Q1/Q2/Q3 parten los datos en cuartos (Q2=mediana). IQR=Q3−Q1 = dispersión ROBUSTA del 50% central (ignora colas), a diferencia del rango (e26) y la desviación (e27). Base del boxplot (e15) y de la regla 1.5·IQR para atípicos (e33).",
)
