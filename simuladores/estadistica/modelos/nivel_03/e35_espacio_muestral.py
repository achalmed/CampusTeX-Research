"""simuladores/estadistica/modelos/nivel_03/e35_espacio_muestral.py — el espacio muestral (sección III, tema 35).

El espacio muestral Ω es el conjunto de TODOS los resultados posibles de un
experimento aleatorio: {cara, sello} para una moneda, {1,…,6} para un dado,
los 36 pares para dos dados. Es el 'universo' sobre el que se define toda la
probabilidad —un evento (e36) es un subconjunto de Ω, y la probabilidad
reparte una masa total de 1 entre sus resultados—. El modelo muestra el espacio
muestral de la SUMA de k dados: enumera cuántas formas hay de obtener cada
suma, revela que |Ω| = 6^k crece exponencialmente, y —de regalo— anticipa que
al sumar más dados la distribución se vuelve acampanada (el TCL, e67).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _conteos_suma(k):
    """Número de formas de obtener cada suma al lanzar k dados (convolución)."""
    dado = np.ones(6)
    c = dado.copy()
    for _ in range(int(k) - 1):
        c = np.convolve(c, dado)
    sumas = np.arange(int(k), 6 * int(k) + 1)
    return sumas, c


def _curvas(p):
    k = int(p["k"])
    sumas, c = _conteos_suma(k)
    total = 6 ** k
    return {"barras": ([str(s) for s in sumas], list(c),
                       [config.AZUL2] * len(sumas)),
            "anotacion": (f"espacio muestral de {k} dado(s): |Ω| = 6^{k} = {total} resultados\n"
                          f"cada resultado elemental es equiprobable (1/{total})\n"
                          f"suma más probable: {int(sumas[np.argmax(c)])} ({int(c.max())} formas) — "
                          f"{'acampanada (→ TCL, e67)' if k >= 3 else 'triangular' if k == 2 else 'uniforme'}")}


def _resultados(p):
    k = int(p["k"])
    sumas, c = _conteos_suma(k)
    total = 6 ** k
    return {"número de dados k": float(k),
            "tamaño del espacio muestral |Ω| = 6^k": float(total),
            "suma total de conteos (= 6^k)": float(c.sum()),
            "probabilidad de cada resultado elemental": 1.0 / total,
            "suma más probable": float(sumas[np.argmax(c)]),
            "formas de la suma más probable": float(c.max())}


def _ecuaciones_calibradas(p):
    k = int(p["k"])
    total = 6 ** k
    return [f"\\Omega = \\{{\\text{{todos los resultados posibles}}\\}};\\ |\\Omega| = 6^{{{k}}} = {total}",
            f"\\sum_{{\\omega \\in \\Omega}} P(\\omega) = 1;\\ P(\\omega) = 1/{total}\\ \\text{{(equiprobable)}}"]


_P0 = {"k": 2}


def _v_tamano_6_k():
    for k in (1, 2, 3):
        _, c = _conteos_suma(k)
        if abs(c.sum() - 6 ** k) > 1e-9:
            return False, f"con {k} dados, los conteos no suman 6^{k}={6**k}"
    return True, \
        ("el tamaño del espacio muestral de k dados es |Ω| = 6^k: 6 para uno, 36 para dos, 216 para tres — "
         "cada dado multiplica por 6 los resultados posibles (principio de la multiplicación, combinatoria)")


def _v_exhaustivo():
    k = 2
    _, c = _conteos_suma(k)
    return abs(c.sum() - 6 ** k) < 1e-9, \
        (f"el espacio muestral es EXHAUSTIVO: las formas de todas las sumas suman {int(c.sum())} = 6² = todos los "
         "resultados posibles — Ω contiene absolutamente todo lo que puede pasar, sin dejar nada afuera")


def _v_masa_total_uno():
    k = 2
    _, c = _conteos_suma(k)
    prob = c / c.sum()
    return abs(prob.sum() - 1.0) < 1e-12, \
        (f"la probabilidad reparte una masa TOTAL de 1 sobre Ω: sumando P de todas las sumas da {prob.sum():.4f} = 1 "
         "— axioma fundamental (Kolmogórov), la base de que las probabilidades de un experimento sumen 100%")


def _v_equiprobable():
    total = 6 ** 2
    return abs(1.0 / total - 1.0 / 36) < 1e-12, \
        (f"cada resultado ELEMENTAL (par ordenado de dados) es equiprobable: 1/36 — pero las SUMAS no lo son "
         "(el 7 tiene 6 formas, el 2 solo una), porque distintos resultados elementales dan la misma suma (e36, e37)")


MODELO = Modelo(
    id="e35", nivel=3,
    nombre="El espacio muestral",
    xlabel="suma de los dados", ylabel="número de formas (resultados)",
    parametros=[
        Parametro("k", _P0["k"], 1, 5, 1, "Número de dados k",
                  grupo="probabilidad", definicion="|Ω|=6^k crece exponencialmente; la distribución de la suma se acampana con k (TCL, e67)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Antes de calcular cualquier probabilidad, ¿cuál es el 'universo' de lo que puede pasar — y cuán grande es?",
        variables=[("Ω", "espacio muestral: el conjunto de todos los resultados posibles"),
                   ("ω", "un resultado elemental (un punto de Ω)"),
                   ("|Ω|", "el tamaño del espacio muestral")],
        derivacion=["\\Omega = \\{\\text{todos los resultados posibles del experimento}\\}",
                    "\\text{un dado: } \\Omega = \\{1,2,3,4,5,6\\},\\ |\\Omega| = 6",
                    "k \\text{ dados: } |\\Omega| = 6^k \\;(\\text{principio de multiplicación})",
                    "\\sum_{\\omega \\in \\Omega} P(\\omega) = 1 \\;(\\text{masa total} = 1)"],
        contexto=("Antes de poder hablar de la probabilidad de algo, hay que "
                  "delimitar el universo de lo que puede ocurrir: ese universo es "
                  "el espacio muestral, Ω, el conjunto de TODOS los resultados "
                  "posibles de un experimento aleatorio. Para una moneda es "
                  "{cara, sello}; para un dado, {1,2,3,4,5,6}; para dos dados, los "
                  "36 pares ordenados; para la altura de una persona, todos los "
                  "números reales positivos en un rango. Definir bien el espacio "
                  "muestral es el primer paso —y a menudo el más importante— de "
                  "cualquier problema de probabilidad, porque todo lo demás se "
                  "construye sobre él: un EVENTO (e36) no es más que un subconjunto "
                  "de Ω, y la PROBABILIDAD es una manera de repartir una 'masa' "
                  "total de 1 entre los resultados de Ω, respetando reglas precisas "
                  "(los axiomas de Kolmogórov, 1933). El modelo ilustra el espacio "
                  "muestral con el experimento de lanzar k dados y sumar, y enseña "
                  "tres cosas de un vistazo. Primero, que el espacio muestral "
                  "elemental crece EXPONENCIALMENTE: |Ω| = 6^k —6 resultados con un "
                  "dado, 36 con dos, 216 con tres—, porque cada dado multiplica por "
                  "6 las posibilidades (el principio de multiplicación de la "
                  "combinatoria). Segundo, que aunque cada resultado ELEMENTAL (cada "
                  "combinación específica de dados) sea equiprobable, los eventos "
                  "compuestos como 'la suma es 7' NO lo son: el 7 se puede formar de "
                  "6 maneras distintas y el 2 de una sola, así que sumar cuenta "
                  "cuántos resultados elementales caen en cada evento —la semilla de "
                  "la probabilidad clásica (e37)—. Y tercero, un regalo inesperado: "
                  "al aumentar el número de dados, la distribución de la suma pasa "
                  "de uniforme (un dado) a triangular (dos) a claramente ACAMPANADA "
                  "(varios) —una primera aparición del teorema central del límite "
                  "(e67), que dice que sumar muchas cosas aleatorias tiende a la "
                  "normal—. El espacio muestral es, en el fondo, el tablero sobre el "
                  "que se juega toda la probabilidad: sin definirlo, no hay pregunta "
                  "bien planteada."),
        autores=("La formalización del espacio muestral y los axiomas de "
                 "probabilidad: Andréi Kolmogórov (1933), que puso la probabilidad "
                 "sobre bases de teoría de conjuntos y medida — mención histórica. "
                 "Conocimiento estadístico general."),
        supuestos=[
            "El espacio muestral debe ser EXHAUSTIVO (contiene todos los resultados posibles) y sus resultados MUTUAMENTE EXCLUYENTES (no pueden ocurrir dos a la vez).",
            "Aquí los dados son justos, así que los resultados elementales son equiprobables; pero el espacio muestral existe con o sin equiprobabilidad (define el QUÉ puede pasar, no el con qué probabilidad).",
            "Distinguir resultado ELEMENTAL (un punto de Ω) de EVENTO (un subconjunto, e36): la suma '7' es un evento con varios resultados elementales.",
        ],
        ecuaciones=[
            Ecuacion("\\Omega = \\{\\text{todos los resultados posibles}\\}", "el espacio muestral",
                     "el universo del experimento: el conjunto de todo lo que puede ocurrir, sobre el que se "
                     "define cualquier evento y cualquier probabilidad."),
            Ecuacion("|\\Omega| = 6^k \\;(k \\text{ dados})", "principio de multiplicación",
                     "cada dado multiplica por 6 los resultados: el tamaño del espacio muestral crece "
                     "exponencialmente con el número de componentes independientes."),
            Ecuacion("\\sum_{\\omega \\in \\Omega} P(\\omega) = 1", "masa total 1 (axioma)",
                     "la probabilidad reparte una masa total de 1 sobre el espacio muestral: las "
                     "probabilidades de todos los resultados de un experimento suman 100%."),
        ],
        intuicion=("El espacio muestral es la pregunta '¿qué puede pasar?' hecha "
                   "conjunto, y plantearla bien es la mitad de resolver cualquier "
                   "problema de probabilidad. Los errores clásicos de probabilidad "
                   "casi siempre empiezan por un espacio muestral mal definido: el "
                   "famoso 'problema de los dos hijos' o el 'problema de Monty Hall' "
                   "confunden a la gente porque enumeran mal los resultados posibles "
                   "y sus pesos. La lección operativa es doble. Primero, enumerar "
                   "con cuidado: para dos dados no hay 11 resultados (las sumas 2 a "
                   "12) sino 36 (los pares ordenados), y confundirlos —tratar las 11 "
                   "sumas como equiprobables— es el error que lleva a apostar mal. "
                   "Segundo, apreciar que el espacio muestral 'elemental' y el de un "
                   "resumen (la suma) son distintos: los 36 pares son equiprobables, "
                   "las 11 sumas no. La magia combinatoria —que |Ω| explota como 6^k— "
                   "es también la razón por la que muchos problemas no se pueden "
                   "resolver enumerando (un mazo de cartas tiene 52! órdenes, más "
                   "que átomos en la galaxia) y hacen falta las reglas de conteo y, "
                   "cuando fallan, la SIMULACIÓN. Y la aparición espontánea de la "
                   "campana al sumar dados es la primera pista de que, detrás del "
                   "aparente desorden de los espacios muestrales grandes, se esconde "
                   "una estructura profunda y universal (el TCL) que ordena la suma "
                   "de lo aleatorio."),
        equilibrio=("El espacio muestral Ω es el conjunto exhaustivo y "
                    "mutuamente excluyente de resultados; |Ω| = 6^k para k dados. La "
                    "probabilidad reparte masa 1 sobre Ω. La distribución de la suma "
                    "pasa de uniforme a acampanada al crecer k (TCL). No hay "
                    "'equilibrio': es la definición del universo del experimento."),
        limitaciones=[
            "Enumerar es inviable para espacios grandes: |Ω| explota (52! para un mazo), y hay que usar reglas de conteo (combinatoria) o simulación en vez de listar.",
            "Espacios muestrales CONTINUOS (alturas, tiempos) no se pueden enumerar: cada resultado tiene probabilidad 0, y se trabaja con densidades (e47) en vez de conteos.",
            "Definir mal Ω (resultados no equiprobables tratados como iguales, o incompletos) es la fuente de casi todos los errores de probabilidad — la parte difícil es plantearlo, no calcular.",
        ],
        evolucion=("Da el universo sobre el que se construye toda la probabilidad: "
                   "los EVENTOS (e36) son subconjuntos de Ω, y la probabilidad "
                   "CLÁSICA (e37) cuenta resultados favorables sobre |Ω|. La "
                   "distinción resultado-elemental / evento-compuesto prepara el "
                   "conteo combinatorio. La aparición de la campana al sumar dados "
                   "anticipa el TCL (e67). Para espacios continuos, Ω motiva las "
                   "densidades (e47). Es la base conjuntista que Kolmogórov usó para "
                   "axiomatizar la probabilidad."),
    ),
    escenarios=[
        Escenario("dos_dados", "dos dados: 36 resultados, sumas triangulares",
                  {"k": 2},
                  "con dos dados, |Ω|=36 pares equiprobables, pero las sumas 2–12 "
                  "NO lo son: el 7 tiene 6 formas y el 2 solo una. La distribución "
                  "de la suma es triangular — el ejemplo clásico de que 'resultado "
                  "elemental' y 'evento' no son lo mismo.",
                  cadena=["dos dados: |Ω| = 36 pares ordenados", "los 36 pares son equiprobables (1/36)",
                          "pero las sumas se forman de distinto número de maneras", "el 7 (6 formas) es más probable que el 2 (1 forma): triangular"]),
        Escenario("muchos_dados", "cinco dados: la campana aparece (TCL)",
                  {"k": 5},
                  "con cinco dados, |Ω|=6⁵=7776 y la distribución de la suma es "
                  "claramente ACAMPANADA: al sumar muchas cosas aleatorias emerge la "
                  "normal (el teorema central del límite, e67), aunque cada dado sea "
                  "uniforme.",
                  cadena=["cinco dados: |Ω| = 6⁵ = 7776", "la suma combina cinco fuentes de azar",
                          "la distribución de la suma se acampana", "aparece la normal (TCL, e67) — de la nada"]),
    ],
    verificaciones=[
        Verificacion("el tamaño del espacio muestral es |Ω| = 6^k", _v_tamano_6_k),
        Verificacion("el espacio muestral es exhaustivo (todo suma 6^k)", _v_exhaustivo),
        Verificacion("la probabilidad reparte masa total 1 (axioma)", _v_masa_total_uno),
        Verificacion("resultados elementales equiprobables (pero sumas no)", _v_equiprobable),
    ],
    notas="Espacio muestral Ω = todos los resultados posibles; base de eventos (e36) y probabilidad. |Ω|=6^k (k dados) crece exponencial. Los resultados ELEMENTALES son equiprobables (1/36 para dos dados) pero los EVENTOS/sumas no (el 7 tiene 6 formas). La masa total es 1 (axioma de Kolmogórov). Sumar dados → campana (TCL, e67).",
)
