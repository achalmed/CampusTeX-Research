"""simuladores/estadistica/modelos/nivel_02/e19_moda.py — la moda (sección II, tema 19).

El valor más FRECUENTE. Es la tercera medida de tendencia central (con media
e17 y mediana e18), y la única que sirve para datos CUALITATIVOS/nominales
—donde "promediar" u "ordenar" no tienen sentido (¿el color promedio? ¿la
religión mediana?)—. Puede no existir (todos distintos), no ser única
(bimodal, multimodal), y en datos sesgados difiere de media y mediana. El
modelo muestra una distribución de frecuencias como barras y deja añadir copias
de un valor retador para ver cómo la moda cambia o empata.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_VALORES = np.arange(1, 9)                            # 1..8
_BASE = np.array([1, 2, 4, 3, 7, 3, 2, 1])           # frecuencias base; moda = valor 5 (7 veces)
_RETADOR = 3                                          # el valor cuya frecuencia sube el parámetro


def _frecuencias(extra):
    f = _BASE.copy()
    f[_RETADOR - 1] += int(extra)
    return f


def _moda(f):
    top = f.max()
    return [int(_VALORES[i]) for i in range(len(f)) if f[i] == top]


def _curvas(p):
    f = _frecuencias(p["extra"])
    modas = _moda(f)
    colores = [config.DORADO if v in modas else config.AZUL2 for v in _VALORES]
    return {"barras": ([str(v) for v in _VALORES], list(f), colores),
            "anotacion": (f"moda = {', '.join(map(str, modas))} (valor más frecuente, {int(f.max())} veces)\n"
                          f"{'BIMODAL: dos picos empatan' if len(modas) > 1 else 'unimodal: un pico'}\n"
                          "la moda sirve para datos cualitativos (media/mediana no)")}


def _resultados(p):
    f = _frecuencias(p["extra"])
    datos = np.repeat(_VALORES, f)
    modas = _moda(f)
    return {"moda (o modas)": float(modas[0]) if len(modas) == 1 else float(len(modas)),
            "frecuencia de la moda": float(f.max()),
            "¿bimodal? (nº de modas)": float(len(modas)),
            "media (comparación)": float(datos.mean()),
            "mediana (comparación)": float(np.median(datos))}


def _ecuaciones_calibradas(p):
    f = _frecuencias(p["extra"])
    modas = _moda(f)
    return [f"\\text{{moda}} = \\arg\\max_v \\ \\mathrm{{frecuencia}}(v) = {{{', '.join(map(str, modas))}}}",
            f"\\text{{sirve para datos nominales; puede no ser única (bimodal) o no existir}}"]


_P0 = {"extra": 0}


def _v_es_el_mas_frecuente():
    f = _frecuencias(0)
    modas = _moda(f)
    return modas == [5] and f[4] == f.max(), \
        (f"la moda es el valor MÁS FRECUENTE (5, con {int(f.max())} apariciones): el pico de la distribución — "
         "argmax de las frecuencias, no un promedio ni una posición")


def _v_sirve_nominal():
    return True, \
        ("la moda es la ÚNICA medida de centro para datos CUALITATIVOS/nominales (color, marca, partido): "
         "no se puede promediar ni ordenar categorías (e05), pero sí contar cuál es la más común")


def _v_bimodal():
    # al igualar la frecuencia del retador (3) con la de la moda (5), hay dos modas
    extra = _BASE[4] - _BASE[_RETADOR - 1]           # cuánto falta para empatar en el pico
    modas = _moda(_frecuencias(extra))
    return len(modas) == 2 and set(modas) == {3, 5}, \
        (f"al empatar las frecuencias aparecen DOS modas ({', '.join(map(str, modas))}): la moda puede no ser "
         "única (bimodal, multimodal) — señal de que hay dos grupos mezclados en los datos")


def _v_difiere_de_media():
    f = _frecuencias(0)
    datos = np.repeat(_VALORES, f)
    moda = _moda(f)[0]
    return abs(moda - datos.mean()) > 0.3, \
        (f"la moda ({moda}) difiere de la media ({datos.mean():.1f}) y la mediana ({np.median(datos):.1f}): en "
         "distribuciones asimétricas las tres medidas de centro se separan — cada una cuenta algo distinto")


MODELO = Modelo(
    id="e19", nivel=2,
    nombre="La moda",
    xlabel="valor", ylabel="frecuencia",
    parametros=[
        Parametro("extra", _P0["extra"], 0, 8, 1, f"Copias extra del valor {_RETADOR}",
                  grupo="descriptiva", definicion="sube la frecuencia del retador; al empatar el pico, la moda se vuelve bimodal"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuál es el valor 'típico' cuando ni siquiera se puede promediar — por ejemplo, el color o la marca más común?",
        variables=[("moda", "el valor (o categoría) más frecuente"),
                   ("frecuencia", "cuántas veces aparece cada valor"),
                   ("unimodal / bimodal", "uno o varios picos")],
        derivacion=["\\text{contar la frecuencia de cada valor: } \\mathrm{frec}(v)",
                    "\\text{moda} = \\arg\\max_v \\ \\mathrm{frec}(v) \\quad(\\text{el pico})",
                    "\\text{si dos valores empatan en el máximo} \\Rightarrow \\text{bimodal}"],
        contexto=("La moda es la medida de tendencia central más intuitiva —el "
                  "valor que más se repite— y, a la vez, la más subestimada. Su "
                  "virtud única aparece cuando los datos NO son numéricos: no tiene "
                  "sentido preguntar por el color 'promedio' de los autos de una "
                  "ciudad, ni por la religión 'mediana' de un país, pero sí por el "
                  "color o la religión MÁS COMÚN —y esa es la moda—. Es la única "
                  "medida de centro aplicable a datos cualitativos o nominales "
                  "(e05), donde promediar y ordenar carecen de significado. Para "
                  "datos numéricos, la moda es el pico de la distribución, y "
                  "conviene mirarla junto a la media y la mediana: en una "
                  "distribución simétrica las tres coinciden, pero en una sesgada se "
                  "separan (en un sesgo a la derecha, típico de ingresos, la moda "
                  "queda a la izquierda, luego la mediana, luego la media). La moda "
                  "tiene además dos peculiaridades que enseñan algo sobre los datos: "
                  "puede NO EXISTIR (si todos los valores son distintos, no hay "
                  "ninguno más frecuente) y puede NO SER ÚNICA (si dos o más valores "
                  "empatan en el máximo, la distribución es bi- o multi-modal). Y "
                  "esa multimodalidad no es un defecto: suele ser la pista de que en "
                  "los datos conviven DOS POBLACIONES distintas —dos grupos, dos "
                  "regímenes, dos procesos— que se están promediando por error. Un "
                  "histograma con dos jorobas (como la población de e02) grita "
                  "'aquí hay dos cosas mezcladas', y la media de todo no describe a "
                  "ninguna."),
        autores=("La moda como estadístico y el término: Karl Pearson (1895), quien "
                 "también nombró la mediana y la desviación estándar — mención "
                 "histórica. Conocimiento estadístico general."),
        supuestos=[
            "Para datos NOMINALES/ordinales la moda es la única medida de centro válida (no se promedia ni se ordena por distancia).",
            "Para datos CONTINUOS la moda depende del agrupamiento (ancho de los intervalos/bins): distintas particiones pueden dar picos distintos — es la menos estable.",
            "Se reporta junto a media y mediana: su relación revela la forma (simétrica ⇒ coinciden; sesgada ⇒ se separan; bimodal ⇒ dos grupos).",
        ],
        ecuaciones=[
            Ecuacion("\\mathrm{moda} = \\arg\\max_v \\ \\mathrm{frec}(v)", "el valor más frecuente",
                     "el valor con la mayor frecuencia: el pico de la distribución de frecuencias — no un "
                     "promedio ni una posición, sino un conteo."),
            Ecuacion("\\text{simétrica: moda} = \\text{mediana} = \\text{media}", "cuando coinciden",
                     "en una distribución simétrica y unimodal las tres medidas de centro caen en el mismo "
                     "punto; su separación mide y señala la asimetría (e30)."),
            Ecuacion("\\text{dos picos que empatan} \\Rightarrow \\text{bimodal}", "multimodalidad",
                     "si dos valores comparten la frecuencia máxima hay dos modas: pista de que los datos "
                     "mezclan dos poblaciones (dos grupos, dos procesos)."),
        ],
        intuicion=("La moda es la respuesta a '¿qué es lo más común?', y por eso es "
                   "la medida que la gente usa sin saberlo: 'el auto más vendido', "
                   "'la talla más pedida', 'la hora pico'. Su poder está en que no "
                   "necesita números: funciona con categorías puras, donde media y "
                   "mediana son mudas. Su debilidad es que ignora casi toda la "
                   "información —solo mira cuál gana en frecuencia, no las "
                   "magnitudes— y es inestable en datos continuos (cambia con el "
                   "ancho de los intervalos). Pero su lección más valiosa es la "
                   "multimodalidad: cuando ves dos picos, la naturaleza te está "
                   "avisando que promediar es un error. La estatura 'promedio' de "
                   "una población que mezcla hombres y mujeres cae en un valle donde "
                   "hay poca gente; la moda revela las dos jorobas. Por eso, antes "
                   "de resumir cualquier conjunto con UN número, conviene mirar su "
                   "histograma: si tiene un solo pico, la media basta; si tiene dos, "
                   "hay que separar los grupos (clustering, e186) antes de hablar de "
                   "'el promedio'."),
        equilibrio=("La moda es el argmax de la frecuencia: única si hay un pico "
                    "claro, múltiple si hay empates, inexistente si todo es "
                    "distinto. Coincide con media y mediana en distribuciones "
                    "simétricas unimodales; se separa de ellas con la asimetría."),
        limitaciones=[
            "Ignora las magnitudes: solo cuenta frecuencias, así que desperdicia información cuando los datos son numéricos (media y mediana la aprovechan).",
            "Inestable en datos continuos: depende del ancho de los intervalos; con pocos datos o bins mal elegidos el 'pico' es artefacto del agrupamiento.",
            "Puede no existir o no ser única: cómodo conceptualmente pero incómodo operativamente; no siempre da 'un número' para resumir.",
        ],
        evolucion=("Completa las tres medidas de tendencia central (media e17, "
                   "mediana e18, moda e19), cada una óptima en su terreno: media "
                   "para simétricas limpias, mediana para sesgadas/robustez, moda "
                   "para nominales y para detectar multimodalidad. Su relación con "
                   "media y mediana anticipa la ASIMETRÍA (e30). La multimodalidad "
                   "que revela motiva el clustering (e186) y recuerda la lección de "
                   "e02: no promediar poblaciones mezcladas."),
    ),
    escenarios=[
        Escenario("unimodal", "un solo pico (sin retador)",
                  {"extra": 0},
                  "sin reforzar al retador, hay una sola moda (5): distribución "
                  "unimodal, un único valor típico. Media, mediana y moda difieren "
                  "por la ligera asimetría.",
                  cadena=["frecuencias base", "un valor domina en frecuencia (5)",
                          "moda única = 5", "unimodal: un solo grupo"]),
        Escenario("bimodal", "empatar los picos (retador iguala a la moda)",
                  {"extra": 4},
                  "al reforzar el valor 3 hasta empatar con el 5, aparecen DOS "
                  "modas: la distribución se vuelve bimodal, señal de dos grupos "
                  "mezclados — donde la media caería en el valle, sin describir a "
                  "nadie.",
                  cadena=["subir la frecuencia del retador (3)", "empata el pico con la moda original (5)",
                          "aparecen dos modas (3 y 5)", "bimodal: dos poblaciones — no promediar"]),
    ],
    verificaciones=[
        Verificacion("la moda es el valor más frecuente (argmax)", _v_es_el_mas_frecuente),
        Verificacion("la moda sirve para datos nominales (media/mediana no)", _v_sirve_nominal),
        Verificacion("la moda puede ser múltiple (bimodal)", _v_bimodal),
        Verificacion("en datos sesgados difiere de media y mediana", _v_difiere_de_media),
    ],
    notas="La moda = valor más frecuente (argmax de la frecuencia). Única medida de centro para datos NOMINALES. Puede no existir o ser múltiple: la bimodalidad delata dos poblaciones mezcladas (no promediar). Con media (e17) y mediana (e18) completa la tendencia central.",
)
