# m103_cobre_crecimiento.py — el precio del cobre y el crecimiento (nivel 12).
#
# El canal de TÉRMINOS DE INTERCAMBIO (m88/m89) con datos peruanos: el cobre es
# el principal producto de exportación del Perú, y su precio (BCRP PN01652XM,
# ¢US$/lb) es el pulso del superciclo de commodities. El laboratorio cuantifica
# cuánto del crecimiento peruano se mueve con el cobre — y enseña una sutileza
# econométrica: es el CAMBIO del precio (no su nivel) lo que impulsa el
# crecimiento. Post-2014 el cobre estuvo ALTO (321¢ de media, más que en el
# superciclo) pero el crecimiento fue BAJO (2.7%), porque el precio había dejado
# de SUBIR — la ganancia de términos de intercambio (m89) es un flujo, no un
# nivel. Y el R² ~0.20 recuerda que el cobre explica ~1/5 del crecimiento: real,
# pero no destino (diversificar es m112).
#
# Procedencia: datos BCRP PN01652XM (cobre LME) y PN01728AM (PBI var%), muestra
# 2004-2024. La correlación es descriptiva; NO es una estimación causal (regla
# del pipeline: nunca causalidad automática). El canal terms-of-trade: m89.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, cobre, pbi = _datos_bcrp.alinear("cobre", "pbi_var")
    dcobre = np.diff(cobre) / cobre[:-1] * 100     # var% del precio del cobre
    return anos, cobre, pbi, dcobre


def _corr(p):
    """Correlación cobre→crecimiento según el rezago elegido."""
    anos, cobre, pbi, dcobre = _series()
    g = pbi[1:]                                     # crecimiento contemporáneo al Δcobre
    k = int(p["rezago"])
    if k == 0:
        return _datos_bcrp.correlacion(dcobre, g)
    return _datos_bcrp.correlacion(dcobre[:-k], g[k:])


def _curvas(p):
    anos, cobre, pbi, dcobre = _series()
    ax = anos[1:]
    corr = _corr(p)
    r2 = _datos_bcrp.correlacion(dcobre, pbi[1:]) ** 2
    return {"lineas": {"variación del precio del cobre (BCRP, %)": (ax, dcobre, config.DORADO),
                       "crecimiento del PBI (BCRP, %)": (ax, pbi[1:], config.AZUL2)},
            "puntos": [(2009.0, float(dcobre[ax == 2009][0]), "2009: crisis global"),
                       (2021.0, float(dcobre[ax == 2021][0]), "2021: rebote")],
            "anotacion": (f"cobre (PN01652XM) vs PBI (PN01728AM), 2005-2024\n"
                          f"corr(Δcobre, crecimiento) = {corr:+.2f} "
                          f"(rezago {int(p['rezago'])} año)\n"
                          f"$R^2 \\approx {r2:.2f}$: el cobre explica ~{r2*100:.0f}% del crecimiento")}


def _resultados(p):
    anos, cobre, pbi, dcobre = _series()
    corr_cambio = _datos_bcrp.correlacion(dcobre, pbi[1:])
    corr_nivel = _datos_bcrp.correlacion(cobre, pbi)
    sc = (anos >= 2004) & (anos <= 2013)
    pb = anos >= 2014
    return {"corr(Δcobre, crecimiento)": float(corr_cambio),
            "corr(nivel del cobre, crecimiento)": float(corr_nivel),
            "R² del cobre sobre el crecimiento": float(corr_cambio ** 2),
            "cobre medio superciclo 2004-13 (¢/lb)": float(cobre[sc].mean()),
            "cobre medio post-2014 (¢/lb)": float(cobre[pb].mean()),
            "PBI medio superciclo 2004-13 (%)": float(pbi[sc].mean()),
            "PBI medio post-2014 (%)": float(pbi[pb].mean())}


