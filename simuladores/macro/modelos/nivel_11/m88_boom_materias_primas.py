"""simuladores/macro/modelos/nivel_11/m88_boom_materias_primas.py — boom de materias primas (nivel 11).

La cara amable de un shock externo — y sus trampas. Un alza de los términos
de intercambio (precio de exportación / precio de importación) para un
exportador de commodities es un shock de INGRESO positivo: más divisas, más
fiscal, más crecimiento. Pero trae dos peligros:
  (1) ENFERMEDAD HOLANDESA (m46): la apreciación real encarece los transables
      NO mineros → desindustrialización;
  (2) PROCICLICIDAD FISCAL: gastar el boom como permanente → crisis cuando
      revierte (la falla de m68). La regla: ahorrar el transitorio (fondo de
      estabilización). Combina m43-m46 (externo), m105 (términos de
      intercambio) y m68 (fiscal contracíclica).

Procedencia: enfermedad holandesa (Corden-Neary — mención); términos de
intercambio y ciclo (m105); fondos de estabilización (Chile, Noruega —
menciones) — conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _efectos(p):
    ingreso = p["ti_shock"] * p["peso_export"] / 100      # shock de ingreso (% PIB)
    apreciacion = ingreso * p["holandesa"]                # apreciación real
    dano_transables = apreciacion * p["exposicion_t"]     # daño a no-mineros
    ahorrado = ingreso * p["ahorro"] / 100                # lo que va al fondo
    gastado = ingreso - ahorrado
    riesgo_reversion = gastado * (1 - p["ahorro"] / 100)  # exposición a la caída
    return dict(ingreso=ingreso, apreciacion=apreciacion, dano=dano_transables,
                ahorrado=ahorrado, gastado=gastado, riesgo=riesgo_reversion)


def _curvas(p):
    e = _efectos(p)
    cats = ["ingreso del\nboom (+)", "daño a transables\nno mineros (−)",
            "ahorrado\n(fondo)", "gastado\n(riesgo)"]
    vals = [e["ingreso"], -e["dano"], e["ahorrado"], e["gastado"]]
    cols = [config.VERDE, config.ROJO, config.AZUL, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"términos de intercambio {p['ti_shock']:+.0f}%, "
                          f"peso exportador {p['peso_export']:.0f}%\n"
                          f"ingreso {e['ingreso']:+.1f}% PIB · ahorro {p['ahorro']:.0f}%\n"
                          "gastar el boom como permanente = crisis al revertir (m68)")}


def _resultados(p):
    e = _efectos(p)
    return {"ingreso del boom (% PIB)": e["ingreso"],
            "apreciación real (m46)": e["apreciacion"],
            "daño a transables no mineros": e["dano"],
            "ahorrado en el fondo": e["ahorrado"],
            "gastado (procíclico)": e["gastado"],
            "exposición a la reversión": e["riesgo"]}


def _ecuaciones_calibradas(p):
    e = _efectos(p)
    return [f"ingreso $= {p['ti_shock']:+.0f}\\%\\times{p['peso_export']:.0f}\\% = {e['ingreso']:+.1f}$% PIB",
            f"ahorrado $= {p['ahorro']:.0f}\\%\\times ingreso = {e['ahorrado']:.1f}$; "
            f"gastado $= {e['gastado']:.1f}$"]


_P0 = {"ti_shock": 40.0, "peso_export": 25.0, "holandesa": 0.4, "exposicion_t": 0.5,
       "ahorro": 30.0}


def _v_ingreso_positivo():
    e = _efectos(_P0)
    return e["ingreso"] > 0, \
        (f"el boom es un shock de INGRESO (+{e['ingreso']:.1f}% PIB): a diferencia del "
         "petróleo para un importador (m82), aquí el país se enriquece")


def _v_enfermedad_holandesa():
    e = _efectos(_P0)
    return e["dano"] > 0, \
        (f"la apreciación real daña a los transables no mineros ({e['dano']:.1f}): la "
         "enfermedad holandesa — el boom minero puede desindustrializar (Corden-Neary)")


def _v_ahorrar_protege():
    riesgo_ahorra = _efectos(dict(_P0, ahorro=70.0))["riesgo"]
    riesgo_gasta = _efectos(dict(_P0, ahorro=10.0))["riesgo"]
    return riesgo_ahorra < riesgo_gasta, \
        (f"ahorrar el transitorio reduce la exposición a la reversión ({riesgo_gasta:.1f}→"
         f"{riesgo_ahorra:.1f}): el fondo de estabilización (Chile, m68) rompe la prociclicidad")


def _v_prociclicidad_peligrosa():
    e = _efectos(dict(_P0, ahorro=0.0))
    return e["riesgo"] > 0, \
        ("gastar TODO el boom (ahorro 0) maximiza la exposición: cuando el precio revierte "
         "(m89), el gasto no cae solo — hay que recortar en recesión (la trampa de m68)")


MODELO = Modelo(
    id="m88", nivel=11,
    nombre="Boom de materias primas",
    xlabel="", ylabel="Efectos del boom (% PIB)",
    parametros=[
        Parametro("ti_shock", _P0["ti_shock"], 0, 80, 10, "Alza de términos de intercambio (%)",
                  grupo="shock", definicion="precio de exportación / importación (m105)"),
        Parametro("ahorro", _P0["ahorro"], 0, 100, 10, "Fracción ahorrada del boom (%)",
                  grupo="política", definicion="al fondo de estabilización: la clave anti-prociclicidad (m68)"),
        Parametro("peso_export", _P0["peso_export"], 10, 40, 5, "Peso del sector exportador (% PIB)",
                  grupo="estructura", definicion="cobre+minería para Perú"),
        Parametro("holandesa", _P0["holandesa"], 0, 1, 0.1, "Intensidad de la apreciación (m46)",
                  grupo="riesgos"),
        Parametro("exposicion_t", _P0["exposicion_t"], 0, 1, 0.1, "Exposición de transables no mineros",
                  grupo="riesgos"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Un boom del cobre enriquece al país — ¿por qué puede terminar en crisis?",
        variables=[("ingreso", "el shock POSITIVo: más divisas, fiscal, crecimiento"),
                   ("enfermedad holandesa", "la trampa 1: apreciación que mata transables (m46)"),
                   ("ahorro", "la defensa: guardar el transitorio (m68)")],
        derivacion=["boom = \\Delta términos\\;de\\;intercambio > 0 \\;(m105)",
                    "ingreso\\uparrow, \\;pero\\;E\\;real\\uparrow \\Rightarrow transables\\;no\\;mineros\\downarrow\\;(m46)",
                    "gastar\\;como\\;permanente \\Rightarrow crisis\\;al\\;revertir\\;(m68)"],
        contexto=("Un boom de materias primas es la cara amable de un shock externo "
                  "— y una de las más traicioneras. Para un exportador como el "
                  "Perú, un alza del precio del cobre (o de los términos de "
                  "intercambio en general, m105) es un shock de ingreso positivo: "
                  "entran más divisas, la recaudación fiscal minera sube, el "
                  "crecimiento se acelera. Pero trae dos trampas históricas. La "
                  "primera es la 'enfermedad holandesa' (Corden-Neary, mención): el "
                  "boom aprecia el tipo de cambio real (m46), encareciendo a los "
                  "transables NO mineros (manufactura, agroexportación) y "
                  "desindustrializando la economía — el país se vuelve más "
                  "dependiente del recurso justo cuando más gana con él. La segunda "
                  "es la PROCICLICIDAD fiscal (la falla de m68): si el gobierno "
                  "trata el ingreso extraordinario como permanente y lo gasta, "
                  "cuando el precio revierte (m89) el gasto ya está comprometido y "
                  "hay que recortar en plena recesión — convirtiendo un boom en una "
                  "crisis. La defensa, que Chile y Noruega institucionalizaron "
                  "(menciones) y el Perú adoptó parcialmente, es un fondo de "
                  "estabilización: ahorrar el componente transitorio del boom para "
                  "gastarlo (o no recortarlo) cuando el ciclo revierta. El boom no "
                  "es el problema; gastarlo como si fuera para siempre, sí."),
        autores=("Enfermedad holandesa: Corden y Neary (1982 — mención); términos "
                 "de intercambio y ciclo: m105; fondos de estabilización: Chile "
                 "(cobre), Noruega (petróleo) — menciones; prociclicidad: m68."),
        supuestos=[
            "El componente del boom es parcialmente transitorio: ahorrar el transitorio y gastar el permanente es la regla óptima (permanent income, m03).",
            "La apreciación real daña a los transables proporcionalmente a su exposición: la enfermedad holandesa como parámetro.",
            "Sin reinversión productiva del boom: si el ingreso financia diversificación, la maldición se mitiga (matiz).",
        ],
        ecuaciones=[
            Ecuacion("ingreso = \\Delta TI \\times peso_{export}", "el shock de ingreso",
                     "a diferencia del importador (m82), el exportador se ENRIQUECE con el shock — "
                     "pero el ingreso extra trae apreciación y tentación de gasto."),
            Ecuacion("exposición = gastado \\times (1 - ahorro)", "el riesgo de la reversión",
                     "cuanto más se gasta del boom (menos se ahorra), mayor el ajuste forzoso "
                     "cuando el precio cae (m89) — la prociclicidad hecha vulnerabilidad."),
        ],
        intuicion=("El boom de materias primas es una prueba de carácter fiscal: la "
                   "manera de arruinarlo es creer que durará para siempre. La "
                   "tentación política es enorme — el ingreso extra llega sin subir "
                   "impuestos, y gastarlo es popular — pero cada sol de gasto "
                   "permanente financiado con ingreso transitorio es una bomba de "
                   "tiempo que estalla cuando el ciclo revierte. La disciplina de "
                   "ahorrar en las vacas gordas es contraintuitiva y "
                   "políticamente costosa, pero es LA diferencia entre los países "
                   "que capitalizan sus booms (Chile, Noruega) y los que los "
                   "desperdician en una sucesión de auges y colapsos. Para el Perú, "
                   "el superciclo de commodities de los 2000 fue en parte "
                   "aprovechado (reservas, reducción de deuda, m108) y en parte "
                   "no (gasto que luego costó ajustar) — la lección de m89 en "
                   "carne propia."),
        equilibrio=("El boom reparte entre ingreso (bueno), enfermedad holandesa "
                    "(malo) y decisión de ahorro (política). El equilibrio "
                    "sostenible ahorra el transitorio; el insostenible lo gasta y "
                    "queda expuesto a la reversión (verificado)."),
        limitaciones=[
            "Distinguir transitorio de permanente es difícil EN TIEMPO REAL (¿es un superciclo o un pico?) — el error de juicio es la trampa práctica.",
            "La enfermedad holandesa puede combatirse con política (intervención cambiaria, m45; diversificación) — no es destino.",
            "Sin reinversión: si el boom financia capital humano e infraestructura (m33, m106), puede elevar el crecimiento permanente — la cara virtuosa.",
        ],
        evolucion=("Es la cara EXPORTADORA del shock externo (contraste con m82 "
                   "importador) y el preludio de m89 (cuando el boom revierte). "
                   "Conecta con m68 (fiscal contracíclica), m46 (enfermedad "
                   "holandesa) y m105 (términos de intercambio). Para el Perú, es "
                   "el superciclo del cobre — m103, m105, m110."),
    ),
    escenarios=[
        Escenario("superciclo", "boom del 40% con ahorro prudente (30%)",
                  {"ti_shock": 40.0, "ahorro": 30.0},
                  "ingreso fuerte con parte ahorrada: el boom aprovechado "
                  "parcialmente — reservas y colchón fiscal para la reversión.",
                  cadena=["alza del cobre (términos de intercambio)", "shock de ingreso positivo",
                          "parte al fondo de estabilización (m68)", "parte gastada",
                          "menor exposición a la caída"]),
        Escenario("despilfarro", "gastar todo el boom (ahorro 0)",
                  {"ti_shock": 40.0, "ahorro": 0.0},
                  "máxima exposición a la reversión: el gasto permanente financiado "
                  "con ingreso transitorio — la bomba de tiempo de m89.",
                  cadena=["boom", "se gasta TODO como permanente",
                          "gasto comprometido a futuro", "cuando el precio cae (m89)",
                          "hay que recortar en recesión: crisis"]),
        Escenario("fondo_soberano", "ahorro alto (70%) tipo Chile/Noruega",
                  {"ahorro": 70.0},
                  "casi todo el transitorio ahorrado: la disciplina que capitaliza "
                  "el boom — gastar suave en el ciclo, no en el pico.",
                  cadena=["boom", "regla fiscal ahorra el transitorio (m68)",
                          "fondo de estabilización crece", "cuando revierte (m89)",
                          "el fondo sostiene el gasto: sin ajuste brusco"]),
        Escenario("enfermedad_severa", "alta exposición de transables (0.9)",
                  {"exposicion_t": 0.9, "holandesa": 0.6},
                  "la apreciación devasta la industria no minera: el boom "
                  "desindustrializa: se gana en cobre lo que se pierde en "
                  "manufactura y agro (m46).",
                  cadena=["boom aprecia el tipo de cambio real (m46)",
                          "transables no mineros pierden competitividad",
                          "manufactura y agro se contraen", "desindustrialización",
                          "mayor dependencia del recurso"]),
    ],
    verificaciones=[
        Verificacion("el boom es un shock de ingreso positivo", _v_ingreso_positivo),
        Verificacion("enfermedad holandesa: daña transables no mineros", _v_enfermedad_holandesa),
        Verificacion("ahorrar el transitorio protege de la reversión", _v_ahorrar_protege),
        Verificacion("gastar todo maximiza la exposición (prociclicidad)", _v_prociclicidad_peligrosa),
    ],
    notas="El boom no es el problema; gastarlo como si fuera para siempre, sí. Prueba de carácter fiscal.",
)
