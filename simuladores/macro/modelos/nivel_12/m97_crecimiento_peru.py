"""simuladores/macro/modelos/nivel_12/m97_crecimiento_peru.py — crecimiento del Perú, con datos del BCRP (nivel 12).

PRIMER modelo del currículo con DATOS REALES. La serie del PBI (variación %
interanual, BCRP PN01728AM) 2004-2024 cuenta la historia macro peruana del
siglo: el superciclo de commodities (2004-2013, ~6-9%), la desaceleración
post-boom (2014-2019), el desplome COVID (2020, −10.9%, el peor año de la
serie) y la recuperación. El laboratorio LEE el dato, calcula el crecimiento
promedio y la volatilidad, e identifica los episodios — conectando la teoría
(Solow m26, ciclo m17, cobre m89) con la evidencia peruana.

Procedencia: dato BCRP PN01728AM (PBI, var% interanual), muestra 2004-2024,
descargada por connectors/bcrp el 2026-08-19. Las lecturas (episodios,
promedios) son descriptivas; NO son pronósticos ni atribución causal.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _serie_pbi():
    return _datos_bcrp.serie("pbi_var", anual=True)      # (años, var% interanual)


def _curvas(p):
    anos, g = _serie_pbi()
    prom = float(g.mean())
    # marcar el umbral de crecimiento "potencial" elegido por el usuario
    return {"lineas": {"crecimiento del PBI (BCRP, %)": (anos, g, config.AZUL2),
                       f"promedio {anos[0]:.0f}-{anos[-1]:.0f} ({prom:.1f}%)":
                           (anos, np.full(len(anos), prom), config.DORADO),
                       f"potencial supuesto ({p['g_pot']:.1f}%)":
                           (anos, np.full(len(anos), p["g_pot"]), config.GRIS)},
            "puntos": [(2020.0, float(g[anos == 2020][0]), "COVID −10.9%"),
                       (2008.0, float(g[anos == 2008][0]), "boom +9.2%")],
            "anotacion": (f"PBI Perú (BCRP PN01728AM), {len(anos)} años\n"
                          f"crecimiento promedio {prom:.1f}%, "
                          f"volatilidad {float(g.std()):.1f} pp\n"
                          "superciclo → desaceleración → COVID → recuperación")}


def _resultados(p):
    anos, g = _serie_pbi()
    boom = g[(anos >= 2004) & (anos <= 2013)].mean()
    post = g[(anos >= 2014) & (anos <= 2019)].mean()
    return {"crecimiento promedio 2004-2024 (%)": float(g.mean()),
            "volatilidad (desv. est., pp)": float(g.std()),
            "peor año (COVID 2020, %)": float(g.min()),
            "mejor año (%)": float(g.max()),
            "promedio superciclo 2004-2013 (%)": float(boom),
            "promedio post-boom 2014-2019 (%)": float(post),
            "años bajo el potencial supuesto": float(np.sum(g < p["g_pot"]))}


def _ecuaciones_calibradas(p):
    anos, g = _serie_pbi()
    return [f"$\\bar{{g}}_{{2004\\text{{-}}24}} = {float(g.mean()):.1f}\\%$ "
            f"(BCRP PN01728AM)",
            f"boom $= {float(g[(anos <= 2013)].mean()):.1f}\\%$ vs "
            f"post-boom $= {float(g[(anos >= 2014) & (anos <= 2019)].mean()):.1f}\\%$"]


_P0 = {"g_pot": 4.0}


def _v_promedio_real():
    anos, g = _serie_pbi()
    prom = float(g.mean())
    return 3.0 < prom < 6.0, \
        (f"el crecimiento promedio real del Perú 2004-2024 es {prom:.1f}% (BCRP): "
         "un emergente de crecimiento medio-alto, sostenido por el superciclo")


def _v_covid_peor():
    anos, g = _serie_pbi()
    return float(g.min()) == float(g[anos == 2020][0]) and float(g.min()) < -8, \
        (f"2020 (COVID) fue el PEOR año de la serie ({float(g.min()):.1f}%): el desplome "
         "más profundo, un shock global (m81) sobre una economía abierta")


def _v_superciclo_mayor():
    anos, g = _serie_pbi()
    boom = g[(anos >= 2004) & (anos <= 2013)].mean()
    post = g[(anos >= 2014) & (anos <= 2019)].mean()
    return boom > post, \
        (f"el superciclo (2004-2013, {boom:.1f}%) creció más que el post-boom "
         f"(2014-2019, {post:.1f}%): el fin del boom del cobre (m89) desaceleró — con datos")


def _v_volatil():
    anos, g = _serie_pbi()
    return float(g.std()) > 2.5, \
        (f"la volatilidad del crecimiento peruano ({float(g.std()):.1f} pp) es alta: "
         "una economía abierta y dependiente de commodities es cíclica (m17, m89)")


MODELO = Modelo(
    id="m97", nivel=12,
    nombre="Crecimiento del Perú (datos BCRP)",
    xlabel="Año", ylabel="Crecimiento del PBI (%)",
    parametros=[
        Parametro("g_pot", _P0["g_pot"], 2, 6, 0.25, "Crecimiento potencial supuesto (%)",
                  grupo="referencia", definicion="umbral de referencia; el potencial real se estima en m98"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo ha crecido el Perú en el siglo XXI — y qué revela la serie del BCRP sobre su modelo económico?",
        variables=[("g_t", "crecimiento del PBI, var% interanual (BCRP PN01728AM)"),
                   ("superciclo vs post-boom", "los dos regímenes de la serie"),
                   ("2020", "el desplome COVID, el peor de la muestra")],
        derivacion=["dato: \\;g_t = PBI\\;var\\%\\;interanual\\;(BCRP\\;PN01728AM)",
                    "\\bar{g}, \\sigma_g \\;descriptivos\\;de\\;la\\;muestra\\;2004\\text{-}2024",
                    "episodios: \\;boom\\;(2004\\text{-}13) > post\\text{-}boom > COVID"],
        contexto=("Este es el primer modelo del currículo que se calibra con DATOS "
                  "REALES, descargados del BCRP por el conector de datafw "
                  "(autorización explícita de Edison para el nivel 12). La serie "
                  "del PBI peruano (variación porcentual interanual, código "
                  "PN01728AM) entre 2004 y 2024 es un retrato de la economía "
                  "peruana del siglo XXI, y todo el aparato teórico construido en "
                  "los niveles 1-11 sirve para leerla. Cuenta cuatro capítulos. El "
                  "SUPERCICLO de commodities (2004-2013): con el cobre y los "
                  "minerales en máximos (m88), el Perú creció 6-9% anual, uno de "
                  "los desempeños más altos de la región. La DESACELERACIÓN "
                  "post-boom (2014-2019): al revertir el ciclo del cobre (m89), el "
                  "crecimiento bajó a 3-4% — la dependencia estructural del recurso "
                  "hecha evidencia. El DESPLOME COVID (2020): −10.9%, el peor año "
                  "de la serie, un shock global (m81) que golpeó a una economía "
                  "abierta con especial dureza (confinamiento estricto + colapso "
                  "del cobre + freno de la minería). Y la RECUPERACIÓN posterior. "
                  "El laboratorio lee el dato, calcula el crecimiento promedio "
                  "(~4-5%) y la volatilidad, e identifica los episodios — "
                  "conectando la teoría del crecimiento (Solow, m26), del ciclo "
                  "(m17) y del cobre (m89) con la evidencia. La lección de fondo, "
                  "que los modelos siguientes desarrollan: el crecimiento peruano "
                  "es alto pero volátil y dependiente de commodities — el desafío "
                  "de desarrollo es diversificar (m112) para crecer más estable."),
        autores=("Dato: BCRP (BCRPData, serie PN01728AM); la lectura por episodios "
                 "y la conexión con la teoría es del laboratorio — conocimiento "
                 "general aplicado a la evidencia peruana."),
        supuestos=[
            "La serie es el agregado oficial del BCRP (var% interanual del PBI): se toma como dato, sin re-estimar.",
            "Las lecturas (episodios, promedios, volatilidad) son DESCRIPTIVAS: no son pronósticos ni atribución causal (la causalidad exige más que correlación — regla del pipeline).",
            "El 'potencial supuesto' es un umbral de referencia elegido por el usuario; el potencial ESTIMADO (con filtro) es m98.",
        ],
        ecuaciones=[
            Ecuacion("g_t = \\frac{PBI_t - PBI_{t-12}}{PBI_{t-12}} \\;(BCRP\\;PN01728AM)",
                     "el dato",
                     "la variación interanual del PBI que publica el BCRP: el laboratorio la lee, "
                     "no la construye — el archivo original es sagrado (regla 1 de datafw)."),
            Ecuacion("boom_{2004\\text{-}13} > post\\text{-}boom_{2014\\text{-}19} > COVID_{2020}",
                     "los regímenes",
                     "la serie se parte en episodios que la teoría explica: superciclo (m88), "
                     "desaceleración (m89) y shock global (m81) — verificado con el dato."),
        ],
        intuicion=("Ver la serie real del PBI peruano después de construir 96 "
                   "modelos teóricos es el momento en que el laboratorio 'aterriza': "
                   "cada rasgo de la curva tiene un modelo que lo explica. El boom "
                   "de 2004-2013 es m88 (materias primas) y m26 (acumulación); la "
                   "desaceleración de 2014-2019 es m89 (fin del ciclo del cobre); "
                   "el desplome de 2020 es m81 (COVID como shock global) amplificado "
                   "por la apertura (m43) y la minería; la recuperación es el rebote "
                   "de m81. La volatilidad alta confirma lo que m17 y m89 "
                   "predecían: una economía abierta y dependiente de commodities es "
                   "estructuralmente cíclica. Y la lección de política se vuelve "
                   "concreta: el crecimiento promedio de ~4-5% es bueno para un "
                   "emergente, pero su dependencia del cobre lo hace frágil — "
                   "diversificar (m112) y elevar la productividad (m90, m33) es "
                   "cómo se pasa de crecer rápido a crecer rápido Y estable."),
        equilibrio=("No hay equilibrio que resolver: es una serie observada que el "
                    "laboratorio describe (promedio, volatilidad, episodios) y "
                    "conecta con la teoría. El 'equilibrio' relevante es el "
                    "crecimiento potencial, que m98 estima separando tendencia de "
                    "ciclo."),
        limitaciones=[
            "Muestra corta (2004-2024, anual): suficiente para los episodios recientes, no para tendencias seculares (el crecimiento de largo plazo exige series más largas).",
            "Descriptivo, no causal: identificar QUÉ causó cada episodio (cobre, política, shocks) exige los modelos siguientes y cuidado econométrico (regla del pipeline: nunca causalidad automática).",
            "Var% interanual mezcla nivel y ciclo: separar el potencial (tendencia) del ciclo es m98; atribuir a factores es m103-m105.",
        ],
        evolucion=("Abre el laboratorio del Perú aterrizando la teoría en el dato. "
                   "m98 estima el potencial y la brecha (m16 con datos); m99 hace "
                   "lo mismo con la inflación; m100 estima la regla del BCRP (m38 "
                   "con datos); m103-m105 cuantifican el canal del cobre (m89 con "
                   "datos). Es el puente entre los 96 modelos teóricos y la "
                   "economía peruana real."),
    ),
    escenarios=[
        Escenario("potencial_alto", "referencia de potencial en 5% (optimista)",
                  {"g_pot": 5.0},
                  "con un potencial exigente, la mayoría de años recientes quedan "
                  "por debajo: la desaceleración post-boom fue real, no una racha "
                  "mala.",
                  cadena=["potencial de referencia alto (5%)", "muchos años bajo el umbral",
                          "la desaceleración post-boom se ve estructural (m89)",
                          "el reto: recuperar el crecimiento alto sin el boom del cobre"]),
        Escenario("potencial_realista", "referencia en 3.5% (post-boom)",
                  {"g_pot": 3.5},
                  "con un potencial modesto, el Perú reciente lo cumple: el "
                  "crecimiento se 'normalizó' tras el superciclo — la pregunta es si "
                  "3.5% basta para converger (m30).",
                  cadena=["potencial de referencia realista (3.5%)", "el crecimiento reciente lo alcanza",
                          "'nueva normalidad' post-superciclo", "¿basta para converger con los ricos? (m30)"]),
    ],
    verificaciones=[
        Verificacion("crecimiento promedio real 3-6% (BCRP)", _v_promedio_real),
        Verificacion("2020 (COVID) fue el peor año", _v_covid_peor),
        Verificacion("el superciclo creció más que el post-boom", _v_superciclo_mayor),
        Verificacion("crecimiento volátil (economía de commodities)", _v_volatil),
    ],
    notas="Primer modelo con DATOS REALES (BCRP): cada rasgo de la curva tiene un modelo teórico que lo explica.",
)
