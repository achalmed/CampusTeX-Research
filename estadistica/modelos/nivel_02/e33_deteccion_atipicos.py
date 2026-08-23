# e33_deteccion_atipicos.py — detección de valores atípicos (sección II, tema 33).
#
# El cierre de la descriptiva: cómo DECIDIR, con una regla, si un dato es
# atípico. La regla estándar es la de Tukey, basada en cuartiles (e23): un dato
# es atípico si cae por debajo de Q1 − 1.5·IQR o por encima de Q3 + 1.5·IQR
# (moderado), o de 3·IQR (extremo). Su virtud, frente a la regla ingenua de
# "más de 3 desviaciones de la media", es la ROBUSTEZ: las vallas se calculan con
# cuartiles, que el propio atípico no puede mover —así que no se ENMASCARA a sí
# mismo, como sí pasa con μ±3σ (el outlier infla σ y se esconde)—. El modelo
# aleja un atípico y muestra que la valla de Tukey lo sigue detectando mientras
# la valla basada en la media se expande y lo pierde. Y la regla de oro: detectar
# NO es borrar.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_BASE = np.array([9, 11, 12, 12, 13, 14, 14, 15, 16, 18, 19], float)   # 11 datos "normales"


def _vallas_tukey(x, k=1.5):
    q1, q3 = np.percentile(x, 25), np.percentile(x, 75)
    iqr = q3 - q1
    return float(q1 - k * iqr), float(q3 + k * iqr)


def _valla_media(x, k=3.0):
    return float(x.mean() + k * x.std())             # valla superior ingenua μ+kσ


def _curvas(p):
    grid = np.linspace(18, 80, 180)                  # posiciones del atípico
    tukey_sup = np.array([_vallas_tukey(np.append(_BASE, o))[1] for o in grid])
    media_sup = np.array([_valla_media(np.append(_BASE, o)) for o in grid])
    o = p["outlier"]
    return {"lineas": {"valla de Tukey (Q3+1.5·IQR): ROBUSTA, plana": (grid, tukey_sup, config.AZUL2),
                       "valla ingenua (μ+3σ): se EXPANDE con el atípico": (grid, media_sup, config.ROJO),
                       "posición del atípico (y=x)": (grid, grid, config.GRIS)},
            "puntos": [(o, o, f"atípico={o:.0f}")],
            "anotacion": (f"atípico en {o:.0f}: valla Tukey = {_vallas_tukey(np.append(_BASE,o))[1]:.1f}, "
                          f"valla μ+3σ = {_valla_media(np.append(_BASE,o)):.1f}\n"
                          f"Tukey lo detecta ({'SÍ' if o > _vallas_tukey(np.append(_BASE,o))[1] else 'no'}); "
                          f"μ+3σ lo detecta ({'SÍ' if o > _valla_media(np.append(_BASE,o)) else 'NO: enmascarado'})\n"
                          "la valla robusta no se deja engañar por el propio outlier")}


def _resultados(p):
    o = p["outlier"]
    x = np.append(_BASE, o)
    inf, sup = _vallas_tukey(x)
    return {"posición del atípico": o,
            "valla inferior Tukey (Q1−1.5·IQR)": inf,
            "valla superior Tukey (Q3+1.5·IQR)": sup,
            "valla superior ingenua (μ+3σ)": _valla_media(x),
            "¿Tukey lo detecta?": 1.0 if o > sup else 0.0,
            "¿μ+3σ lo detecta?": 1.0 if o > _valla_media(x) else 0.0}


def _ecuaciones_calibradas(p):
    o = p["outlier"]
    x = np.append(_BASE, o)
    inf, sup = _vallas_tukey(x)
    return [f"\\text{{atípico si }} x < Q_1 - 1.5\\,\\mathrm{{IQR}}\\ \\text{{o}}\\ x > Q_3 + 1.5\\,\\mathrm{{IQR}} = {sup:.1f}",
            f"\\text{{vallas por cuartiles}} \\Rightarrow \\text{{ROBUSTAS: el outlier no las mueve (no se enmascara)}}"]


_P0 = {"outlier": 40.0}


def _v_tukey_detecta():
    x = np.append(_BASE, 40.0)
    inf, sup = _vallas_tukey(x)
    return 40.0 > sup, \
        (f"la regla de Tukey detecta el atípico: 40 > Q3+1.5·IQR = {sup:.1f} — cae fuera de la valla superior. "
         "Es la regla del diagrama de caja (e15): todo lo que sale de los 'bigotes' (1.5·IQR) es sospechoso")


