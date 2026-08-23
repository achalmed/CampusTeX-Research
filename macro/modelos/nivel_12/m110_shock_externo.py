# m110_shock_externo.py — el shock externo sobre el Perú (síntesis, nivel 12).
#
# Integra el bloque externo (m103-m105, m109) en un solo termómetro: un ÍNDICE DE
# CONDICIONES EXTERNAS que promedia las variaciones estandarizadas del precio del
# cobre (m103), los términos de intercambio (m105) y las exportaciones (m109). La
# tesis de m86-m89 —el ciclo peruano lo marca el mundo— se vuelve medible: el
# índice correlaciona +0.58 con el crecimiento. Los años de mejores condiciones
# externas (2006, 2010, 2021) fueron los de mayor crecimiento; los de peores
# (2009 la crisis global, 2015 el fin del superciclo del cobre) los de freno. Es
# el canal REAL/comercial del exterior (el financiero —FED, capitales— es m111).
# Pero el modelo es honesto sobre su límite: explica MUCHO, no todo. 2020 es la
# excepción reveladora —el peor año de crecimiento (−10.9%) NO fue un shock
# externo comercial (el cobre y los términos de intercambio hasta subieron) sino
# un shock DOMÉSTICO de oferta (el confinamiento)—: no todo lo malo viene de afuera.
#
# Procedencia: datos BCRP PN01652XM (cobre), PN38923BM (términos de intercambio),
# PM04933AA (exportaciones) y PN01728AM (PBI), muestra 2004-2024. El índice es
# una síntesis del laboratorio (promedio de variaciones estandarizadas), no un
# indicador oficial del BCRP. Los canales: m86-m89 (conocimiento general).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _z(v):
    v = np.asarray(v, float)
    return (v - v.mean()) / v.std() if v.std() > 0 else v * 0.0


def _series():
    anos, cobre, pbi = _datos_bcrp.alinear("cobre", "pbi_var")
    _, _, tdi = _datos_bcrp.alinear("cobre", "terminos_intercambio")
    _, _, xpo = _datos_bcrp.alinear("cobre", "exportaciones")
    dc = np.diff(cobre) / cobre[:-1] * 100
    dt = np.diff(tdi) / tdi[:-1] * 100
    dx = np.diff(xpo) / xpo[:-1] * 100
    ax = anos[1:]
    idx = (_z(dc) + _z(dt) + _z(dx)) / 3                 # índice de condiciones externas
    g = pbi[1:]
    return ax, idx, g


def _idx_foco(ax, p):
    a = int(p["anio_foco"])
    return int(list(ax).index(a)) if a in ax else len(ax) - 1


def _curvas(p):
    ax, idx, g = _series()
    gz = _z(g)
    i = _idx_foco(ax, p)
    return {"lineas": {"condiciones externas (índice, estandarizado)": (ax, idx, config.DORADO),
                       "crecimiento del PBI (estandarizado)": (ax, gz, config.AZUL2)},
            "puntos": [(2009.0, float(idx[ax == 2009][0]), "2009: shock externo (crisis global)"),
                       (2020.0, float(idx[ax == 2020][0]), "2020: volumen ↓ (parte doméstica)")],
            "anotacion": (f"índice externo (cobre+TdI+exportaciones) vs PBI\n"
                          f"corr $= {_datos_bcrp.correlacion(idx, g):+.2f}$ ($R^2\\approx{_datos_bcrp.correlacion(idx, g)**2:.2f}$): el mundo marca gran parte del ciclo (m86-m89)\n"
                          "pero ~2/3 es doméstico: 2020 precio↑ / volumen↓ (minas cerradas)")}


def _resultados(p):
    ax, idx, g = _series()
    i = _idx_foco(ax, p)
    order = np.argsort(idx)
    return {"corr(índice externo, crecimiento)": float(_datos_bcrp.correlacion(idx, g)),
            "peor año de condiciones externas": float(ax[order[0]]),
            "crecimiento ese año (%)": float(g[order[0]]),
            "mejor año de condiciones externas": float(ax[order[-1]]),
            "crecimiento ese año (%)": float(g[order[-1]]),
            f"índice externo {int(ax[i])}": float(idx[i]),
            f"crecimiento {int(ax[i])} (%)": float(g[i])}


def _ecuaciones_calibradas(p):
    ax, idx, g = _series()
    return [f"índice externo $= \\frac{{1}}{{3}}(z_{{cobre}} + z_{{TdI}} + z_{{export}})$ (síntesis m103/m105/m109)",
            f"corr(índice, crecimiento) $= {_datos_bcrp.correlacion(idx, g):+.2f}$: el ciclo peruano es, en gran parte, externo (m86-m89)"]


