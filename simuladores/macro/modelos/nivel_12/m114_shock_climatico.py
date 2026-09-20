"""simuladores/macro/modelos/nivel_12/m114_shock_climatico.py — shock climático: El Niño (nivel 12).

El Perú es de los países más expuestos del mundo a El Niño: el calentamiento
del mar frente a su costa desorganiza las lluvias (inundaciones en el norte,
sequías en el sur), golpea la AGRICULTURA y la PESCA (la anchoveta huye del
agua caliente) y daña la infraestructura. En macro, es un SHOCK DE OFERTA
ADVERSO de manual (m11, m52): sube los precios de los alimentos (m83) Y baja la
producción a la vez —estanflacionario— y, si el ancla del banco central aguanta
(m40), es TRANSITORIO: cuando el clima se normaliza, la producción se recupera
y la inflación revierte. El laboratorio simula ese pulso, calibrado a los dos
episodios recientes: El Niño costero de 2017 (inundaciones en el norte, ~1pp de
crecimiento perdido en el primer trimestre) y El Niño de 2023 (que junto con la
crisis política contribuyó a la recesión de ese año, −0.3%).

Procedencia: DECISIÓN DE DISEÑO — no hay conector SENAMHI todavía, así que el
shock climático se MODELA como un shock de oferta transitorio (m11/m52) con
calibración DIDÁCTICA inspirada en la magnitud de El Niño 2017/2023 (no son
datos oficiales de un índice climático). La estructura del shock de oferta:
m11/m52; alimentos: m83; anclaje: m40 (conocimiento general).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config

_T = 8                    # trimestres simulados
_T_SHOCK = 2              # trimestre del impacto de El Niño
_G0 = 3.0                 # crecimiento tendencial (%), referencia
_PI0 = 2.0                # inflación meta (%), ancla del BCRP (m40)


def _simular(p):
    """Pulso de un shock de oferta transitorio (El Niño): la producción cae y la
    inflación de alimentos sube en el impacto, y ambas revierten al disiparse."""
    intensidad = p["intensidad"]                  # severidad de El Niño (0-3)
    persistencia = p["persistencia"]              # cuán rápido se disipa (0-1)
    t = np.arange(_T)
    # el shock golpea en _T_SHOCK y decae geométricamente (transitorio)
    pulso = np.where(t >= _T_SHOCK, persistencia ** (t - _T_SHOCK), 0.0)
    pulso[t < _T_SHOCK] = 0.0
    caida_producto = -1.0 * intensidad * pulso    # pp de producto perdido
    alza_inflacion = 0.9 * intensidad * pulso     # pp de inflación de alimentos (m83)
    g = _G0 + caida_producto
    pi = _PI0 + alza_inflacion
    return t, g, pi, caida_producto, alza_inflacion


def _curvas(p):
    t, g, pi, cp, ai = _simular(p)
    x = t.astype(float)
    return {"lineas": {"crecimiento (%)": (x, g, config.AZUL2),
                       "inflación (%)": (x, pi, config.ROJO),
                       "tendencia / meta": (x, np.full(_T, _G0), config.GRIS)},
            "puntos": [(float(_T_SHOCK), float(g[_T_SHOCK]), "El Niño: producción ↓"),
                       (float(_T_SHOCK), float(pi[_T_SHOCK]), "y alimentos ↑ (m83)")],
            "anotacion": (f"shock de oferta transitorio (El Niño), calibración didáctica\n"
                          f"impacto: producto {cp[_T_SHOCK]:+.1f}pp, inflación {ai[_T_SHOCK]:+.1f}pp\n"
                          "estanflacionario y TRANSITORIO (revierte con ancla, m40)")}


def _resultados(p):
    t, g, pi, cp, ai = _simular(p)
    return {"crecimiento en el impacto (%)": float(g[_T_SHOCK]),
            "inflación en el impacto (%)": float(pi[_T_SHOCK]),
            "producto perdido en el impacto (pp)": float(cp[_T_SHOCK]),
            "alza de inflación en el impacto (pp)": float(ai[_T_SHOCK]),
            "crecimiento al final (%)": float(g[-1]),
            "inflación al final (%)": float(pi[-1]),
            "trimestres hasta casi normalizar": float(np.sum(np.abs(cp) > 0.1))}


def _ecuaciones_calibradas(p):
    t, g, pi, cp, ai = _simular(p)
    return [f"shock de oferta El Niño: producto ${cp[_T_SHOCK]:+.1f}$pp Y inflación ${ai[_T_SHOCK]:+.1f}$pp (estanflación, m11)",
            f"transitorio: revierte a $g={_G0:.0f}\\%$, $\\pi={_PI0:.0f}\\%$ si el ancla aguanta (m40)"]


_P0 = {"intensidad": 2.0, "persistencia": 0.5}


def _v_estanflacionario():
    t, g, pi, cp, ai = _simular(_P0)
    return cp[_T_SHOCK] < 0 and ai[_T_SHOCK] > 0, \
        (f"El Niño es un shock de OFERTA (m11): en el impacto la producción CAE ({cp[_T_SHOCK]:+.1f}pp) y la "
         f"inflación SUBE ({ai[_T_SHOCK]:+.1f}pp) a la vez — estanflacionario, la firma del shock de oferta (a diferencia del de demanda)")


def _v_transitorio():
    t, g, pi, cp, ai = _simular(_P0)
    return abs(g[-1] - _G0) < 0.3 and abs(pi[-1] - _PI0) < 0.3, \
        (f"el shock es TRANSITORIO: al disiparse El Niño, el crecimiento vuelve a {g[-1]:.1f}% y la inflación a "
         f"{pi[-1]:.1f}% — la producción agrícola se recupera y los precios revierten (si el ancla aguanta, m40)")


def _v_intensidad_escala():
    suave = _simular({"intensidad": 1.0, "persistencia": 0.5})[3][_T_SHOCK]
    fuerte = _simular({"intensidad": 3.0, "persistencia": 0.5})[3][_T_SHOCK]
    return abs(fuerte) > abs(suave), \
        (f"a mayor severidad de El Niño, mayor golpe: un evento fuerte quita {abs(fuerte):.1f}pp de producto vs "
         f"{abs(suave):.1f}pp uno suave — 2017 (costero) y 2023 fueron severos; la exposición del Perú es estructural")


def _v_ancla_contiene():
    t, g, pi, cp, ai = _simular(_P0)
    return pi.max() < _PI0 + 3, \
        (f"el ancla del BCRP (m40) CONTIENE el pico: la inflación sube a lo sumo {pi.max():.1f}% y no espirala (m14) — "
         "el banco central 'mira a través' de un shock de oferta transitorio en vez de sobre-reaccionar (m113)")


MODELO = Modelo(
    id="m114", nivel=12,
    nombre="Shock climático: El Niño (Perú)",
    xlabel="Trimestre", ylabel="Porcentaje (%)",
    parametros=[
        Parametro("intensidad", _P0["intensidad"], 0, 3, 0.5, "Severidad de El Niño",
                  grupo="shock", definicion="0 = sin evento, 3 = El Niño extraordinario (2017 costero, 2023)"),
        Parametro("persistencia", _P0["persistencia"], 0.1, 0.9, 0.1, "Persistencia del shock",
                  grupo="shock", definicion="cuán lento se disipa; el clima normaliza y la producción se recupera"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo golpea El Niño a la macroeconomía peruana — y por qué el banco central debe 'mirar a través' del pico de precios?",
        variables=[("intensidad", "severidad del evento El Niño (shock de oferta)"),
                   ("g", "crecimiento — cae en el impacto (agricultura, pesca)"),
                   ("π", "inflación — sube en el impacto (alimentos, m83), transitoria")],
        derivacion=["El\\;Niño = shock\\;de\\;oferta\\;adverso\\;(m11, m52)",
                    "impacto: \\;producto\\downarrow \\;Y\\; inflación\\;de\\;alimentos\\uparrow \\;(estanflación)",
                    "transitorio: \\;revierte\\;a\\;g_0, \\pi_0 \\;si\\;el\\;ancla\\;aguanta\\;(m40)",
                    "el\\;BCRP\\;mira\\;a\\;través \\;(no\\;sobre\\text{-}reacciona, m113)"],
        contexto=("El Perú tiene una vulnerabilidad geográfica singular: El Niño, el "
                  "calentamiento periódico del Pacífico oriental, se origina "
                  "literalmente frente a sus costas y lo golpea con especial dureza. "
                  "Cuando ocurre, las lluvias se desorganizan —inundaciones "
                  "devastadoras en el norte, sequías en el sur—, la agricultura "
                  "pierde cosechas, la anchoveta (base de la harina de pescado, un "
                  "gran export) huye de las aguas calientes y la infraestructura "
                  "—carreteras, puentes— se destruye. En el lenguaje del "
                  "laboratorio, El Niño es un SHOCK DE OFERTA ADVERSO de manual "
                  "(m11, m52): a diferencia de un shock de demanda, mueve la "
                  "producción y los precios en direcciones OPUESTAS. En el impacto, "
                  "la producción CAE (menos cosecha, menos pesca) y la inflación "
                  "SUBE (los alimentos escasean y se encarecen, el canal de m83) —es "
                  "estanflacionario—. Pero, y esta es la lección de política, "
                  "también es TRANSITORIO: cuando el clima se normaliza, la "
                  "agricultura se recupera, la pesca vuelve y los precios de "
                  "alimentos revierten. El modelo simula ese pulso —un golpe en el "
                  "trimestre del evento que se disipa después— y su calibración se "
                  "inspira en los dos episodios recientes: el Niño costero de 2017, "
                  "que inundó el norte y restó cerca de un punto al crecimiento del "
                  "primer trimestre con un blip de inflación de alimentos, y El Niño "
                  "de 2023, que junto con la crisis política y el ciclón Yaku "
                  "contribuyó a la recesión de ese año (−0.3%). La implicación para "
                  "el BCRP es delicada y conecta con m113: ante un shock de oferta "
                  "TRANSITORIO, el banco central debe 'mirar a través' del pico de "
                  "precios —no subir la tasa para combatir una inflación de "
                  "alimentos que se irá sola, porque hacerlo agravaría la caída de "
                  "la producción sin necesidad—. Solo debe reaccionar si el shock "
                  "amenaza con desanclar las expectativas (m40). El costo real de El "
                  "Niño no es la inflación pasajera, es la producción perdida y la "
                  "infraestructura destruida —y la respuesta correcta es fiscal "
                  "(reconstrucción, m106) y de prevención, no monetaria."),
        autores=("Estructura: shock de oferta transitorio (m11, m52) — decisión de "
                 "diseño del laboratorio; canal de alimentos: m83; anclaje y 'mirar "
                 "a través': m40, m113. Calibración DIDÁCTICA inspirada en El Niño "
                 "2017/2023 (no hay conector SENAMHI; no son datos de un índice "
                 "climático oficial)."),
        supuestos=[
            "El shock climático se MODELA como un shock de oferta transitorio (m11/m52): decisión de diseño, no una serie climática (SENAMHI no está conectada).",
            "La calibración (intensidad, ~0.9pp de inflación por pp de producto) es DIDÁCTICA, inspirada en la magnitud de El Niño 2017/2023 — no una estimación oficial.",
            "La reversión supone que el ancla del BCRP aguanta (m40): un shock climático que desanclara expectativas (o uno permanente, cambio climático) tendría efectos más persistentes.",
        ],
        ecuaciones=[
            Ecuacion("El\\;Niño: \\;producto\\downarrow \\;\\wedge\\; \\pi_{alimentos}\\uparrow", "shock de oferta (m11)",
                     "producción y precios se mueven en direcciones opuestas: la firma del shock de oferta "
                     "(estanflación) — distinto de un shock de demanda, que los mueve juntos."),
            Ecuacion("transitorio: \\;(g,\\pi) \\to (g_0, \\pi_0) \\;al\\;disiparse", "es pasajero",
                     "cuando el clima normaliza, la producción agrícola se recupera y la inflación de "
                     "alimentos revierte: el golpe es temporal si el ancla aguanta (m40)."),
            Ecuacion("respuesta\\;BCRP: \\;mirar\\;a\\;través \\;(no\\;subir\\;la\\;tasa)", "la lección de política",
                     "ante un shock de oferta transitorio, subir la tasa agravaría la caída sin frenar una "
                     "inflación que se irá sola: el BCRP mira a través (m113); la respuesta es fiscal (m106)."),
        ],
        intuicion=("La imagen es una V en la producción y una joroba en la "
                   "inflación, ambas breves: El Niño golpea, la economía se hunde un "
                   "trimestre y los precios de la papa y el limón se disparan en los "
                   "titulares, y luego —si no hay un evento extraordinario— todo "
                   "vuelve a su cauce. Entender que es un shock de OFERTA y "
                   "TRANSITORIO es lo que separa una buena respuesta de política de "
                   "una mala. La tentación populista es 'combatir la inflación' de "
                   "alimentos con controles de precios (que crean desabasto, m01) o "
                   "exigir al banco central que suba la tasa (que hunde más la "
                   "producción sin traer de vuelta las cosechas). La respuesta "
                   "correcta es otra: el BCRP mira a través del pico (m113), y el "
                   "Estado actúa por el lado fiscal —ayuda a los damnificados, "
                   "reconstruye la infraestructura (m106), y sobre todo PREVIENE con "
                   "obras de mitigación—. Porque la mala noticia de fondo es que "
                   "para el Perú El Niño no es un cisne negro sino un evento "
                   "recurrente, y el cambio climático amenaza con hacerlo más "
                   "frecuente e intenso —acercándolo a un shock permanente, que ya "
                   "no revertiría solo—. La resiliencia climática (infraestructura, "
                   "diversificación agrícola, alerta temprana) es, en el fondo, "
                   "parte de la misma agenda de desarrollo que la diversificación de "
                   "m112: reducir la exposición de un país pequeño a shocks que no "
                   "controla."),
        equilibrio=("El sistema tiene un equilibrio de largo plazo en la tendencia "
                    "(g₀, π₀); El Niño lo desplaza temporalmente (producción abajo, "
                    "inflación arriba) y revierte al disiparse, siempre que el ancla "
                    "aguante (m40). Un shock permanente (cambio climático) movería el "
                    "propio equilibrio."),
        limitaciones=[
            "No usa datos climáticos: el shock es una decisión de diseño (m11/m52) calibrada didácticamente; un modelo serio usaría un índice de El Niño (SENAMHI/ENFEN) y estimaría el impacto — pendiente de ese conector.",
            "Agregado y estilizado: no distingue regiones (el norte se inunda, el sur se seca) ni sectores (agricultura vs pesca vs infraestructura), que tienen dinámicas distintas.",
            "Supone reversión: válido para El Niño recurrente con ancla creíble; el cambio climático (shocks más frecuentes/intensos, o permanentes) rompería el supuesto de transitoriedad.",
        ],
        evolucion=("Aplica el shock de oferta de m11/m52 y el canal de alimentos de "
                   "m83 a la vulnerabilidad climática peruana, con la lección de "
                   "'mirar a través' de m113 (anclaje, m40). Junto con el enclave de "
                   "m112, completa los riesgos estructurales del Perú (externos, "
                   "sectoriales, climáticos) que la síntesis final (m115) integra en "
                   "un solo retrato — y que motivan la agenda de resiliencia y "
                   "diversificación."),
    ),
    escenarios=[
        Escenario("nino_severo", "El Niño extraordinario (2017 costero, 2023)",
                  {"intensidad": 3.0, "persistencia": 0.6},
                  "un evento severo hunde la producción y dispara la inflación de "
                  "alimentos en el impacto, y tarda más en disiparse: el patrón de "
                  "2017 (inundaciones del norte) y 2023 (con crisis política). El "
                  "costo real es la producción y la infraestructura perdidas.",
                  cadena=["El Niño extraordinario (mar caliente)", "inundaciones norte, sequía sur: agricultura y pesca caen",
                          "producción ↓ y alimentos ↑ (estanflación, m11/m83)", "el golpe es fuerte y tarda en disiparse",
                          "respuesta: fiscal (reconstrucción m106), no subir la tasa"]),
        Escenario("nino_leve", "un evento leve",
                  {"intensidad": 1.0, "persistencia": 0.4},
                  "un El Niño débil apenas mella la producción y el blip de "
                  "inflación se disipa rápido: el BCRP mira a través sin problema "
                  "(m113) y la economía casi ni lo nota.",
                  cadena=["El Niño débil", "golpe menor a agricultura y pesca",
                          "producción y alimentos se mueven poco y brevemente", "el BCRP mira a través (m113) — no reacciona",
                          "la economía absorbe el shock sin secuelas"]),
        Escenario("sobre_reaccion", "el error: subir la tasa ante el pico",
                  {"intensidad": 2.0, "persistencia": 0.5},
                  "el escenario a EVITAR: si el BCRP subiera la tasa para combatir "
                  "una inflación de alimentos que es transitoria, agravaría la caída "
                  "de la producción sin frenar el shock — la respuesta correcta es "
                  "mirar a través (m113) y actuar por el lado fiscal (m106).",
                  cadena=["shock de oferta: inflación de alimentos sube (transitoria)", "TENTACIÓN: subir la tasa para 'combatir la inflación'",
                          "pero eso hunde más la producción (ya caída)", "sin frenar un shock que se irá solo (m113)",
                          "la respuesta correcta: mirar a través + fiscal (m106)"]),
    ],
    verificaciones=[
        Verificacion("El Niño es un shock de oferta (estanflacionario, m11)", _v_estanflacionario),
        Verificacion("el shock es transitorio (revierte, m40)", _v_transitorio),
        Verificacion("a mayor severidad, mayor golpe (exposición estructural)", _v_intensidad_escala),
        Verificacion("el ancla contiene el pico (mirar a través, m113)", _v_ancla_contiene),
    ],
    notas="El Niño = shock de oferta transitorio (m11/m52): producción ↓ e inflación de alimentos ↑ (m83), reversible con ancla (m40). El BCRP debe MIRAR A TRAVÉS (m113); la respuesta es fiscal (m106). Calibración didáctica (sin conector SENAMHI).",
)