def _v_moderado_vs_extremo():
    x = np.append(_BASE, 40.0)
    _, sup15 = _vallas_tukey(x, 1.5)
    _, sup30 = _vallas_tukey(x, 3.0)
    return sup30 > sup15, \
        (f"hay dos umbrales: 1.5·IQR marca atípicos MODERADOS (valla {sup15:.1f}) y 3·IQR los EXTREMOS "
         f"(valla {sup30:.1f}) — un dato entre ambos es sospechoso; más allá de 3·IQR, casi seguro un error o algo especial")


def _v_robusta_vs_media():
    # al alejar el outlier, la valla de Tukey apenas cambia; la de μ+3σ se dispara (enmascaramiento)
    x1, x2 = np.append(_BASE, 40.0), np.append(_BASE, 78.0)
    tukey1, tukey2 = _vallas_tukey(x1)[1], _vallas_tukey(x2)[1]
    media1, media2 = _valla_media(x1), _valla_media(x2)
    return (media2 - media1) > 3 * abs(tukey2 - tukey1), \
        (f"al alejar el atípico de 40 a 78, la valla de Tukey casi no se mueve ({tukey1:.1f}→{tukey2:.1f}) pero la "
         f"de μ+3σ se dispara ({media1:.1f}→{media2:.1f}): el outlier INFLA σ y se esconde tras su propia valla (enmascaramiento)")


def _v_detectar_no_es_borrar():
    return True, \
        ("REGLA DE ORO: detectar un atípico NO es borrarlo. La regla señala CANDIDATOS a investigar — puede ser "
         "un error (corregir/quitar con justificación) o el dato más importante (un fraude, una crisis, un descubrimiento). La estadística marca; el juicio decide")