_P0 = {"anio_foco": 2009.0}


def _v_indice_correlaciona():
    ax, idx, g = _series()
    c = _datos_bcrp.correlacion(idx, g)
    return c > 0.45, \
        (f"el índice de condiciones externas correlaciona {c:+.2f} con el crecimiento: el ciclo peruano "
         "está marcado, en gran parte, por el mundo (m86-m89) — cobre, términos de intercambio y exportaciones juntos")


def _v_shock_2009():
    ax, idx, g = _series()
    return float(idx[ax == 2009][0]) < -0.5, \
        (f"2009 fue un shock externo puro (índice {float(idx[ax == 2009][0]):+.2f}): la crisis global hundió el cobre "
         "y las exportaciones, y el crecimiento cayó de 9% a 1% — la transmisión de m86-m89 en acción")


def _v_boom_externo():
    ax, idx, g = _series()
    order = np.argsort(idx)
    mejores = ax[order[-3:]]
    g_mejores = g[order[-3:]].mean()
    return g_mejores > 8, \
        (f"los años de mejores condiciones externas ({', '.join(str(int(a)) for a in sorted(mejores))}) "
         f"crecieron {g_mejores:.1f}% en promedio: el superciclo fue, en el fondo, un viento de cola externo (m88)")


def _v_no_todo_externo():
    # 2020: el PRECIO externo (términos de intercambio) subió pero el VOLUMEN exportado cayó por el confinamiento
    anos, tdi = _datos_bcrp.serie("terminos_intercambio", anual=True)
    _, xpo = _datos_bcrp.serie("exportaciones", anual=True)
    i19, i20 = list(anos).index(2019), list(anos).index(2020)
    return tdi[i20] > tdi[i19] and xpo[i20] < xpo[i19], \
        ("2020 es la excepción honesta: el PRECIO externo (términos de intercambio) SUBIÓ pero el VOLUMEN exportado "
         "CAYÓ porque el confinamiento cerró las minas — parte del 'shock externo' de 2020 fue en realidad DOMÉSTICO (oferta): no todo lo malo viene de afuera")


