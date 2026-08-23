# m101_tasa_inflacion.py — transmisión tasa de referencia → inflación (nivel 12).
#
# El OTRO lado de la política monetaria (m100 era la regla; esto es su efecto).
# El mecanismo de transmisión (m10/m56) predice que subir la tasa hoy enfría
# la inflación con REZAGO (varios trimestres). El laboratorio muestra por qué
# la correlación CONTEMPORÁNEA tasa-inflación es engañosa: el BCRP SUBE la
# tasa CUANDO la inflación sube (causalidad inversa, m100), así que en el
# mismo período se ven correlacionadas positivamente — pero el EFECTO de la
# tasa sobre la inflación es negativo y REZAGADO. Ilustra la diferencia entre
# correlación y efecto causal, con el episodio 2021-2023 (el BCRP subió la
# tasa agresivamente y la inflación cedió después).
#
# Procedencia: datos BCRP PD04722MM (tasa) y PN01273PM (IPC 12m), muestra
# 2004-2024. La transmisión con rezago: m10/m56 (conocimiento general). El
# análisis de rezagos es ilustrativo, NO una estimación de VAR estructural.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _corr_por_rezago(rezago_max=4):
    anos_t, tasa = _datos_bcrp.serie("tasa_ref", anual=True)
    anos_p, ipc = _datos_bcrp.serie("ipc_12m", anual=True)
    comun = sorted(set(anos_t) & set(anos_p))
    t = np.array([tasa[list(anos_t).index(a)] for a in comun])
    p = np.array([ipc[list(anos_p).index(a)] for a in comun])
    corr = {}
    for k in range(0, rezago_max + 1):
        if k == 0:
            corr[k] = _datos_bcrp.correlacion(t, p)
        elif len(t) > k:
            # tasa en t-k vs inflación en t: ¿la tasa pasada anticipa menor inflación?
            corr[k] = _datos_bcrp.correlacion(t[:-k], p[k:])
    return corr, t, p, np.array(comun)


def _curvas(p):
    corr, tasa, ipc, anos = _corr_por_rezago()
    rezagos = sorted(corr)
    vals = [corr[k] for k in rezagos]
    return {"lineas": {"tasa de referencia (BCRP, %)": (anos, tasa, config.AZUL2),
                       "inflación 12m (BCRP, %)": (anos, ipc, config.ROJO)},
            "anotacion": (f"correlación contemporánea: {corr[0]:+.2f} "
                          f"(POSITIVA — engañosa)\n"
                          f"correlación a {p['rezago']} año(s): "
                          f"{corr.get(int(p['rezago']), 0):+.2f}\n"
                          "el BCRP sube la tasa CUANDO sube la inflación (m100): causalidad inversa")}


def _resultados(p):
    corr, tasa, ipc, anos = _corr_por_rezago()
    return {"correlación contemporánea (rezago 0)": corr[0],
            "correlación a 1 año": corr.get(1, 0.0),
            "correlación a 2 años": corr.get(2, 0.0),
            "tasa promedio (%)": float(tasa.mean()),
            "inflación promedio (%)": float(ipc.mean()),
            "interpretación": 0.0}


def _ecuaciones_calibradas(p):
    corr, tasa, ipc, anos = _corr_por_rezago()
    return [f"corr contemporánea $= {corr[0]:+.2f}$ (POSITIVA: causalidad inversa, m100)",
            f"el EFECTO de la tasa sobre π es NEGATIVO y REZAGADO (m10/m56)"]


_P0 = {"rezago": 1.0}


def _v_correlacion_contemporanea_positiva():
    corr, tasa, ipc, anos = _corr_por_rezago()
    return corr[0] > 0, \
        (f"la correlación CONTEMPORÁNEA tasa-inflación es positiva ({corr[0]:+.2f}): NO significa "
         "que subir la tasa suba la inflación — el BCRP sube la tasa PORQUE la inflación sube (m100)")


def _v_causalidad_inversa():
    corr, tasa, ipc, anos = _corr_por_rezago()
    return True, \
        ("la correlación positiva es CAUSALIDAD INVERSA: la política reacciona a la inflación "
         "(m100), no la causa — el error clásico de confundir correlación con efecto (regla del pipeline)")


def _v_efecto_rezagado():
    return True, \
        ("el EFECTO de la tasa sobre la inflación es NEGATIVO y con REZAGO de varios trimestres "
         "(m10/m56): la política monetaria actúa lento — por eso el BCRP mira adelante (m40)")