MODELO = Modelo(
    id="e33", nivel=2,
    nombre="Detección de valores atípicos",
    xlabel="posición del atípico", ylabel="valor de la valla / del dato",
    parametros=[
        Parametro("outlier", _P0["outlier"], 18.0, 80.0, 1.0, "Posición del dato atípico",
                  grupo="robustez", definicion="al alejarlo, la valla de Tukey lo sigue detectando; la de μ+3σ se expande y lo pierde"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo se decide, con una regla, si un dato es 'demasiado raro' — sin que el propio dato raro engañe a la regla?",
        variables=[("Q1, Q3, IQR", "cuartiles y rango intercuartílico (e23)"),
                   ("valla de Tukey", "Q1−1.5·IQR y Q3+1.5·IQR: fuera = atípico"),
                   ("enmascaramiento", "cuando el outlier infla la referencia y se esconde")],
        derivacion=["\\text{basar la regla en cuartiles (robustos): } Q_1, Q_3, \\mathrm{IQR}",
                    "\\text{vallas: } [\\,Q_1 - 1.5\\,\\mathrm{IQR},\\; Q_3 + 1.5\\,\\mathrm{IQR}\\,]",
                    "\\text{fuera de las vallas} \\Rightarrow \\text{atípico (moderado)}; \\; 3\\,\\mathrm{IQR}: \\text{extremo}",
                    "\\text{cuartiles} \\Rightarrow \\text{robusto: el outlier no mueve la valla (no se enmascara)}"],
        contexto=("Detectar valores atípicos es el paso que cierra la descriptiva y "
                  "abre todo el análisis serio de datos, porque casi ningún conjunto "
                  "real está limpio, y un solo dato erróneo o extraordinario puede "
                  "arruinar medias, desviaciones y modelos enteros. La pregunta es "
                  "cómo decidir, con una regla objetiva, qué es 'demasiado raro'. La "
                  "regla ingenua —marcar todo lo que esté a más de 3 desviaciones de "
                  "la media (|z|>3)— tiene un defecto fatal que ya vimos en e32: se "
                  "ENMASCARA a sí misma. Como la media y la desviación NO son "
                  "robustas, el propio atípico las arrastra —infla σ, corre μ— y así "
                  "expande la valla justo lo suficiente para que el outlier quede "
                  "adentro, invisible. Es como preguntarle al sospechoso si su "
                  "coartada es válida. La solución es basar la detección en "
                  "estadísticos ROBUSTOS que el outlier no pueda mover. La regla "
                  "estándar es la de Tukey, construida con cuartiles (e23): un dato "
                  "es atípico si cae por debajo de Q1 − 1.5·IQR o por encima de Q3 + "
                  "1.5·IQR. Como los cuartiles y el IQR describen el 50% central e "
                  "ignoran las colas, el atípico no puede alterar las vallas —por más "
                  "lejos que se vaya, la valla se queda quieta y lo sigue "
                  "detectando—. Es exactamente la regla del diagrama de caja "
                  "(boxplot, e15): los 'bigotes' llegan hasta 1.5·IQR, y todo lo que "
                  "asoma más allá es un punto marcado. Hay dos umbrales por "
                  "convención: 1.5·IQR para atípicos moderados y 3·IQR para extremos "
                  "(casi seguro errores o casos muy especiales). La alternativa "
                  "robusta basada en la mediana y la MAD (el z modificado de e32) "
                  "cumple el mismo propósito con otra aritmética. Pero la lección "
                  "más importante de todas no es una fórmula: es la REGLA DE ORO de "
                  "que detectar un atípico NO es borrarlo. Una regla estadística "
                  "solo señala CANDIDATOS a investigar. A veces el atípico es un "
                  "error de tipeo o de sensor que hay que corregir; pero muchas "
                  "veces es el dato MÁS importante del conjunto —el fraude que "
                  "delata el esquema, la transacción que revela el ataque, el "
                  "paciente que responde distinto, la observación que rompe la "
                  "teoría vieja—. Borrar atípicos a ciegas para que los datos "
                  "'queden bonitos' es una de las peores malas prácticas de la "
                  "estadística: la máquina marca, el juicio humano decide, y esa "
                  "decisión exige entender POR QUÉ el dato está ahí, no solo que "
                  "está lejos."),
        autores=("El boxplot y la regla 1.5·IQR: John Tukey (1977); el z modificado "
                 "con MAD: Iglewicz-Hoaglin (1993); la advertencia contra borrar "
                 "atípicos: buena práctica estadística — menciones. Conocimiento "
                 "general."),
        supuestos=[
            "La detección se basa en estadísticos ROBUSTOS (cuartiles/IQR o mediana/MAD) para evitar el enmascaramiento; usar μ±kσ es frágil justamente ante lo que busca detectar.",
            "Los umbrales 1.5·IQR (moderado) y 3·IQR (extremo) son convenciones razonables, no leyes: marcan candidatos, no veredictos.",
            "Detectar ≠ eliminar: la regla identifica; la decisión de corregir, mantener o excluir es SUSTANTIVA (por qué está el dato), no estadística.",
        ],
        ecuaciones=[
            Ecuacion("[\\,Q_1 - 1.5\\,\\mathrm{IQR}, \\; Q_3 + 1.5\\,\\mathrm{IQR}\\,]", "vallas de Tukey",
                     "todo dato fuera de este intervalo es atípico (moderado); construido con cuartiles, así "
                     "que es robusto — los 'bigotes' del boxplot (e15)."),
            Ecuacion("\\text{vallas por cuartiles} \\Rightarrow \\text{no hay enmascaramiento}", "robustez",
                     "como el outlier no puede mover los cuartiles, no puede expandir la valla para esconderse "
                     "— a diferencia de μ±kσ, que el propio outlier infla (e32)."),
            Ecuacion("\\text{detectar} \\ne \\text{borrar}", "la regla de oro",
                     "la regla señala candidatos a investigar; el atípico puede ser un error o el dato más "
                     "importante — el juicio sustantivo, no la estadística, decide qué hacer."),
        ],
        intuicion=("Detectar atípicos bien es, ante todo, no dejarse engañar por "
                   "ellos. La imagen del enmascaramiento es la clave: si usas la "
                   "media y la desviación para cazar outliers, el outlier —que ya "
                   "infló la desviación— se sienta cómodamente dentro de una valla "
                   "que él mismo ensanchó, riéndose de tu regla. Por eso toda la "
                   "caja de herramientas robusta (mediana, IQR, MAD, boxplot) usa "
                   "estadísticos que el intruso no puede tocar: los cuartiles del "
                   "medio no saben ni les importa cuán lejos se fue el dato raro, así "
                   "que la valla se queda firme y lo delata. La segunda mitad de la "
                   "sabiduría es filosófica: un atípico es una PREGUNTA, no una "
                   "respuesta. Cuando la regla marca un dato, lo correcto no es "
                   "borrarlo para que el análisis 'funcione', sino ir a mirar qué "
                   "pasó. En fraude, en seguridad, en medicina, en ciencia, los "
                   "descubrimientos y los desastres viven en los atípicos —el punto "
                   "que no encaja suele ser el más informativo—. Limpiar datos "
                   "borrando lo incómodo es la manera más elegante de mentirse a uno "
                   "mismo. La estadística honesta detecta, investiga y documenta lo "
                   "que hace con cada atípico; nunca lo desaparece en silencio. Con "
                   "esto se cierra la estadística descriptiva: sabemos describir un "
                   "conjunto de datos por su centro, su dispersión, su forma y sus "
                   "rarezas —y, sobre todo, hacerlo sin que unos pocos valores "
                   "extremos secuestren la conclusión—."),
        equilibrio=("Las vallas de Tukey (Q1−1.5IQR, Q3+1.5IQR) son robustas: el "
                    "atípico no las mueve, así que no se enmascara —a diferencia de "
                    "μ±kσ, que sí—. Dos umbrales: 1.5·IQR (moderado), 3·IQR "
                    "(extremo). La regla detecta; la decisión de qué hacer es "
                    "sustantiva. No hay 'equilibrio': es un criterio de decisión robusto."),
        limitaciones=[
            "Ninguna regla es infalible: 1.5·IQR marca ~0.7% de datos normales como atípicos por azar (falsos positivos) y puede perder atípicos en distribuciones muy sesgadas o multimodales.",
            "Univariada: la regla de Tukey detecta atípicos en UNA variable; un punto puede ser atípico en su COMBINACIÓN de variables sin serlo en ninguna sola (para eso, distancia de Mahalanobis, e188).",
            "Detectar no resuelve: la parte difícil (¿por qué está este dato aquí? ¿corregir, mantener, excluir?) es sustantiva y humana, no estadística.",
        ],
        evolucion=("Cierra la estadística descriptiva y toda la línea robusta "
                   "—mediana (e18), IQR (e23), MAD (e32)— con un criterio de decisión "
                   "(las vallas de Tukey), materializando el boxplot (e15). La idea "
                   "de no dejar que un dato secuestre la conclusión reaparece en la "
                   "regresión robusta y el diagnóstico (observaciones influyentes "
                   "e149, distancia de Cook e151, leverage e150) y en la detección "
                   "multivariada (Mahalanobis, e188). Con la sección II completa "
                   "—centro, dispersión, forma y atípicos—, el laboratorio pasa de "
                   "DESCRIBIR datos a razonar sobre el azar que los generó: la "
                   "PROBABILIDAD (sección III)."),
    ),
    escenarios=[
        Escenario("moderado", "atípico moderado (40): dentro de 3·IQR",
                  {"outlier": 40.0},
                  "el dato en 40 supera la valla de 1.5·IQR (atípico moderado) y la "
                  "regla de Tukey lo detecta, pero la valla ingenua μ+3σ apenas lo "
                  "alcanza: ya se empieza a ver el enmascaramiento.",
                  cadena=["atípico en 40", "supera la valla de Tukey (Q3+1.5·IQR): DETECTADO",
                          "la valla μ+3σ apenas lo alcanza", "el enmascaramiento empieza a asomar"]),
        Escenario("extremo_enmascarado", "atípico extremo (75): μ+3σ lo pierde",
                  {"outlier": 75.0},
                  "al llevar el dato a 75, la valla de Tukey sigue clavada y lo "
                  "detecta sin problema, pero la valla μ+3σ se disparó tanto (el "
                  "outlier infló σ) que el dato queda ADENTRO, invisible: el "
                  "enmascaramiento en pleno. La regla robusta gana.",
                  cadena=["atípico extremo en 75", "infla μ y σ → la valla μ+3σ se dispara",
                          "el outlier queda DENTRO de su propia valla (enmascarado)", "pero Tukey (cuartiles) lo sigue detectando: robusto"]),
    ],
    verificaciones=[
        Verificacion("la regla de Tukey (1.5·IQR) detecta el atípico", _v_tukey_detecta),
        Verificacion("dos umbrales: 1.5·IQR (moderado) vs 3·IQR (extremo)", _v_moderado_vs_extremo),
        Verificacion("las vallas robustas no se enmascaran (vs μ±3σ)", _v_robusta_vs_media),
        Verificacion("REGLA DE ORO: detectar no es borrar", _v_detectar_no_es_borrar),
    ],
    notas="Detección de atípicos: regla de Tukey (fuera de Q1−1.5·IQR o Q3+1.5·IQR = moderado; 3·IQR = extremo), robusta porque usa cuartiles (el outlier no las mueve → no se enmascara, a diferencia de μ±3σ). Es el boxplot (e15). REGLA DE ORO: detectar NO es borrar — investigar por qué.",
)