MODELO = Modelo(
    id="m110", nivel=12,
    nombre="Shock externo sobre el Perú (síntesis BCRP)",
    xlabel="Año", ylabel="Estandarizado (media 0)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2005, 2024, 1, "Año a destacar (condiciones externas)",
                  grupo="análisis", definicion="año a inspeccionar; 2009 shock externo, 2020 shock doméstico"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto del ciclo económico peruano viene de afuera — y todo lo malo es culpa del mundo?",
        variables=[("índice externo", "promedio estandarizado de Δcobre, Δtérminos de intercambio, Δexportaciones"),
                   ("g_t", "crecimiento del PBI (BCRP PN01728AM)"),
                   ("2009 vs 2020", "shock externo (crisis global) vs shock doméstico (COVID)")],
        derivacion=["índice_t = \\tfrac{1}{3}(z_{\\Delta cobre} + z_{\\Delta TdI} + z_{\\Delta export})",
                    "corr(índice, g) \\approx +0.58, \\;R^2 \\approx 0.34 \\;(el\\;mundo\\;marca\\;gran\\;parte, m86\\text{-}89)",
                    "\\sim 2/3\\;es\\;doméstico; \\;2020: \\;TdI\\uparrow\\;pero\\;volumen\\downarrow \\;(minas\\;cerradas)"],
        contexto=("Este modelo integra todo el bloque externo del laboratorio "
                  "—el cobre (m103), los términos de intercambio (m105) y las "
                  "exportaciones (m109)— en un solo termómetro: un índice de "
                  "condiciones externas que promedia las variaciones estandarizadas "
                  "de las tres. La idea es convertir en algo medible la tesis de "
                  "m86-m89: que el ciclo de una economía pequeña, abierta y "
                  "dependiente de commodities como la peruana lo marca, en buena "
                  "parte, el mundo. Y los datos la confirman: el índice de "
                  "condiciones externas correlaciona +0.58 con el crecimiento. Los "
                  "años de mejores condiciones externas —2006, 2010, 2021, con el "
                  "cobre y las exportaciones al alza— fueron los de mayor "
                  "crecimiento; los de peores —2009, cuando la crisis financiera "
                  "global hundió el cobre y las exportaciones, y 2015, el fin del "
                  "superciclo— fueron los de freno. El superciclo entero puede "
                  "leerse como un largo viento de cola externo (m88), y su "
                  "reversión (m89) como el fin de esa suerte. Este es el canal REAL "
                  "o comercial del exterior; el canal FINANCIERO —la Fed, los flujos "
                  "de capital— es m111, y juntos completan la dimensión externa. "
                  "Pero el modelo incluye, deliberadamente, su propia advertencia. "
                  "El índice explica mucho, no todo (su R² es solo ~0.34: dos "
                  "tercios del ciclo son domésticos), y 2020 es la excepción que lo "
                  "prueba: fue el PEOR año de crecimiento de la serie (−10.9%), y su "
                  "índice externo aparece bajo solo porque las EXPORTACIONES "
                  "cayeron —pero el PRECIO externo, los términos de intercambio, "
                  "SUBIÓ, empujado por el oro refugio (m105)—. El volumen exportado "
                  "se hundió no porque el mundo dejara de comprar, sino porque el "
                  "confinamiento cerró las minas peruanas: un shock DOMÉSTICO "
                  "de oferta disfrazado de externo, no un shock externo de demanda. "
                  "La lección es doble: el Perú está "
                  "profundamente expuesto al ciclo mundial (y debe protegerse de él, "
                  "m66, m112), pero atribuir todo lo malo al exterior es un error —a "
                  "veces el shock es propio, y confundirlos lleva a políticas "
                  "equivocadas."),
        autores=("Datos: BCRP (PN01652XM cobre, PN38923BM términos de intercambio, "
                 "PM04933AA exportaciones, PN01728AM PBI); los canales de "
                 "transmisión externa: m86-m89; el índice compuesto es una síntesis "
                 "del laboratorio (conocimiento general), no un indicador oficial."),
        supuestos=[
            "El índice de condiciones externas es una SÍNTESIS del laboratorio (promedio de tres variaciones estandarizadas): ilustrativo, no un indicador oficial del BCRP.",
            "El cobre y los términos de intercambio están muy correlacionados (m105), así que el índice pesa fuerte hacia el canal minero: refleja la estructura real de la economía peruana, no un sesgo.",
            "Correlación descriptiva (+0.58): mide co-movimiento del canal externo con el ciclo, no un efecto causal aislado (aunque el exterior es largamente exógeno, m109).",
        ],
        ecuaciones=[
            Ecuacion("índice_t = \\tfrac{1}{3}(z_{\\Delta cobre} + z_{\\Delta TdI} + z_{\\Delta export})", "el termómetro externo",
                     "un solo número que resume las condiciones externas del Perú, sintetizando m103, "
                     "m105 y m109 — el canal comercial del mundo hacia el Perú."),
            Ecuacion("corr(índice, \\; g) \\approx +0.58", "el mundo marca el ciclo (m86-m89)",
                     "más de la mitad del pulso del crecimiento peruano se mueve con las condiciones "
                     "externas: el superciclo fue viento de cola (m88), su fin fue el freno (m89)."),
            Ecuacion("2020: \\;TdI\\uparrow \\;pero\\;exportaciones\\downarrow \\;\\Rightarrow\\; parte\\;doméstica", "no todo viene de afuera",
                     "en 2020 el precio externo (términos de intercambio) subió, pero el volumen exportado "
                     "cayó porque el confinamiento cerró las minas — parte del shock fue interno, no del mundo."),
        ],
        intuicion=("La imagen es la de dos líneas que bailan casi juntas: cuando las "
                   "condiciones externas suben, el Perú crece; cuando caen, se "
                   "frena. Es el retrato de una economía profundamente abierta y "
                   "dependiente de sus materias primas, cuyo destino de corto plazo "
                   "se decide en buena medida en Shanghái y Chicago, no en Lima. "
                   "Entender esto es entender por qué el Perú necesita colchones "
                   "—el fondo de estabilización (m66, m108), reservas, "
                   "diversificación (m112)—: para no quedar a merced de un ciclo que "
                   "no controla. Pero la segunda línea de la lección es igual de "
                   "importante y más difícil de aceptar políticamente: no todo lo "
                   "malo viene de afuera. 2020 lo grita —el peor año en dos décadas, "
                   "y los PRECIOS externos estaban altos (el volumen cayó porque se "
                   "cerraron las minas, no porque el mundo dejara de comprar)—; fue "
                   "un shock doméstico. Un gobierno "
                   "que atribuye cada recesión al mundo evita mirar sus propios "
                   "errores (una mala política, una crisis institucional, un shock "
                   "de oferta interno). El índice externo, con su +0.58 (un R² de "
                   "solo ~0.34), dice exactamente eso: el mundo explica cerca de un "
                   "tercio del ciclo, y deja dos tercios a lo doméstico. Saber cuál "
                   "shock es cuál —externo o propio— es la "
                   "diferencia entre la política correcta y el chivo expiatorio."),
        equilibrio=("No hay equilibrio que resolver: es la síntesis empírica del "
                    "canal externo. El índice de condiciones externas correlaciona "
                    "+0.58 con el crecimiento (el mundo marca gran parte del ciclo, "
                    "m86-m89), con 2020 como excepción doméstica que acota la tesis."),
        limitaciones=[
            "Índice ad hoc: promedio simple de tres variables estandarizadas; ponderaciones distintas darían un índice algo distinto (aunque la conclusión —fuerte peso externo— es robusta).",
            "Solo el canal comercial: el índice omite el canal financiero (Fed, flujos de capital, m111), que es la otra mitad de la dimensión externa — juntos explicarían más.",
            "Correlación, no causalidad aislada: aunque el exterior es largamente exógeno (m109), el índice co-mueve con factores internos (inversión) que también responden al ciclo global.",
        ],
        evolucion=("Sintetiza el canal externo REAL (m103-m105, m109) en un "
                   "termómetro y acota su alcance con 2020 (shock doméstico). Su "
                   "complemento es m111, el canal FINANCIERO externo (Fed → flujos "
                   "de capital → tipo de cambio), que explica episodios como 2021 "
                   "(m104) que el canal comercial no capta. Juntos motivan m112 "
                   "(diversificar para depender menos del mundo) y toda la lógica de "
                   "colchones fiscales (m66, m108)."),
    ),
    escenarios=[
        Escenario("shock_2009", "shock externo puro (crisis global 2009)",
                  {"anio_foco": 2009.0},
                  "2009: la crisis financiera global hunde el cobre y las "
                  "exportaciones; el índice externo se desploma y el crecimiento cae "
                  "de 9% a 1%. El shock externo de manual (m86-m89) — el mundo se "
                  "frena y el Perú con él.",
                  cadena=["crisis financiera global (2009)", "cobre −26%, exportaciones caen (m88→m89)",
                          "el índice de condiciones externas se desploma", "el crecimiento cae de 9% a 1%",
                          "shock externo puro: el mundo marca el ciclo"]),
        Escenario("boom_externo", "viento de cola (superciclo)",
                  {"anio_foco": 2010.0},
                  "2010 (y 2006, 2021): condiciones externas inmejorables —cobre y "
                  "exportaciones disparados— y crecimiento de 8-16%. El superciclo "
                  "leído como lo que fue: un largo viento de cola externo (m88).",
                  cadena=["demanda mundial fuerte (China, m88)", "cobre, términos de intercambio y exportaciones al alza",
                          "el índice externo en máximos", "el Perú crece 8-16% — el superciclo como suerte externa"]),
        Escenario("domestico_2020", "shock DOMÉSTICO (COVID 2020)",
                  {"anio_foco": 2020.0},
                  "2020: el peor año de crecimiento (−10.9%). El índice externo baja "
                  "solo porque el VOLUMEN exportado cayó, pero el PRECIO externo "
                  "(términos de intercambio) SUBIÓ: las minas cerraron por el "
                  "confinamiento, no porque el mundo dejara de comprar — un shock de "
                  "oferta interno disfrazado de externo. No todo lo malo viene de afuera.",
                  cadena=["2020: peor crecimiento de la serie (−10.9%)", "precio externo (términos de intercambio) SUBE (oro refugio, m105)",
                          "pero el volumen exportado cae: las minas cerraron (confinamiento)", "el shock fue DOMÉSTICO (oferta), no del mundo",
                          "no todo lo malo viene de afuera — honestidad analítica"]),
    ],
    verificaciones=[
        Verificacion("el ciclo peruano es en gran parte externo (m86-m89)", _v_indice_correlaciona),
        Verificacion("2009: shock externo puro (crisis global)", _v_shock_2009),
        Verificacion("el superciclo fue viento de cola externo (m88)", _v_boom_externo),
        Verificacion("pero no todo es externo: 2020 fue doméstico", _v_no_todo_externo),
    ],
    notas="Índice de condiciones externas (cobre+TdI+exportaciones) corr +0.58 con el crecimiento: el mundo marca gran parte del ciclo (m86-m89). Pero 2020 (peor año) fue DOMÉSTICO — no todo lo malo viene de afuera. Canal financiero = m111.",
)
