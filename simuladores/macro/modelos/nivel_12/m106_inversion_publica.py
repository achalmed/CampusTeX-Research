"""simuladores/macro/modelos/nivel_12/m106_inversion_publica.py — inversión pública y crecimiento (nivel 12).

Abre el bloque FISCAL del laboratorio del Perú. La teoría da dos canales para
la inversión pública: demanda (es gasto, activa el multiplicador m37/m04) y
oferta (construye infraestructura, eleva la capacidad m26). El Perú expandió
su inversión pública de ~2.9% del PBI (2004) a ~5.2% (2024) — casi el doble.
Y sin embargo su correlación con el crecimiento es ~0 (incluso negativa,
−0.07). ¿La inversión pública no sirve? No: el modelo enseña que la
correlación cruda ENGAÑA porque la inversión pública es CONTRACÍCLICA. El caso
de manual es 2009: ante la crisis financiera global, el Perú SUBIÓ la
inversión pública de 4.5% a 5.7% del PBI justo cuando el crecimiento se
desplomaba de 9.2% a 1.1% — el plan de estímulo (m69, m37). El gobierno
invierte MÁS cuando el ciclo cae, así que en los datos inversión alta coincide
con crecimiento bajo. Es la endogeneidad exacta que hace difícil medir el
multiplicador (m70) — el tema de m107.

Procedencia: datos BCRP PM10081FA (inversión pública, % del PBI) y PN01728AM
(PBI var%), muestra 2004-2024. Los canales (demanda m37, oferta m26,
contracíclico m69): conocimiento general. Correlación descriptiva, NO causal
(regla del pipeline): el signo ~0 es endogeneidad, no efecto.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, inv = _datos_bcrp.serie("inv_publica", anual=True)
    _, g = _datos_bcrp.serie("pbi_var", anual=True)
    return anos, inv, g


def _idx(anos, p):
    a = int(p["anio_foco"])
    return int(list(anos).index(a)) if a in anos else len(anos) - 1


def _curvas(p):
    anos, inv, g = _series()
    i = _idx(anos, p)
    corr = _datos_bcrp.correlacion(inv, g)
    puntos = [(2009.0, float(inv[anos == 2009][0]), "2009: estímulo (inv ↑, PBI ↓)")]
    if int(anos[i]) != 2009:                          # evita duplicar la etiqueta de 2009
        puntos.append((float(anos[i]), float(inv[i]),
                       f"{int(anos[i])}: inv {inv[i]:.1f}%, PBI {g[i]:+.1f}%"))
    return {"lineas": {"inversión pública (% del PBI)": (anos, inv, config.VERDE),
                       "crecimiento del PBI (%)": (anos, g, config.AZUL2)},
            "puntos": puntos,
            "anotacion": (f"inversión pública (PM10081FA) vs PBI (PN01728AM)\n"
                          f"la inversión subió de {inv[0]:.1f}% a {inv[-1]:.1f}% del PBI (casi 2×)\n"
                          f"corr con el crecimiento = {corr:+.2f} (engañosa: contracíclica)")}


def _resultados(p):
    anos, inv, g = _series()
    i = _idx(anos, p)
    m = anos != 2020
    return {"corr(inversión pública %PBI, crecimiento)": float(_datos_bcrp.correlacion(inv, g)),
            "corr excluyendo 2020 (COVID)": float(_datos_bcrp.correlacion(inv[m], g[m])),
            "inversión pública media 2004-2024 (% PBI)": float(inv.mean()),
            "inversión pública 2004 (% PBI)": float(inv[0]),
            "inversión pública 2024 (% PBI)": float(inv[-1]),
            f"inversión pública {int(anos[i])} (% PBI)": float(inv[i]),
            f"crecimiento {int(anos[i])} (%)": float(g[i])}


def _ecuaciones_calibradas(p):
    anos, inv, g = _series()
    return [f"inversión pública: ${inv[0]:.1f}\\%\\to{inv[-1]:.1f}\\%$ del PBI (2004-2024, casi 2×)",
            f"corr con el crecimiento $= {_datos_bcrp.correlacion(inv, g):+.2f}$ (contracíclica, m69): endogeneidad, no efecto"]


_P0 = {"anio_foco": 2009.0}


def _v_inversion_subio():
    anos, inv, g = _series()
    return inv[-1] > inv[0] and inv.max() > 5 and inv[0] < 3.5, \
        (f"el Perú expandió la inversión pública de {inv[0]:.1f}% a {inv[-1]:.1f}% del PBI (2004-2024, casi 2×): "
         "un esfuerzo real de infraestructura (capacidad, m26) y de demanda (multiplicador, m37)")


def _v_correlacion_enganosa():
    anos, inv, g = _series()
    corr = _datos_bcrp.correlacion(inv, g)
    return corr < 0.15, \
        (f"la correlación inversión pública-crecimiento es {corr:+.2f} (~0, incluso negativa): NO significa "
         "que la inversión pública no sirva — es contracíclica, se despliega cuando el crecimiento cae (m69)")


def _v_2009_estimulo():
    anos, inv, g = _series()
    i08 = list(anos).index(2008)
    i09 = list(anos).index(2009)
    return inv[i09] > inv[i08] and g[i09] < g[i08], \
        (f"2009 es el caso de manual: la inversión pública subió {inv[i08]:.1f}%→{inv[i09]:.1f}% del PBI mientras "
         f"el crecimiento caía {g[i08]:+.1f}%→{g[i09]:+.1f}% — el plan de estímulo contracíclico (m69, m37) ante la crisis global")


def _v_endogeneidad_sistematica():
    anos, inv, g = _series()
    m = anos != 2020
    corr = _datos_bcrp.correlacion(inv[m], g[m])
    return corr < 0, \
        (f"aun excluyendo el COVID la correlación es {corr:+.2f} < 0: la contraciclicidad es sistemática, "
         "no un año raro — el gobierno invierte cuando el ciclo cae (m69). Esta endogeneidad hace difícil medir el multiplicador (m70, m107)")


MODELO = Modelo(
    id="m106", nivel=12,
    nombre="Inversión pública → crecimiento (BCRP)",
    xlabel="Año", ylabel="Porcentaje (%)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2004, 2024, 1, "Año a destacar (inversión vs crecimiento)",
                  grupo="análisis", definicion="año a inspeccionar; 2009 es el estímulo contracíclico de manual"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="El Perú casi duplicó su inversión pública (3%→5% del PBI), pero no correlaciona con el crecimiento. ¿No sirve la inversión pública?",
        variables=[("g_pública_t", "inversión pública, % del PBI (BCRP PM10081FA)"),
                   ("g_t", "crecimiento del PBI (BCRP PN01728AM)"),
                   ("2009", "el estímulo contracíclico: inversión ↑, crecimiento ↓")],
        derivacion=["dato: \\;inv\\;pública_t \\;(PM10081FA, \\%\\;PBI), \\;g_t \\;(PN01728AM)",
                    "corr(inv, g) \\approx -0.07 \\;(engañosa)",
                    "porque\\;inv\\;pública\\;es\\;CONTRACÍCLICA \\;(m69): \\;sube\\;cuando\\;g\\;cae",
                    "2009: \\;inv \\;4.5\\%\\to5.7\\%, \\;g \\;9.2\\%\\to1.1\\% \\;(estímulo)"],
        contexto=("Este modelo abre el bloque fiscal del laboratorio del Perú, y lo "
                  "hace con una paradoja instructiva. La teoría da razones sólidas "
                  "para que la inversión pública impulse el crecimiento: por el lado "
                  "de la demanda es gasto que activa el multiplicador (m04, m37), y "
                  "por el lado de la oferta construye la infraestructura que eleva "
                  "la capacidad productiva (carreteras, puertos, escuelas — el "
                  "capital de m26). El Perú, además, hizo un esfuerzo real: su "
                  "inversión pública pasó de cerca de 2.9% del PBI en 2004 a 5.2% en "
                  "2024, casi el doble. Y sin embargo, al mirar los datos, la "
                  "correlación entre inversión pública y crecimiento es "
                  "prácticamente nula, incluso ligeramente negativa (−0.07). ¿Debemos "
                  "concluir que la inversión pública no sirve? De ninguna manera — y "
                  "entender por qué es la lección. La inversión pública es "
                  "CONTRACÍCLICA: el gobierno la usa como herramienta de "
                  "estabilización, aumentándola cuando la economía se debilita y "
                  "moderándola cuando crece por sí sola. El caso de manual es 2009: "
                  "ante la crisis financiera global, el Perú lanzó un plan de "
                  "estímulo y subió la inversión pública de 4.5% a 5.7% del PBI justo "
                  "cuando el crecimiento se desplomaba de 9.2% a 1.1% (m69, m37). En "
                  "los datos, entonces, la inversión pública ALTA coincide con "
                  "crecimiento BAJO — no porque lo cause, sino porque responde a él. "
                  "Es exactamente la ENDOGENEIDAD que hace notoriamente difícil "
                  "medir el multiplicador fiscal (m70): la política reacciona al "
                  "ciclo, así que su correlación con el ciclo no revela su efecto. "
                  "La lección se completa con una nota peruana: parte del pobre "
                  "vínculo también refleja problemas de EJECUCIÓN (el Estado "
                  "peruano crónicamente sub-ejecuta su presupuesto de inversión) y "
                  "de calidad del gasto — pero incluso con ejecución perfecta, la "
                  "correlación cruda seguiría sin medir el efecto, por la "
                  "contraciclicidad. Para medirlo de verdad hace falta identificación "
                  "(m70, m107), no correlación."),
        autores=("Datos: BCRP (PM10081FA inversión pública % PBI, PN01728AM PBI); "
                 "los canales demanda/oferta: m37/m26; la política contracíclica: "
                 "m69; la endogeneidad de la política y la dificultad de medir "
                 "multiplicadores: m70 (conocimiento general)."),
        supuestos=[
            "Correlación descriptiva: cuantifica co-movimiento, no el efecto causal de la inversión pública (que exige identificación, m70).",
            "La inversión pública (% PBI) del BCRP se toma como dato; su EJECUCIÓN efectiva y CALIDAD (que afectan el impacto real) no se modelan aquí.",
            "El signo ~0/negativo se interpreta como endogeneidad (política contracíclica, m69), la lectura estándar — no como evidencia de que la inversión pública reduzca el crecimiento.",
        ],
        ecuaciones=[
            Ecuacion("inv\\;pública: \\;2.9\\% \\to 5.2\\%\\;del\\;PBI \\;(2004\\text{-}2024)", "el esfuerzo real",
                     "el Perú casi duplicó su inversión pública como porcentaje del PBI: un esfuerzo "
                     "sostenido de infraestructura (capacidad, m26) y demanda (multiplicador, m37)."),
            Ecuacion("corr(inv\\;pública, \\; g) \\approx -0.07 \\;\\neq\\; efecto", "la correlación engañosa",
                     "el signo ~0/negativo NO es el efecto de la inversión: es endogeneidad, porque la "
                     "inversión pública es contracíclica (sube cuando g cae, m69) — verificado con 2009."),
            Ecuacion("2009: \\;inv \\;4.5\\%\\to5.7\\%, \\;\\; g \\;9.2\\%\\to1.1\\%", "el estímulo de manual",
                     "ante la crisis global el Perú subió la inversión pública mientras el crecimiento "
                     "se desplomaba: el plan de estímulo contracíclico (m69, m37) — la endogeneidad hecha episodio."),
        ],
        intuicion=("La imagen es la de 2009: crisis mundial, el crecimiento peruano "
                   "cae de 9% a 1%, y el gobierno responde subiendo la inversión "
                   "pública a máximos. Un observador ingenuo que solo mire la "
                   "correlación vería 'más inversión pública, menos crecimiento' y "
                   "concluiría, absurdamente, que invertir hace daño. El economista "
                   "ve lo contrario: la inversión pública se disparó PARA amortiguar "
                   "la caída, y probablemente evitó que fuera peor. Es la misma "
                   "trampa de causalidad inversa de m101 (tasa e inflación), ahora "
                   "en lo fiscal: una política bien manejada es contracíclica, así "
                   "que su correlación con el ciclo tiene el signo 'equivocado'. Por "
                   "eso medir el multiplicador fiscal es de los problemas más "
                   "difíciles de la macro empírica (m70): hay que encontrar "
                   "variaciones del gasto que NO respondan al ciclo (guerras, "
                   "desastres, reglas) para aislar el efecto. La moraleja para leer "
                   "datos peruanos: cuando veas que la inversión pública sube en los "
                   "malos años, no es que cause los malos años — es que para eso "
                   "está. Y la nota de política: el Perú invierte más que antes, "
                   "pero el desafío es EJECUTAR bien y con calidad, no solo "
                   "presupuestar."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica entre "
                    "inversión pública y crecimiento. El resultado es que la "
                    "correlación es ~0/negativa (−0.07, y −0.22 sin COVID) por "
                    "contraciclicidad (m69), no porque la inversión pública carezca "
                    "de efecto — medirlo exige identificación (m70)."),
        limitaciones=[
            "Correlación, no efecto: la contraciclicidad (m69) sesga el signo; el efecto causal exige identificación (variación exógena del gasto, m70) — el trabajo de m107.",
            "Ignora ejecución y calidad: la inversión pública PRESUPUESTADA (% PBI) no es la EJECUTADA ni la eficiente; el impacto real depende de ambas (gobernanza).",
            "Nivel agregado y anual: mezcla infraestructura productiva con gasto de capital de bajo retorno; no distingue proyectos buenos de malos.",
        ],
        evolucion=("Abre el bloque fiscal mostrando, con el episodio de 2009, la "
                   "endogeneidad de la política contracíclica (m69) — el obstáculo "
                   "central para medir su efecto. m107 lo enfrenta de lleno: cómo se "
                   "estima (y cómo NO se estima) el multiplicador fiscal (m37, m70). "
                   "m108 pasa a la deuda que esta inversión ayuda a financiar y su "
                   "sostenibilidad (m64). Juntos son la política fiscal peruana con "
                   "datos."),
    ),
    escenarios=[
        Escenario("estimulo_2009", "el estímulo contracíclico (2009)",
                  {"anio_foco": 2009.0},
                  "2009: inversión pública en máximos (5.7% del PBI) con crecimiento "
                  "en mínimos (1.1%) — el estímulo ante la crisis global. La "
                  "correlación negativa es esto: la política responde al ciclo (m69).",
                  cadena=["crisis financiera global (2009)", "el crecimiento se desploma (9.2%→1.1%)",
                          "el gobierno SUBE la inversión pública (estímulo, m69/m37)", "inversión alta + crecimiento bajo en los datos",
                          "correlación negativa = causalidad inversa, no efecto"]),
        Escenario("boom_2008", "el boom privado (2008)",
                  {"anio_foco": 2008.0},
                  "2008: crecimiento altísimo (9.2%) con inversión pública todavía "
                  "moderada (4.5%) — en el boom el sector privado lidera y el Estado "
                  "no necesita empujar. El otro extremo de la contraciclicidad.",
                  cadena=["superciclo, boom privado (2008)", "el crecimiento es muy alto (9.2%)",
                          "la inversión pública no necesita empujar (aún 4.5%)", "crecimiento alto + inversión moderada",
                          "refuerza el signo negativo de la correlación (contracíclica)"]),
        Escenario("reciente_2024", "el esfuerzo reciente (2024)",
                  {"anio_foco": 2024.0},
                  "2024: inversión pública otra vez alta (5.2%) con crecimiento "
                  "modesto (3.5%) — el Estado sostiene la demanda tras años flojos, "
                  "pero el desafío es ejecutar con calidad, no solo presupuestar.",
                  cadena=["años de crecimiento flojo (post-2022)", "el Estado sostiene la inversión (5.2%)",
                          "crecimiento aún modesto (3.5%)", "el reto ya no es cuánto, sino ejecutar bien (gobernanza)"]),
    ],
    verificaciones=[
        Verificacion("el Perú casi duplicó la inversión pública", _v_inversion_subio),
        Verificacion("la correlación con el crecimiento engaña (~0)", _v_correlacion_enganosa),
        Verificacion("2009: el estímulo contracíclico (inv ↑, PBI ↓)", _v_2009_estimulo),
        Verificacion("contraciclicidad sistemática = endogeneidad (m70)", _v_endogeneidad_sistematica),
    ],
    notas="Inversión pública ~0/negativa con el crecimiento porque es CONTRACÍCLICA (2009 estímulo: inv↑, PBI↓). Endogeneidad, no efecto — el problema de medir multiplicadores (m70, m107).",
)