def _ecuaciones_calibradas(p):
    anos, cobre, pbi, dcobre = _series()
    cc = _datos_bcrp.correlacion(dcobre, pbi[1:])
    cn = _datos_bcrp.correlacion(cobre, pbi)
    return [f"corr$(\\Delta cobre, g) = {cc:+.2f}$ > corr$(\\text{{nivel}}, g) = {cn:+.2f}$",
            f"es el CAMBIO del precio (flujo de términos de intercambio, m89), no el nivel"]


_P0 = {"rezago": 0.0}


def _v_correlacion_positiva():
    corr = _corr({"rezago": 0})
    return corr > 0.3, \
        (f"el cambio del precio del cobre y el crecimiento se mueven juntos (corr {corr:+.2f}): "
         "el canal de términos de intercambio (m89) — el cobre sube, el Perú crece")


def _v_cambio_mas_que_nivel():
    anos, cobre, pbi, dcobre = _series()
    cc = _datos_bcrp.correlacion(dcobre, pbi[1:])
    cn = _datos_bcrp.correlacion(cobre, pbi)
    return cc > cn, \
        (f"es el CAMBIO del precio, no el nivel: corr(Δcobre,g)={cc:+.2f} > corr(nivel,g)={cn:+.2f} — "
         "post-2014 el cobre estuvo ALTO pero el crecimiento BAJO porque había dejado de subir (m89)")


def _v_r2_parcial():
    anos, cobre, pbi, dcobre = _series()
    r2 = _datos_bcrp.correlacion(dcobre, pbi[1:]) ** 2
    return 0.1 < r2 < 0.35, \
        (f"el cobre explica ~{r2*100:.0f}% del crecimiento ($R^2={r2:.2f}$): real pero NO destino — "
         "los otros ~80% son inversión (m26), política (m107) y productividad (m90); diversificar es m112")


def _v_superciclo_mayor():
    anos, cobre, pbi, dcobre = _series()
    sc = float(pbi[(anos >= 2004) & (anos <= 2013)].mean())
    pb = float(pbi[anos >= 2014].mean())
    return sc > pb, \
        (f"el superciclo (cobre SUBIENDO) creció {sc:.1f}% > post-2014 (cobre alto pero PLANO) {pb:.1f}%: "
         "el boom fue del PRECIO en ascenso, no del nivel — la ganancia de términos de intercambio es un flujo (m89)")