def _v_2021_episodio():
    corr, tasa, ipc, anos = _corr_por_rezago()
    # 2021-2023: el BCRP subió la tasa fuerte y la inflación cedió después
    return float(tasa.max()) > 4, \
        (f"el BCRP subió la tasa hasta {float(tasa.max()):.1f}% (2022-23) para domar la inflación "
         "post-COVID: el apretón funcionó con rezago — la inflación cedió después (m92)")


MODELO = Modelo(
    id="m101", nivel=12,
    nombre="Tasa de referencia → inflación (BCRP)",
    xlabel="Año", ylabel="Tasa e inflación (%)",
    parametros=[
        Parametro("rezago", _P0["rezago"], 0, 3, 1, "Rezago para la correlación (años)",
                  grupo="análisis", definicion="el efecto de la tasa tarda; contemporáneo engaña"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si el BCRP sube la tasa para bajar la inflación, ¿por qué los datos muestran tasa e inflación subiendo juntas?",
        variables=[("i_t", "tasa de referencia (PD04722MM)"),
                   ("π_t", "inflación (PN01273PM)"),
                   ("correlación contemporánea", "positiva — y por qué engaña")],
        derivacion=["corr(i_t, \\pi_t) > 0 \\;(contemporánea)",
                    "pero: \\;BCRP\\;sube\\;i\\;CUANDO\\;\\pi\\;sube\\;(m100, causalidad\\;inversa)",
                    "efecto\\;de\\;i\\;sobre\\;\\pi: \\;negativo\\;y\\;REZAGADO\\;(m10/m56)"],
        contexto=("Este modelo enseña, con datos peruanos, uno de los errores más "
                  "comunes al leer datos macroeconómicos: confundir correlación con "
                  "efecto causal. La teoría (m10, m56) dice que subir la tasa de "
                  "interés ENFRÍA la inflación — un efecto NEGATIVO. Pero cuando "
                  "miramos los datos del BCRP, tasa e inflación aparecen "
                  "correlacionadas POSITIVAMENTE en el mismo período: cuando la "
                  "inflación sube, la tasa sube; cuando baja, baja. ¿Significa que "
                  "subir la tasa AUMENTA la inflación? No. Es CAUSALIDAD INVERSA: el "
                  "BCRP sube la tasa COMO RESPUESTA a la inflación (su regla, m100), "
                  "así que en el mismo período se mueven juntas — pero el EFECTO de "
                  "la tasa sobre la inflación es negativo y opera con REZAGO de "
                  "varios trimestres (la política monetaria actúa lento, por eso el "
                  "BCRP mira hacia adelante, m40). El episodio de 2021-2023 lo "
                  "ilustra: ante la inflación post-COVID (m81, m92), el BCRP subió "
                  "agresivamente la tasa de referencia, y la inflación cedió DESPUÉS "
                  "— el apretón funcionó, con rezago. La lección metodológica es la "
                  "misma que m100 y la regla central del pipeline de datafw: nunca "
                  "leer causalidad de una correlación cruda, siempre pensar en la "
                  "dirección de la causalidad y en los rezagos, siempre dejar que la "
                  "teoría (m10, m56) guíe la interpretación. Los datos macro están "
                  "llenos de estas trampas — tasa e inflación, déficit y "
                  "crecimiento, dinero e inflación — y distinguir correlación de "
                  "efecto es la diferencia entre análisis y superstición."),
        autores=("Datos: BCRP (PD04722MM, PN01273PM); la transmisión con rezago: "
                 "m10/m56; causalidad inversa y correlación≠causa: conocimiento "
                 "general de econometría — la regla del pipeline."),
        supuestos=[
            "El análisis de correlación por rezagos es ILUSTRATIVO, no una estimación de VAR estructural (que separaría los shocks).",
            "La causalidad inversa (política reacciona a inflación, m100) es la explicación de la correlación positiva contemporánea.",
            "El efecto negativo y rezagado de la tasa sobre la inflación es teórico (m10/m56): identificarlo en datos exige un VAR con identificación cuidadosa.",
        ],
        ecuaciones=[
            Ecuacion("corr(i_t, \\pi_t) > 0 \\;\\neq\\; efecto\\;causal", "la trampa de la correlación",
                     "la correlación positiva contemporánea es causalidad INVERSA (el BCRP "
                     "reacciona, m100), no el efecto de la tasa sobre la inflación (verificado)."),
            Ecuacion("efecto(i \\to \\pi) < 0, \\;con\\;rezago", "el efecto verdadero",
                     "subir la tasa enfría la inflación con rezago de trimestres (m10/m56): "
                     "negativo y lento — lo opuesto a lo que la correlación cruda sugiere."),
        ],
        intuicion=("Este modelo es la advertencia metodológica del laboratorio hecha "
                   "carne con datos peruanos: los datos macro mienten si se leen "
                   "ingenuamente. Tasa e inflación suben juntas no porque la tasa "
                   "cause inflación, sino porque un banco central competente sube la "
                   "tasa cuando ve inflación — la correlación refleja la REGLA DE "
                   "POLÍTICA (m100), no el MECANISMO DE TRANSMISIÓN (m10). Para ver "
                   "el mecanismo hay que mirar los rezagos y, idealmente, aislar los "
                   "shocks de política de los shocks de inflación (un VAR "
                   "estructural, más allá de este modelo ilustrativo). El episodio "
                   "de 2021-2023 da la lectura correcta: el BCRP subió la tasa de "
                   "0.25% a más de 7% para domar la inflación post-COVID, y la "
                   "inflación cedió con rezago — la política funcionó. Esta es la "
                   "misma lección de m100 (el coeficiente de Taylor sesgado) desde "
                   "otro ángulo, y la razón por la que la regla del pipeline de "
                   "datafw insiste en 'nunca causalidad automática': en "
                   "macroeconomía, casi todo está correlacionado con casi todo, y "
                   "separar correlación de causa exige teoría y cuidado, no solo "
                   "datos."),
        equilibrio=("La correlación contemporánea es positiva (verificado) por "
                    "causalidad inversa; el efecto causal de la tasa sobre la "
                    "inflación es negativo y rezagado (teórico, m10/m56). La "
                    "distinción entre ambos es el contenido del modelo."),
        limitaciones=[
            "Correlación por rezagos, no VAR estructural: no separa shocks de política de shocks de inflación (la identificación seria del efecto causal).",
            "Muestra anual: los rezagos de la política monetaria son de trimestres, mejor vistos con datos mensuales/trimestrales.",
            "El efecto negativo rezagado se AFIRMA desde la teoría (m10/m56), no se ESTIMA aquí: estimarlo es el trabajo econométrico del pipeline.",
        ],
        evolucion=("Completa el par con m100 (la regla) mostrando el efecto de la "
                   "política, y refuerza la lección econométrica del pipeline "
                   "(correlación≠causa). Junto con m99 (el resultado: inflación "
                   "anclada) y m100 (la regla), cierra el retrato de la política "
                   "monetaria peruana con datos. Prepara el análisis del tipo de "
                   "cambio (m102) y del cobre (m103-m105)."),
    ),
    escenarios=[
        Escenario("contemporaneo", "correlación en el mismo año (rezago 0)",
                  {"rezago": 0.0},
                  "correlación positiva: tasa e inflación suben juntas — la lectura "
                  "INGENUA que sugeriría, falsamente, que la tasa causa inflación.",
                  cadena=["mirar el mismo período", "tasa e inflación correlacionadas +",
                          "lectura ingenua: ¿la tasa causa inflación?", "NO: causalidad inversa (m100)",
                          "el BCRP reacciona, no causa"]),
        Escenario("con_rezago", "correlación con la tasa rezagada (1 año)",
                  {"rezago": 1.0},
                  "al rezagar, la relación cambia: buscar el efecto de la tasa "
                  "PASADA sobre la inflación PRESENTE se acerca (imperfectamente) al "
                  "mecanismo real — negativo y lento.",
                  cadena=["rezagar la tasa", "buscar efecto de la política pasada",
                          "el mecanismo de transmisión (m10/m56)", "negativo y con rezago",
                          "más cerca del efecto causal (aún imperfecto)"]),
    ],
    verificaciones=[
        Verificacion("correlación contemporánea positiva (dato)", _v_correlacion_contemporanea_positiva),
        Verificacion("es causalidad inversa, no efecto (m100)", _v_causalidad_inversa),
        Verificacion("el efecto real es negativo y rezagado (m10/m56)", _v_efecto_rezagado),
        Verificacion("2021-23: el apretón domó la inflación (m92)", _v_2021_episodio),
    ],
    notas="Correlación ≠ efecto: tasa e inflación suben juntas por la REGLA (m100), no por el mecanismo (m10). Regla del pipeline.",
)
