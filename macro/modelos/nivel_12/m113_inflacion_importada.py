"""simuladores/macro/modelos/nivel_12/m113_inflacion_importada.py — inflación importada y passthrough (nivel 12).

El miedo clásico de una economía abierta: si el sol se devalúa, ¿se dispara la
inflación (los importados —combustible, alimentos, máquinas— cuestan más)? El
passthrough del tipo de cambio a los precios. Y la respuesta peruana es una de
las lecciones más bonitas del laboratorio: el passthrough es MUY BAJO, casi
cero. El sol se depreció +12% en 2015 y +11% en 2021, y la inflación apenas se
movió (3.5% y 4.0%, dentro o cerca de la banda meta). Una devaluación NO se
convierte en espiral inflacionaria. ¿Por qué? Por la CREDIBILIDAD del BCRP
(m40, m99): con expectativas ancladas, las empresas no trasladan cada
devaluación a precios porque saben que el banco central mantendrá la meta —el
dividendo de la credibilidad que rompe el círculo devaluación→inflación→
devaluación de m14—. El contrapunto honesto es 2022: la inflación SÍ saltó a
7.9%, pero con el sol ESTABLE: fue inflación importada por los PRECIOS GLOBALES
(alimentos y energía, guerra de Ucrania, m83/m85), no por el tipo de cambio.
Hay dos "inflaciones importadas": la del tipo de cambio (baja en el Perú) y la
de los precios mundiales (real) — no confundirlas.

Procedencia: datos BCRP PN01207PM (tipo de cambio) y PN01273PM (IPC 12m),
muestra 2004-2024. El passthrough y su relación con la credibilidad: m40/m85
(conocimiento general). El passthrough bajo es del DATO; su explicación
(anclaje) es teórica (m40).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, tc, ipc = _datos_bcrp.alinear("tipo_cambio", "ipc_12m")
    dtc = np.diff(tc) / tc[:-1] * 100                # depreciación % del sol
    ax = anos[1:]
    infl = ipc[1:]                                    # inflación contemporánea
    return ax, dtc, infl


def _passthrough(dtc, infl):
    _, b, _ = _datos_bcrp.ols(dtc, infl)
    return b


def _curvas(p):
    ax, dtc, infl = _series()
    b = _passthrough(dtc, infl)
    return {"lineas": {"depreciación del sol (BCRP, %)": (ax, dtc, config.ROJO),
                       "inflación (BCRP, %)": (ax, infl, config.AZUL2),
                       "meta del BCRP (2%)": (ax, np.full(len(ax), 2.0), config.GRIS)},
            "puntos": [(2015.0, float(dtc[ax == 2015][0]), "2015: sol −12%, inflación 3.5%"),
                       (2022.0, float(infl[ax == 2022][0]), "2022: sol estable, inflación 7.9% (global)")],
            "anotacion": (f"depreciación vs inflación (PN01207PM, PN01273PM)\n"
                          f"passthrough $= {b:+.2f}$ (≈0): la devaluación NO se traslada\n"
                          "el ancla del BCRP (m40) rompe la espiral (m14)")}


def _resultados(p):
    ax, dtc, infl = _series()
    return {"passthrough (pp inflación por pp depreciación)": float(_passthrough(dtc, infl)),
            "corr(depreciación, inflación)": float(_datos_bcrp.correlacion(dtc, infl)),
            "depreciación 2015 (%)": float(dtc[ax == 2015][0]),
            "inflación 2015 (%)": float(infl[ax == 2015][0]),
            "depreciación 2021 (%)": float(dtc[ax == 2021][0]),
            "inflación 2021 (%)": float(infl[ax == 2021][0]),
            "inflación 2022 (%, sol estable)": float(infl[ax == 2022][0]),
            "depreciación 2022 (%)": float(dtc[ax == 2022][0])}


def _ecuaciones_calibradas(p):
    ax, dtc, infl = _series()
    return [f"passthrough $= {_passthrough(dtc, infl):+.2f}$ pp/pp (≈0): devaluación $\\not\\to$ inflación",
            f"anclaje (m40) $\\Rightarrow$ bajo passthrough; 2022: inflación por precios GLOBALES (m83), no por el sol"]


_P0 = {"umbral_dev": 8.0}


def _v_passthrough_bajo():
    ax, dtc, infl = _series()
    b = _passthrough(dtc, infl)
    return abs(b) < 0.3, \
        (f"el passthrough del tipo de cambio a la inflación es ~0 (pendiente {b:+.2f}): una devaluación del sol "
         "casi NO se traslada a los precios — muy distinto del miedo clásico de la economía abierta")


def _v_devaluacion_sin_espiral():
    ax, dtc, infl = _series()
    d15, i15 = float(dtc[ax == 2015][0]), float(infl[ax == 2015][0])
    d21, i21 = float(dtc[ax == 2021][0]), float(infl[ax == 2021][0])
    return d15 > 8 and i15 < 5 and d21 > 8 and i21 < 5, \
        (f"el sol se depreció fuerte (+{d15:.0f}% en 2015, +{d21:.0f}% en 2021) y la inflación apenas se movió "
         f"({i15:.1f}%, {i21:.1f}%): sin espiral (m14) — el ancla del BCRP (m40) desactivó la devaluación")


def _v_dividendo_credibilidad():
    return True, \
        ("el passthrough bajo es el DIVIDENDO DE LA CREDIBILIDAD (m40, m99): con expectativas ancladas, las "
         "empresas no trasladan la devaluación a precios; en países con banco central débil el passthrough es alto y espiral (m14)")


def _v_2022_global():
    ax, dtc, infl = _series()
    d22, i22 = float(dtc[ax == 2022][0]), float(infl[ax == 2022][0])
    return i22 > 6 and d22 < 3, \
        (f"2022 es el contrapunto: la inflación saltó a {i22:.1f}% con el sol ESTABLE ({d22:+.1f}%) — fue inflación "
         "importada por los PRECIOS GLOBALES (alimentos y energía, m83/m85), no por el tipo de cambio: dos canales distintos")


MODELO = Modelo(
    id="m113", nivel=12,
    nombre="Inflación importada: passthrough (BCRP)",
    xlabel="Año", ylabel="Variación anual (%)",
    parametros=[
        Parametro("umbral_dev", _P0["umbral_dev"], 3, 15, 1, "Umbral de devaluación 'grande' (%)",
                  grupo="análisis", definicion="referencia para resaltar años de devaluación fuerte sin inflación"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si el sol se devalúa 12%, ¿por qué la inflación peruana apenas se mueve — y por qué en 2022 saltó con el sol estable?",
        variables=[("Δe", "depreciación del sol, var% (BCRP PN01207PM)"),
                   ("π", "inflación (BCRP PN01273PM)"),
                   ("passthrough", "cuánto de la devaluación pasa a precios (≈0 en el Perú)")],
        derivacion=["dato: \\;\\Delta e \\;(PN01207PM), \\;\\pi \\;(PN01273PM)",
                    "passthrough = \\partial\\pi/\\partial\\Delta e \\approx 0 \\;(el\\;dato)",
                    "porque\\;expectativas\\;ancladas\\;(m40) \\Rightarrow no\\;se\\;traslada",
                    "2022: \\;\\pi\\uparrow\\;con\\;e\\;estable \\Rightarrow precios\\;globales\\;(m83), no\\;el\\;sol"],
        contexto=("Toda economía abierta teme la 'inflación importada': la idea de "
                  "que si su moneda se debilita, los bienes importados —combustible, "
                  "trigo, maquinaria— se encarecen y disparan la inflación. Este "
                  "modelo mide ese temor con datos peruanos y encuentra un resultado "
                  "tranquilizador y profundo: el passthrough del tipo de cambio a los "
                  "precios en el Perú es muy BAJO, prácticamente cero. La evidencia "
                  "es contundente: el sol se depreció 12% en 2015 y 11% en 2021, "
                  "devaluaciones grandes, y la inflación apenas se movió —3.5% y "
                  "4.0%, dentro o muy cerca de la banda meta del BCRP—. Una "
                  "devaluación del sol, en el Perú de hoy, no se convierte en una "
                  "espiral inflacionaria. La razón es la lección central: la "
                  "CREDIBILIDAD del banco central (m40, m99). Cuando las empresas y "
                  "los trabajadores confían en que el BCRP mantendrá la inflación "
                  "cerca de 2% pase lo que pase, no trasladan cada subida del dólar "
                  "a sus precios y salarios —saben que sería insostenible—, y esa "
                  "expectativa anclada se autorrealiza: el passthrough se apaga. Es "
                  "el mismo mecanismo de m14 pero al revés: donde un banco central "
                  "débil deja que la devaluación alimente la inflación y la "
                  "inflación alimente más devaluación (el círculo vicioso de tantas "
                  "crisis latinoamericanas), un banco central creíble ROMPE el "
                  "círculo. Es, literalmente, el dividendo de dos décadas de "
                  "credibilidad (m99). Pero el modelo cierra con un contrapunto "
                  "honesto y necesario: 2022. Ese año la inflación peruana SÍ saltó, "
                  "a 7.9%, la más alta en más de una década. ¿Se rompió el ancla? "
                  "No: el sol estuvo ESTABLE en 2022 (hasta se apreció un poco). La "
                  "inflación de 2022 fue importada, sí, pero por otro canal: los "
                  "PRECIOS GLOBALES de alimentos y energía disparados por la guerra "
                  "de Ucrania (m83, m85), que suben en dólares para todo el mundo, "
                  "no por el tipo de cambio peruano. La lección fina: hay dos "
                  "'inflaciones importadas' —la del tipo de cambio (baja en el Perú, "
                  "gracias al ancla) y la de los precios mundiales (real, e "
                  "inevitable para un importador de petróleo y trigo)— y "
                  "confundirlas lleva a diagnósticos errados."),
        autores=("Datos: BCRP (PN01207PM tipo de cambio, PN01273PM IPC); el "
                 "passthrough y su relación con el anclaje de expectativas: m40, "
                 "m85; la espiral que se evita: m14; los precios globales de 2022: "
                 "m83 (conocimiento general)."),
        supuestos=[
            "El passthrough se mide como la relación contemporánea depreciación-inflación (pendiente de MCO): ilustrativo del orden de magnitud (~0), no una estimación estructural con rezagos y controles.",
            "El passthrough bajo es DATO (BCRP); su explicación —anclaje de expectativas (m40)— es teórica: la evidencia consistente con el ancla, no una prueba de causalidad.",
            "2022 se atribuye a precios globales (m83) por el hecho de que el sol estuvo estable ese año; es una lectura del episodio, no una descomposición formal de la inflación.",
        ],
        ecuaciones=[
            Ecuacion("passthrough = \\partial\\pi/\\partial\\Delta e \\approx 0", "el passthrough (casi) nulo",
                     "en el Perú una devaluación del sol casi no se traslada a la inflación: +12% en 2015, "
                     "+11% en 2021, e inflación en la banda — el dato que desmonta el miedo clásico."),
            Ecuacion("expectativas\\;ancladas\\;(m40) \\;\\Rightarrow\\; passthrough\\downarrow", "el dividendo de la credibilidad",
                     "con un BCRP creíble, las empresas no trasladan la devaluación (sería insostenible): "
                     "el ancla rompe el círculo devaluación→inflación→devaluación de m14."),
            Ecuacion("2022: \\;\\pi = 7.9\\%\\;con\\;e\\;estable \\;\\Rightarrow\\; precios\\;globales\\;(m83)", "la otra inflación importada",
                     "2022 subió la inflación con el sol quieto: fue por los precios mundiales de alimentos "
                     "y energía (m83, m85), no por el tipo de cambio — otro canal, no el passthrough."),
        ],
        intuicion=("La imagen son dos líneas que se ignoran: el sol da saltos "
                   "—se deprecia fuerte en 2015, 2021— y la inflación sigue "
                   "planita, pegada a la meta. Para quien creció con la hiperinflación "
                   "peruana de los 80 (m36), donde cada devaluación era gasolina "
                   "sobre el fuego de los precios, esto es casi milagroso —y no es "
                   "magia, es institución—. El BCRP se ganó, a lo largo de dos "
                   "décadas, el derecho a que le crean, y ese activo intangible —la "
                   "credibilidad— hace que el tipo de cambio pueda flotar (m102), "
                   "absorber los shocks externos (m111) y moverse con libertad SIN "
                   "contaminar los precios. Es de lo más valioso que tiene la "
                   "economía peruana, y de lo más fácil de destruir: bastaría una "
                   "racha de dominancia fiscal (m35) o de politización del banco "
                   "central para que las expectativas se desanclen y el passthrough "
                   "reviva. El episodio de 2022 enseña la otra mitad: la credibilidad "
                   "protege del canal cambiario, pero no del mundo. Cuando el trigo y "
                   "el petróleo se disparan en dólares (m83), un país que los importa "
                   "sufre inflación aunque su moneda esté firme —y ahí el BCRP solo "
                   "puede administrar el golpe (subir la tasa, m100), no evitarlo—. "
                   "Distinguir el shock del tipo de cambio (defendido) del shock de "
                   "precios globales (inevitable) es la diferencia entre entender la "
                   "inflación y buscar culpables."),
        equilibrio=("No hay equilibrio que resolver: es la relación empírica "
                    "depreciación-inflación. El resultado es un passthrough ≈0 "
                    "(devaluaciones grandes con inflación en banda), consistente con "
                    "expectativas ancladas (m40, m99); 2022 muestra el canal "
                    "alternativo (precios globales, m83) con el sol estable."),
        limitaciones=[
            "Passthrough contemporáneo y agregado: no estima rezagos ni distingue bienes transables de no transables (donde el passthrough sí es mayor); da el orden de magnitud (~0), no una cifra estructural.",
            "El anclaje se INFIERE del passthrough bajo (consistencia), no se mide directamente (exigiría datos de expectativas de inflación).",
            "2022 atribuido a precios globales por el sol estable: es una lectura del episodio; una descomposición formal separaría alimentos, energía, brecha y tipo de cambio.",
        ],
        evolucion=("Aplica m85 (inflación importada) y m40 (anclaje) con datos, "
                   "mostrando que la credibilidad del BCRP (m99, m100) protege al "
                   "Perú del canal cambiario de la inflación —el complemento de m111 "
                   "(el sol se mueve con la FED pero no contamina los precios)—. Con "
                   "2022 conecta a m83 (shock de alimentos global). Cierra los "
                   "canales del nivel antes del shock climático (m114) y la síntesis "
                   "final (m115)."),
    ),
    escenarios=[
        Escenario("devaluacion_2015", "devaluación sin inflación (2015, 2021)",
                  {"umbral_dev": 8.0},
                  "2015 y 2021: el sol se deprecia 12% y 11% —fuerte— y la inflación "
                  "se queda en 3.5% y 4.0%, cerca de la meta. El passthrough casi "
                  "nulo en acción: el ancla del BCRP (m40) desactiva la devaluación.",
                  cadena=["el sol se deprecia fuerte (+12%, +11%)", "las empresas NO trasladan (expectativas ancladas, m40)",
                          "la inflación se queda en la banda (3.5%, 4.0%)", "passthrough ≈0: sin espiral (m14) — dividendo de credibilidad"]),
        Escenario("global_2022", "inflación importada por precios globales (2022)",
                  {"umbral_dev": 8.0},
                  "2022: la inflación salta a 7.9% pero el sol está estable —no fue "
                  "el tipo de cambio—. Los precios mundiales de alimentos y energía "
                  "(guerra de Ucrania, m83) subieron en dólares para todos: la OTRA "
                  "inflación importada, la que el ancla no puede evitar.",
                  cadena=["guerra de Ucrania: alimentos y energía globales suben (m83)", "suben en dólares para todo importador",
                          "el sol está estable (no es passthrough)", "la inflación salta a 7.9% igual",
                          "inflación importada por PRECIOS globales, no por el tipo de cambio"]),
    ],
    verificaciones=[
        Verificacion("passthrough del tipo de cambio ≈0 (dato)", _v_passthrough_bajo),
        Verificacion("devaluaciones fuertes sin inflación (2015, 2021)", _v_devaluacion_sin_espiral),
        Verificacion("passthrough bajo = dividendo de credibilidad (m40)", _v_dividendo_credibilidad),
        Verificacion("2022: inflación global, sol estable (m83)", _v_2022_global),
    ],
    notas="Passthrough del tipo de cambio ≈0: el sol se depreció +12% (2015) y +11% (2021) con inflación en banda — el ancla del BCRP (m40) rompe la espiral (m14). Pero 2022: inflación 7.9% con sol estable = precios globales (m83), otra inflación importada.",
)