MODELO = Modelo(
    id="m103", nivel=12,
    nombre="Precio del cobre → crecimiento (BCRP)",
    xlabel="Año", ylabel="Variación anual (%)",
    parametros=[
        Parametro("rezago", _P0["rezago"], 0, 2, 1, "Rezago cobre→crecimiento (años)",
                  grupo="análisis", definicion="¿el cobre impulsa el crecimiento el mismo año o con retraso?"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto del crecimiento peruano explica el precio del cobre — y es el nivel del precio o su cambio lo que importa?",
        variables=[("cobre_t", "precio del cobre, ¢US$/lb (BCRP PN01652XM)"),
                   ("Δcobre_t", "variación anual del precio — el flujo de términos de intercambio (m89)"),
                   ("g_t", "crecimiento del PBI (BCRP PN01728AM)")],
        derivacion=["dato: \\;cobre_t \\;(PN01652XM), \\;g_t \\;(PN01728AM)",
                    "corr(\\Delta cobre_t, g_t) \\approx +0.45 \\;>\\; corr(nivel_t, g_t) \\approx +0.23",
                    "es\\;el\\;CAMBIO\\;del\\;precio\\;(flujo\\;de\\;términos\\;de\\;intercambio, m89)"],
        contexto=("El cobre es el corazón exportador del Perú: alrededor de un "
                  "tercio de las exportaciones y el motor del superciclo de "
                  "commodities. Este modelo cuantifica, con datos del BCRP, el "
                  "canal de TÉRMINOS DE INTERCAMBIO que la teoría construyó en m88 "
                  "(auge de materias primas) y m89 (su reversión): cuando el precio "
                  "del cobre sube, el Perú recibe más dólares por lo mismo que "
                  "exporta, sube el ingreso nacional, la inversión minera, la "
                  "recaudación fiscal y la confianza — y el PBI crece. Los datos lo "
                  "confirman: la variación del precio del cobre y el crecimiento del "
                  "PBI se mueven juntos con correlación de +0.45. Pero el modelo "
                  "enseña una sutileza que separa el análisis de la superstición: es "
                  "el CAMBIO del precio, no su NIVEL, lo que impulsa el crecimiento. "
                  "Después de 2014 el cobre estuvo, en promedio, MÁS alto (321¢/lb) "
                  "que durante el superciclo (291¢/lb), y sin embargo el crecimiento "
                  "fue mucho menor (2.7% vs 6.4%). ¿Por qué? Porque en el superciclo "
                  "el precio SUBÍA sin parar (de 130 a 400¢), y esa subida es una "
                  "ganancia de términos de intercambio cada año (un flujo, m89); "
                  "después de 2014 el precio se estabilizó alto, y un nivel alto pero "
                  "plano ya no aporta ganancias nuevas. La correlación del nivel con "
                  "el crecimiento es apenas +0.23; la del cambio, +0.45. Y el R² de "
                  "~0.20 cierra con humildad: el cobre explica cerca de un quinto del "
                  "crecimiento peruano — enorme para una sola variable, pero deja "
                  "cuatro quintos a la inversión (m26), la política (m107) y la "
                  "productividad (m90). El cobre es importante, no es destino: por "
                  "eso el desafío de desarrollo es diversificar (m112)."),
        autores=("Datos: BCRP (PN01652XM cobre LME, PN01728AM PBI); el canal de "
                 "términos de intercambio: m88/m89 (conocimiento general); la "
                 "distinción nivel/cambio: econometría básica (series en niveles vs "
                 "diferencias) — la misma lección que m101."),
        supuestos=[
            "La correlación es DESCRIPTIVA: cuantifica co-movimiento, no un efecto causal aislado (que exigiría controlar inversión, política externa, etc.).",
            "El precio del cobre es tratado como EXÓGENO al Perú (precio mundial LME): el Perú es tomador de precio (m43), supuesto razonable pero no exacto (es un productor grande).",
            "Muestra anual 2004-2024: capta el superciclo y su reversión, no ciclos más largos.",
        ],
        ecuaciones=[
            Ecuacion("corr(\\Delta cobre_t, \\; g_t) \\approx +0.45", "el canal de términos de intercambio (m89)",
                     "la variación del precio del cobre y el crecimiento del PBI se mueven juntos: "
                     "cuando el cobre sube, el Perú crece — el mecanismo de m88/m89, verificado con datos."),
            Ecuacion("corr(\\Delta cobre, g) \\; > \\; corr(nivel, g)", "es el cambio, no el nivel",
                     "el nivel alto pero plano del cobre post-2014 coincidió con crecimiento bajo: "
                     "la ganancia de términos de intercambio es un FLUJO (el precio subiendo), no un stock."),
            Ecuacion("R^2 \\approx 0.20", "importante, no destino",
                     "el cobre explica ~1/5 del crecimiento: real y grande, pero los otros 4/5 son "
                     "inversión (m26), política (m107) y productividad (m90) — de ahí diversificar (m112)."),
        ],
        intuicion=("Ver la serie del cobre junto a la del crecimiento es ver el "
                   "modelo económico del Perú en dos líneas: el país sube cuando el "
                   "cobre sube y se frena cuando el cobre deja de subir. Es el canal "
                   "de términos de intercambio (m89) hecho evidencia. Pero la lección "
                   "fina — la que distingue a un economista de un titular de "
                   "periódico — es que importa el CAMBIO, no el nivel. Un país "
                   "exportador de commodities no crece porque el precio esté alto, "
                   "sino porque está SUBIENDO; cuando el precio se estabiliza (aun en "
                   "un nivel alto), la ganancia extraordinaria desaparece y el "
                   "crecimiento vuelve a su base estructural. Esto explica la "
                   "'decepción' post-2014: el cobre no colapsó, simplemente dejó de "
                   "subir, y eso bastó para que el crecimiento cayera a la mitad. Es "
                   "la misma trampa de niveles-vs-cambios que m101 mostró en el tipo "
                   "de cambio, y una advertencia general: en series económicas, "
                   "preguntar '¿está alto?' es casi siempre menos útil que preguntar "
                   "'¿está cambiando?'. Y el R² de 0.20 mantiene la humildad: el "
                   "cobre manda, pero no manda solo."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica entre "
                    "dos series observadas. El 'resultado' es que el cambio del cobre "
                    "correlaciona +0.45 con el crecimiento (más que el nivel, +0.23) "
                    "y explica ~20% de su varianza — cuantificación del canal de m89."),
        limitaciones=[
            "Correlación, no causalidad aislada: el cobre correlaciona con crecimiento, pero también con inversión, confianza y política — separar su efecto propio exige controles (regla del pipeline).",
            "Precio exógeno supuesto: el Perú es tomador de precio en el cobre (m43), pero es un productor grande; en rigor el precio no es 100% exógeno.",
            "R² sobre-atribuible: 0.20 mezcla el efecto del cobre con todo lo correlacionado con él (el ciclo global, m86) — es una cota superior del canal puro.",
        ],
        evolucion=("Cuantifica el canal real del cobre (m89) que m97 identificó "
                   "descriptivamente. m104 lleva el mismo precio al TIPO DE CAMBIO "
                   "(y descubre que ahí el canal es más débil y se rompe en las "
                   "crisis); m105 generaliza del cobre a los TÉRMINOS DE INTERCAMBIO "
                   "completos. Juntos forman el bloque del canal externo del Perú, "
                   "que m110 (shock externo) y m111 (FED) llevan al extremo."),
    ),
    escenarios=[
        Escenario("contemporaneo", "el cobre impulsa el crecimiento el mismo año (rezago 0)",
                  {"rezago": 0.0},
                  "la correlación contemporánea es la más fuerte (+0.45): el cobre "
                  "golpea rápido — vía exportaciones, recaudación y confianza, no "
                  "solo vía inversión minera (que tardaría).",
                  cadena=["el precio del cobre sube este año", "más dólares de exportación e ingreso fiscal (m89)",
                          "más gasto, inversión y confianza el mismo año", "el PBI crece contemporáneamente (+0.45)"]),
        Escenario("rezagado", "el cobre impulsa con un año de retraso (rezago 1)",
                  {"rezago": 1.0},
                  "con rezago la correlación baja (+0.24): parte del efecto opera "
                  "rápido (mismo año), no con el retraso largo de la inversión — el "
                  "canal de ingreso es más veloz que el de capacidad.",
                  cadena=["mirar el cobre del año pasado", "correlación menor que la contemporánea",
                          "el efecto es rápido (ingreso), no lento (inversión)", "el canal de términos de intercambio golpea en el año"]),
    ],
    verificaciones=[
        Verificacion("cobre y crecimiento se mueven juntos (m89)", _v_correlacion_positiva),
        Verificacion("es el CAMBIO del precio, no el nivel", _v_cambio_mas_que_nivel),
        Verificacion("el cobre explica ~20% (real, no destino)", _v_r2_parcial),
        Verificacion("el superciclo (precio subiendo) creció más", _v_superciclo_mayor),
    ],
    notas="El canal de términos de intercambio (m89) con datos: corr(Δcobre,g)=+0.45. Importa el CAMBIO, no el nivel; R²~0.20 (no destino: m112).",
)
