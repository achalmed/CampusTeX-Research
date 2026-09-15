"""simuladores/macro/modelos/nivel_12/m115_modelo_peru.py — modelo macroeconómico simplificado del Perú (nivel 12).

EL CIERRE del currículo macro: un modelo estilizado que integra TODO el nivel
12 —y buena parte del currículo— en un solo retrato de la economía peruana.
Toma las relaciones calibradas de los modelos anteriores y las conecta para que
un shock se propague por TODOS los canales a la vez:
  • canal externo real (m103/m105/m109/m110): el precio del cobre mueve el
    crecimiento y, más aún, el INGRESO (efecto términos de intercambio, m105);
  • canal externo financiero (m104/m111): la FED y el riesgo mueven el sol;
  • canal monetario (m99/m100/m113): el ancla del BCRP mantiene la inflación
    estable — el passthrough del sol es casi nulo;
  • canal fiscal (m106/m107/m108): el impulso fiscal empuja el crecimiento con
    un multiplicador modesto (~0.7) y mueve la deuda (aritmética de m64);
  • estructura (m112): el peso del cobre hace al Perú dependiente de commodities.
El usuario aplica un shock (cobre, FED, fiscal) y ve responder al Perú entero:
crecimiento, ingreso, inflación, sol y deuda. La lección que emerge: el Perú es
una economía ABIERTA y dependiente de commodities, con un ANCLA monetaria sólida
y DISCIPLINA fiscal que le dan resiliencia — pero cuya prosperidad sigue atada
al mundo, y cuyo reto pendiente es DIVERSIFICAR (m112).

Procedencia: DECISIÓN DE DISEÑO — modelo de síntesis. Las elasticidades son
calibración DIDÁCTICA que resume los hallazgos de m97-m114 (p.ej. cobre→
crecimiento de m103, multiplicador de m107, passthrough de m113): reproducen
los HECHOS ESTILIZADOS cualitativos, no son una estimación estructural conjunta.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

# Calibración didáctica (síntesis de m97-m114). Coeficientes redondos que
# reproducen los signos y órdenes de magnitud de los modelos del nivel.
_G0 = 4.0        # crecimiento tendencial (%) — m97 (~4.5%)
_PI0 = 2.0       # inflación meta (%) — m40/m99
_B_COBRE = 0.09  # 1pp Δcobre → 0.09pp crecimiento — m103 (pendiente OLS)
_INGRESO_TI = 0.06   # efecto términos de intercambio sobre el ingreso — m105
_MULT = 0.7      # multiplicador fiscal — m107 (rango identificado)
_PASS = 0.05     # passthrough tipo de cambio → inflación (≈0) — m113
_SOL_COBRE = -0.03   # cobre↑ → sol se aprecia (débil) — m104
_SOL_FED = 0.6       # FED↑ → sol se deprecia (fuerte) — m111


def _responder(cobre, fed, fiscal):
    """La economía peruana estilizada responde a tres shocks (síntesis del nivel)."""
    g = _G0 + _B_COBRE * cobre + _MULT * fiscal              # crecimiento (m103, m107)
    ingreso = g + _INGRESO_TI * cobre                         # ingreso: + efecto TdI (m105)
    dsol = _SOL_COBRE * cobre + _SOL_FED * fed                # tipo de cambio (m104, m111)
    inflacion = _PI0 + _PASS * dsol                           # inflación anclada (m113)
    # deuda/PBI: cae con el crecimiento (denominador, m64/m108), sube con déficit
    delta_deuda = -0.3 * (g - _G0) + 0.5 * fiscal             # Δb aproximado (m64)
    return g, ingreso, inflacion, dsol, delta_deuda


def _curvas(p):
    cobre = np.linspace(-40, 40, 81)                          # barrido del shock de cobre
    g, ing, infl, dsol, _ = _responder(cobre, p["shock_fed"], p["impulso_fiscal"])
    c0 = p["shock_cobre"]
    g0, ing0, infl0, dsol0, _ = _responder(c0, p["shock_fed"], p["impulso_fiscal"])
    return {"lineas": {"crecimiento (%)": (cobre, g, config.AZUL2),
                       "ingreso nacional (%)": (cobre, ing, config.DORADO),
                       "inflación (%)": (cobre, infl, config.ROJO),
                       "depreciación del sol (%)": (cobre, dsol, config.VERDE)},
            "puntos": [(float(c0), float(g0), f"shock cobre {c0:+.0f}%: crecimiento {g0:+.1f}%"),
                       (float(c0), float(ing0), f"ingreso {ing0:+.1f}% (efecto TdI, m105)")],
            "anotacion": ("modelo simplificado del Perú (síntesis m97-m114)\n"
                          "cobre↑ → crecimiento e INGRESO ↑ (m103/m105), sol se aprecia (m104)\n"
                          "inflación ANCLADA (m113): el sol se mueve sin contaminar precios")}


def _resultados(p):
    g, ing, infl, dsol, ddeuda = _responder(p["shock_cobre"], p["shock_fed"], p["impulso_fiscal"])
    return {"crecimiento (%)": float(g),
            "ingreso nacional (%)": float(ing),
            "inflación (%)": float(infl),
            "depreciación del sol (%)": float(dsol),
            "cambio en deuda/PBI (pp)": float(ddeuda),
            "brecha ingreso-crecimiento (pp, efecto TdI)": float(ing - g)}


def _ecuaciones_calibradas(p):
    g, ing, infl, dsol, ddeuda = _responder(p["shock_cobre"], p["shock_fed"], p["impulso_fiscal"])
    return [f"$g = {_G0:.0f} + {_B_COBRE:.2f}\\,\\Delta cobre + {_MULT:.1f}\\,fiscal = {g:.1f}\\%$ (m103, m107)",
            f"$\\pi = {_PI0:.0f} + {_PASS:.2f}\\,\\Delta e = {infl:.1f}\\%$ (anclada, m113); sol $= {dsol:+.1f}\\%$ (m104, m111)"]


_P0 = {"shock_cobre": 0.0, "shock_fed": 0.0, "impulso_fiscal": 0.0}


def _v_cobre_crecimiento_ingreso():
    g_boom, ing_boom, _, _, _ = _responder(30, 0, 0)
    g_base, ing_base, _, _, _ = _responder(0, 0, 0)
    return g_boom > g_base and (ing_boom - g_boom) > (ing_base - g_base), \
        (f"un boom del cobre (+30%) sube el crecimiento ({g_base:.1f}→{g_boom:.1f}%) y AÚN MÁS el ingreso "
         f"(brecha ingreso-PBI {ing_boom-g_boom:+.1f}pp): el canal de m103 más el efecto términos de intercambio de m105")


def _v_ancla_inflacion():
    _, _, infl_boom, _, _ = _responder(40, 0, 0)
    _, _, infl_fed, dsol_fed, _ = _responder(0, 3, 0)
    return abs(infl_boom - _PI0) < 0.5 and abs(infl_fed - _PI0) < 0.5 and abs(dsol_fed) > 1, \
        (f"el ancla del BCRP domina: ni un boom del cobre ni un alza de la FED (que deprecia el sol {dsol_fed:+.1f}%) "
         f"mueven la inflación (queda en {infl_fed:.1f}%) — passthrough ≈0 (m113): el sol flota sin contaminar precios")


def _v_fed_deprecia_sol():
    _, _, _, dsol_fed, _ = _responder(0, 3, 0)
    _, _, _, dsol_cobre, _ = _responder(30, 0, 0)
    return dsol_fed > 1 and dsol_cobre < 0, \
        (f"el sol es un precio financiero: la FED lo deprecia fuerte (+3pp FED → sol {dsol_fed:+.1f}%, m111) y el "
         f"cobre lo aprecia poco ({dsol_cobre:+.1f}%, m104) — el canal financiero pesa más que el comercial en el corto plazo")


def _v_disciplina_deuda():
    _, _, _, _, dd_crece = _responder(30, 0, 0)          # boom sin gastarlo: deuda baja
    _, _, _, _, dd_gasta = _responder(0, 0, 5)           # impulso fiscal: deuda sube
    return dd_crece < 0 and dd_gasta > 0, \
        (f"la aritmética de m64/m108: crecer sin gastar el boom BAJA la deuda ({dd_crece:+.1f}pp), gastar la SUBE "
         f"({dd_gasta:+.1f}pp) — ahorrar en la bonanza (disciplina, m108) es lo que dio al Perú espacio para el COVID")


MODELO = Modelo(
    id="m115", nivel=12,
    nombre="Modelo macroeconómico simplificado del Perú (síntesis)",
    xlabel="Shock del precio del cobre (%)", ylabel="Respuesta (%)",
    parametros=[
        Parametro("shock_cobre", _P0["shock_cobre"], -40, 40, 5, "Shock del precio del cobre (%)",
                  grupo="shock externo", definicion="el pulso del mundo sobre el Perú (m103/m105/m110)"),
        Parametro("shock_fed", _P0["shock_fed"], -3, 3, 0.5, "Shock de la tasa de la FED (pp)",
                  grupo="shock externo", definicion="el ciclo financiero global (m111): + deprecia el sol"),
        Parametro("impulso_fiscal", _P0["impulso_fiscal"], -3, 5, 1, "Impulso fiscal (pp del PBI)",
                  grupo="política", definicion="gasto público extra: empuja el crecimiento (m107) y la deuda (m108)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si tuvieras que explicar la macroeconomía del Perú en un solo modelo, ¿cuál sería — y qué shocks lo mueven?",
        variables=[("shock de cobre", "el pulso del mundo (m103/m105/m110)"),
                   ("shock de la FED", "el ciclo financiero global (m111)"),
                   ("impulso fiscal", "la política doméstica (m107/m108)"),
                   ("g, ingreso, π, sol, deuda", "las respuestas del Perú entero")],
        derivacion=["g = g_0 + \\beta_{cobre}\\Delta cobre + mult\\cdot fiscal \\;(m103, m107)",
                    "ingreso = g + efecto\\;TdI \\;(m105); \\;\\; \\Delta e = f(cobre, FED) \\;(m104, m111)",
                    "\\pi = \\pi_0 + passthrough\\cdot\\Delta e \\approx \\pi_0 \\;(anclada, m113)",
                    "\\Delta b = -(g-g_0)\\cdot\\theta + fiscal \\;(aritmética\\;de\\;m64/m108)"],
        contexto=("Este es el modelo que cierra el currículo macro: un retrato "
                  "estilizado del Perú que junta, en un solo sistema, todo lo que el "
                  "nivel 12 descubrió con datos y todo lo que los once niveles "
                  "previos construyeron en teoría. La idea es simple y poderosa: la "
                  "economía peruana puede entenderse como el cruce de cinco canales, "
                  "cada uno estudiado en su propio modelo, ahora conectados. El "
                  "canal externo REAL (m103, m105, m109, m110): el precio del cobre "
                  "—y con él los términos de intercambio— mueve el crecimiento y, "
                  "más aún, el INGRESO nacional, porque una mejora de precios es un "
                  "windfall que eleva el poder de compra por encima de la producción "
                  "(la lección de m105). El canal externo FINANCIERO (m104, m111): "
                  "la tasa de la Reserva Federal y el riesgo país mueven el tipo de "
                  "cambio, que es un precio de activo gobernado por los flujos de "
                  "capital más que por el comercio. El canal MONETARIO (m99, m100, "
                  "m113): el ancla de credibilidad del BCRP mantiene la inflación "
                  "cerca de la meta pase lo que pase con el sol —el passthrough es "
                  "casi nulo—, de modo que el tipo de cambio puede flotar y absorber "
                  "shocks sin contaminar los precios. El canal FISCAL (m106, m107, "
                  "m108): el gasto público empuja el crecimiento con un multiplicador "
                  "modesto (la economía abierta filtra parte por importaciones) y "
                  "mueve la deuda según la aritmética de m64, donde crecer y ahorrar "
                  "en los buenos años reduce la deuda y da espacio para las crisis. "
                  "Y la ESTRUCTURA (m112): el peso desproporcionado del cobre hace "
                  "que el destino de corto plazo del país dependa de un puñado de "
                  "precios que no controla. Al mover los tres shocks —cobre, FED, "
                  "fiscal— y ver responder al Perú entero, emerge el diagnóstico de "
                  "fondo: el Perú es una economía pequeña, abierta y dependiente de "
                  "commodities, expuesta al ciclo mundial; pero ha construido dos "
                  "defensas notables —un ancla monetaria creíble (que le da "
                  "estabilidad de precios y una moneda que puede flotar) y "
                  "disciplina fiscal (que le da baja deuda y espacio de maniobra)—, "
                  "y esas dos fortalezas explican por qué ha crecido con estabilidad "
                  "macro pese a los vaivenes. El reto pendiente, que ningún ancla ni "
                  "disciplina resuelve, es el estructural: DIVERSIFICAR la economía "
                  "(m112) para depender menos del cobre, generar empleo de calidad "
                  "y convertir el crecimiento en desarrollo. Ese es el hilo que "
                  "conecta este modelo con el futuro —y con la micro, la "
                  "econometría y la economía del desarrollo que vienen después—."),
        autores=("Síntesis del laboratorio (decisión de diseño): integra las "
                 "relaciones calibradas de m97-m114 —cobre→crecimiento (m103), "
                 "efecto términos de intercambio (m105), multiplicador (m107), "
                 "passthrough (m113), aritmética de la deuda (m64/m108), trilema "
                 "(m50/m111)— en un modelo estilizado. Calibración didáctica, no "
                 "estimación estructural conjunta."),
        supuestos=[
            "Es un modelo de SÍNTESIS estilizado: las elasticidades son calibración didáctica que resume m97-m114 (signos y órdenes de magnitud), NO una estimación econométrica conjunta del sistema.",
            "Relaciones lineales y estáticas: captura la dirección y el orden relativo de los efectos (comparativa estática), no dinámicas, rezagos ni no-linealidades (que sí están en los modelos individuales).",
            "El ancla monetaria (passthrough ≈0) y la disciplina fiscal se toman como rasgos vigentes del Perú (m99, m108): un cambio de régimen (dominancia fiscal, m35; desanclaje) rompería el modelo — como en los países de m96.",
        ],
        ecuaciones=[
            Ecuacion("g = g_0 + \\beta_{cobre}\\,\\Delta cobre + mult\\cdot fiscal", "el crecimiento (m103, m107)",
                     "el crecimiento peruano responde al cobre (canal externo, m103) y al impulso fiscal "
                     "(multiplicador modesto, m107): el mundo y la política, combinados."),
            Ecuacion("ingreso = g + efecto\\;TdI; \\quad \\Delta e = f(cobre, FED)", "ingreso y sol (m105, m104/m111)",
                     "el ingreso supera al crecimiento cuando el cobre sube (windfall de términos de "
                     "intercambio, m105); el sol lo mueven el cobre (poco) y la FED (mucho) — precio de activo."),
            Ecuacion("\\pi \\approx \\pi_0 \\;(passthrough\\approx0); \\quad \\Delta b = -(g-g_0)\\theta + fiscal", "ancla y deuda (m113, m64)",
                     "la inflación queda anclada pase lo que pase con el sol (m113); la deuda cae si se crece "
                     "y sube si se gasta (aritmética de m64/m108) — las dos defensas del Perú."),
        ],
        intuicion=("La imagen final del laboratorio es este tablero: subes el precio "
                   "del cobre y ves al Perú entero iluminarse —el crecimiento sube, "
                   "el ingreso sube aún más, el sol se fortalece un poco— mientras la "
                   "inflación no se inmuta, firme en su meta. Subes la tasa de la FED "
                   "y el sol se debilita, pero la inflación sigue quieta. Metes un "
                   "impulso fiscal y el crecimiento reacciona algo, pero la deuda "
                   "sube. En ese pequeño tablero está la macroeconomía de un país "
                   "emergente bien manejado: profundamente expuesto al mundo, pero "
                   "protegido por instituciones —un banco central creíble y un fisco "
                   "disciplinado— que convierten shocks que en otros países serían "
                   "crisis (m96) en fluctuaciones administrables. Es también un mapa "
                   "de lo que falta: el modelo no tiene una palanca de "
                   "'productividad' ni de 'diversificación' que el gobierno pueda "
                   "mover a voluntad, porque esas no se decretan —se construyen en "
                   "décadas, con educación, instituciones e inversión (m26, m30, "
                   "m90)—. El cobre, la FED y el gasto son los shocks del trimestre; "
                   "la diversificación y la productividad son el proyecto de "
                   "generación. Y ahí, exactamente, el laboratorio de macro entrega "
                   "la posta: entender cómo funciona la economía peruana en su "
                   "conjunto es el punto de partida para las preguntas que siguen "
                   "—cómo se comportan los mercados y las personas (micro), cómo se "
                   "mide y se prueba una hipótesis con datos (econometría), y cómo se "
                   "logra que un país deje de depender de un mineral (desarrollo)—."),
        equilibrio=("El modelo tiene un equilibrio de referencia (g₀, π₀, deuda "
                    "estable) del que los shocks lo desvían: un boom de cobre lo "
                    "lleva a crecimiento e ingreso altos con inflación anclada; una "
                    "FED restrictiva deprecia el sol sin mover la inflación; el "
                    "impulso fiscal empuja el crecimiento a costa de deuda. Las dos "
                    "anclas (monetaria y fiscal) mantienen el sistema estable — su "
                    "ruptura sería la crisis de m96."),
        limitaciones=[
            "Síntesis estilizada, no estructural: reproduce los hechos cualitativos de m97-m114, no predice magnitudes; cada canal está mejor modelado en su propio archivo.",
            "Estático y lineal: sin dinámicas, rezagos ni umbrales (que sí aparecen en los modelos individuales, p.ej. la no-linealidad de la deuda en m76/m108).",
            "Toma las instituciones como dadas: el ancla (m40) y la disciplina (m108) son supuestos vigentes; el modelo no endogeniza su posible ruptura (dominancia fiscal m35, populismo) — que es justo el riesgo a vigilar.",
        ],
        evolucion=("CIERRA el currículo macro integrando el nivel 12 (y el "
                   "currículo) en un modelo del Perú. De aquí el laboratorio se "
                   "extiende, según la directiva de Edison, a MICROECONOMÍA (cómo "
                   "deciden hogares y empresas), ECONOMETRÍA (cómo se prueban estas "
                   "hipótesis con datos, sin duplicar el pipeline de datafw) y "
                   "MATEMÁTICA para economistas — con la misma filosofía de ficha "
                   "histórica, escenarios y verificaciones. El reto de "
                   "diversificación y productividad que este modelo deja abierto es "
                   "el puente natural hacia la economía del desarrollo."),
    ),
    escenarios=[
        Escenario("superciclo", "un boom del cobre (superciclo)",
                  {"shock_cobre": 30.0, "shock_fed": 0.0, "impulso_fiscal": 0.0},
                  "el cobre sube 30%: el crecimiento y sobre todo el INGRESO se "
                  "disparan (m103/m105), el sol se aprecia un poco (m104) y la "
                  "inflación no se mueve (m113). El superciclo 2004-2013 en un "
                  "vistazo — prosperidad importada, pero real.",
                  cadena=["el cobre sube 30% (demanda mundial, m88)", "crecimiento e INGRESO suben (m103, windfall m105)",
                          "el sol se aprecia levemente (m104)", "la inflación sigue anclada (m113)",
                          "prosperidad — pero dependiente del mundo (m112)"]),
        Escenario("giro_fed", "la FED endurece (2022-2023)",
                  {"shock_cobre": 0.0, "shock_fed": 3.0, "impulso_fiscal": 0.0},
                  "la FED sube 3pp: el sol se deprecia (m111), pero la inflación "
                  "sigue anclada (m113) — el sol absorbe el shock sin contaminar los "
                  "precios. La flotación (m102) más el ancla (m40) hacen su trabajo.",
                  cadena=["la FED sube 3pp (ciclo financiero global)", "el capital sale, el sol se deprecia (m111)",
                          "pero el passthrough es ≈0 (m113)", "la inflación no se mueve — el sol absorbe el golpe",
                          "flotación (m102) + ancla (m40) = resiliencia"]),
        Escenario("estimulo", "un impulso fiscal (estímulo)",
                  {"shock_cobre": 0.0, "shock_fed": 0.0, "impulso_fiscal": 4.0},
                  "un estímulo fiscal de 4pp empuja el crecimiento —con multiplicador "
                  "modesto (m107, la economía abierta filtra)— pero sube la deuda "
                  "(m108). Útil en recesión, si hay espacio fiscal (el que la "
                  "disciplina del boom construyó).",
                  cadena=["impulso fiscal de 4pp del PBI (estímulo)", "el crecimiento sube (multiplicador ~0.7, m107)",
                          "modesto: la economía abierta filtra (m43)", "la deuda sube (m108) — usa el espacio fiscal",
                          "sostenible solo si se ahorró antes (disciplina, m108)"]),
        Escenario("tormenta_perfecta", "shock adverso combinado",
                  {"shock_cobre": -30.0, "shock_fed": 2.0, "impulso_fiscal": 2.0},
                  "lo peor junto: el cobre cae 30% Y la FED sube — el crecimiento y "
                  "el ingreso caen, el sol se deprecia. Pero la inflación aguanta "
                  "(m113) y el Perú responde con fiscal (m107) desde su espacio de "
                  "deuda (m108): resiliencia institucional ante un shock externo.",
                  cadena=["cobre −30% + FED +2pp (shock externo doble, m110/m111)", "crecimiento e ingreso caen, el sol se deprecia",
                          "PERO la inflación aguanta (ancla, m113)", "el Perú responde con fiscal (m107) desde su espacio (m108)",
                          "las instituciones convierten la crisis en fluctuación (vs m96)"]),
    ],
    verificaciones=[
        Verificacion("cobre↑ → crecimiento e INGRESO ↑ (m103, m105)", _v_cobre_crecimiento_ingreso),
        Verificacion("la inflación queda anclada pase lo que pase (m113)", _v_ancla_inflacion),
        Verificacion("el sol es financiero: la FED lo mueve más (m111 vs m104)", _v_fed_deprecia_sol),
        Verificacion("disciplina: crecer baja la deuda, gastar la sube (m64/m108)", _v_disciplina_deuda),
    ],
    notas="EL CIERRE del currículo macro: el Perú en un modelo. Economía abierta y dependiente de commodities (m103/m110), con ancla monetaria (m113) y disciplina fiscal (m108) que dan resiliencia; el reto pendiente es diversificar (m112). Puente a micro/econometría/desarrollo.",
)
