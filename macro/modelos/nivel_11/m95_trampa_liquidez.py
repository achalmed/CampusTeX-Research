# m95_trampa_liquidez.py — trampa de liquidez: el episodio (Japón, 2008-2015)
# (nivel 11).
#
# La aplicación histórica de m12: cuando la tasa de política llega a cero y la
# economía sigue deprimida, la política monetaria convencional se agota. El
# episodio muestra el MENÚ de respuestas no convencionales y su eficacia:
#   (0) convencional: bajar la tasa — YA en cero, sin efecto
#   (1) QE (expansión cuantitativa): comprar activos largos → baja tasas largas
#   (2) forward guidance: prometer tasas bajas por más tiempo (m54)
#   (3) estímulo fiscal: multiplicador ALTO en el ZLB (m91)
#   (4) subir la meta de inflación: bajar la tasa real esperada (m94)
# La lección de Japón (décadas), EE.UU./Europa (2008-2015): la fiscal y las no
# convencionales SÍ funcionan, pero son más difíciles y controvertidas.
# Combina m12 (trampa), m54 (guidance), m91 (fiscal), m94 (deflación).
#
# Procedencia: trampa de liquidez (Keynes, Krugman 1998), ZLB post-2008
# (Woodford, Eggertsson — menciones) — conocimiento general; calibración
# didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _brecha(p):
    """La brecha de producto tras cada herramienta (partiendo de recesión)."""
    base = p["recesion"]                                  # brecha inicial negativa
    convencional = 0.0                                    # tasa ya en cero: sin efecto
    qe = p["qe"] * p["efic_qe"]
    guidance = p["guidance"] * p["efic_guidance"]
    fiscal = p["fiscal"] * p["mult_zlb"]                  # multiplicador ALTO (m91)
    cierre = convencional + qe + guidance + fiscal
    brecha_final = base + cierre
    return dict(base=base, convencional=convencional, qe=qe, guidance=guidance,
                fiscal=fiscal, cierre=cierre, final=brecha_final)


def _curvas(p):
    b = _brecha(p)
    cats = ["brecha\ninicial", "convencional\n(tasa=0)", "QE", "forward\nguidance",
            "fiscal\n(mult alto)", "brecha\nfinal"]
    vals = [b["base"], b["convencional"], b["qe"], b["guidance"], b["fiscal"], b["final"]]
    cols = [config.ROJO, config.GRIS, config.AZUL2, config.DORADO, config.VERDE, config.AZUL]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"recesión inicial {p['recesion']:+.0f} con tasa en el ZLB\n"
                          f"convencional: 0 (agotada) · fiscal: multiplicador {p['mult_zlb']:.1f}\n"
                          f"brecha final: {b['final']:+.1f} "
                          f"({'recuperada' if b['final'] > -1 else 'aún deprimida'})")}


def _resultados(p):
    b = _brecha(p)
    return {"brecha inicial (recesión)": b["base"],
            "efecto de bajar la tasa (ZLB)": b["convencional"],
            "efecto QE": b["qe"],
            "efecto forward guidance (m54)": b["guidance"],
            "efecto fiscal (mult alto, m91)": b["fiscal"],
            "brecha final": b["final"]}


def _ecuaciones_calibradas(p):
    b = _brecha(p)
    return [f"convencional $= 0$ (tasa ya en el ZLB, m12)",
            f"fiscal $= {p['fiscal']:.0f}\\times{p['mult_zlb']:.1f} = {b['fiscal']:.1f}$ "
            f"(multiplicador alto en ZLB, m91)"]


_P0 = {"recesion": -6.0, "qe": 2.0, "guidance": 1.5, "fiscal": 2.0,
       "efic_qe": 0.8, "efic_guidance": 1.0, "mult_zlb": 1.8}


def _v_convencional_inutil():
    b = _brecha(_P0)
    return b["convencional"] == 0, \
        ("bajar la tasa NO hace nada: ya está en cero (ZLB, m12) — la política monetaria "
         "convencional se agotó, el punto de partida del episodio")


def _v_fiscal_potente():
    b = _brecha(_P0)
    return b["fiscal"] > b["qe"] and _P0["mult_zlb"] > 1.5, \
        (f"el estímulo fiscal es la herramienta más potente en el ZLB (efecto {b['fiscal']:.1f}): "
         "el multiplicador es alto porque la política monetaria no lo compensa (m91)")


def _v_no_convencionales_funcionan():
    b = _brecha(_P0)
    return b["qe"] > 0 and b["guidance"] > 0, \
        (f"QE ({b['qe']:.1f}) y forward guidance ({b['guidance']:.1f}) SÍ estimulan aunque la "
         "tasa esté en cero: actúan sobre tasas largas y expectativas (m54)")


def _v_combinacion_recupera():
    b = _brecha(_P0)
    return b["final"] > b["base"], \
        (f"la combinación de herramientas cierra parte de la brecha ({b['base']:.0f}→{b['final']:.1f}): "
         "el ZLB no es impotencia, es un menú más difícil y controvertido (Japón, 2008-2015)")


MODELO = Modelo(
    id="m95", nivel=11,
    nombre="Trampa de liquidez (episodio)",
    xlabel="", ylabel="Brecha del producto y aportes",
    parametros=[
        Parametro("recesion", _P0["recesion"], -10, -2, 0.5, "Profundidad de la recesión inicial",
                  grupo="situación", definicion="la brecha que hay que cerrar con la tasa en cero"),
        Parametro("fiscal", _P0["fiscal"], 0, 5, 0.5, "Tamaño del estímulo fiscal", grupo="herramientas",
                  definicion="la más potente en el ZLB (m91)"),
        Parametro("mult_zlb", _P0["mult_zlb"], 1, 2.5, 0.1, "Multiplicador fiscal en ZLB",
                  grupo="herramientas", definicion="alto porque la tasa no compensa (m60, m91)"),
        Parametro("qe", _P0["qe"], 0, 4, 0.5, "Tamaño del QE", grupo="herramientas"),
        Parametro("guidance", _P0["guidance"], 0, 3, 0.5, "Fuerza del forward guidance (m54)",
                  grupo="herramientas"),
        Parametro("efic_qe", _P0["efic_qe"], 0.3, 1, 0.1, "Eficacia del QE", grupo="eficacia"),
        Parametro("efic_guidance", _P0["efic_guidance"], 0.3, 1.5, 0.1, "Eficacia del guidance",
                  grupo="eficacia"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando la tasa llega a cero y la economía sigue deprimida, ¿qué le queda al banco central?",
        variables=[("convencional", "bajar la tasa — YA en cero, sin efecto (m12)"),
                   ("QE, guidance", "las no convencionales: tasas largas y expectativas"),
                   ("fiscal", "la más potente en el ZLB: multiplicador alto (m91)")],
        derivacion=["tasa\\;en\\;ZLB\\;(m12): \\;convencional = 0",
                    "no\\;convencional: \\;QE + guidance\\;(m54) > 0",
                    "fiscal: \\;multiplicador\\;ALTO\\;(m91)\\;porque\\;no\\;hay\\;compensación"],
        contexto=("La trampa de liquidez pasó de curiosidad teórica (m12) a "
                  "problema central tras 2008, cuando EE.UU., Europa y el Reino "
                  "Unido llevaron sus tasas a cero y descubrieron lo que Japón "
                  "sabía desde los 90: que ahí la política monetaria convencional "
                  "se agota. Este modelo muestra el MENÚ de respuestas que se "
                  "desarrolló. La expansión cuantitativa (QE): comprar bonos largos "
                  "y otros activos para bajar las tasas LARGAS aunque la corta esté "
                  "en cero. El forward guidance (m54): prometer mantener las tasas "
                  "bajas por mucho tiempo, para bajar las tasas largas y las "
                  "expectativas. Y sobre todo, el estímulo FISCAL (m91), que en el "
                  "ZLB tiene un multiplicador especialmente alto porque el banco "
                  "central no lo compensa subiendo la tasa (no puede, ya está en "
                  "cero) — el argumento más fuerte para la política fiscal "
                  "activista, que 2009 (estímulo) y 2010-2012 (austeridad "
                  "prematura, m69) pusieron a prueba en direcciones opuestas. La "
                  "lección del episodio: el ZLB no es impotencia total, pero las "
                  "herramientas que quedan son más difíciles, más lentas y más "
                  "controvertidas — y la coordinación fiscal-monetaria se vuelve "
                  "esencial. Japón, con décadas de experiencia, sigue siendo el "
                  "laboratorio; la eurozona, con su austeridad de 2010-2012, el "
                  "contraejemplo de qué NO hacer."),
        autores=("Trampa de liquidez: Keynes (m12), Krugman (1998); ZLB post-2008: "
                 "Woodford, Eggertsson-Krugman, Bernanke — menciones; el "
                 "multiplicador alto en ZLB: m60/m91 (menciones)."),
        supuestos=[
            "La tasa está en el ZLB: la convencional es exactamente cero por construcción (m12).",
            "Las no convencionales tienen eficacia dada (QE, guidance): en la realidad es incierta y debatida.",
            "El multiplicador fiscal es alto en el ZLB (m60/m91): la evidencia post-2009 lo respalda pero con rango.",
        ],
        ecuaciones=[
            Ecuacion("convencional = 0 \\;;\\; fiscal = \\Delta G\\times mult_{ZLB}", "el menú del ZLB",
                     "la tasa no puede bajar (ya en cero), pero la fiscal rinde MÁS que en tiempos "
                     "normales porque no hay compensación monetaria (verificado)."),
            Ecuacion("no\\;convencional: \\;QE + guidance > 0", "las herramientas que quedan",
                     "actúan sobre tasas largas (QE) y expectativas (guidance, m54) — funcionan, "
                     "pero con eficacia menor y más incierta que la tasa corta (verificado)."),
        ],
        intuicion=("La trampa de liquidez enseña que 'sin munición' es un mito: "
                   "cuando la tasa llega a cero, al banco central le quedan "
                   "herramientas, solo que peores — como un cirujano que perdió su "
                   "bisturí preferido pero tiene otros instrumentos, más torpes. La "
                   "lección más importante del episodio 2008-2015 es sobre "
                   "COORDINACIÓN: en el ZLB, la política fiscal y la monetaria "
                   "deben trabajar juntas, porque la monetaria sola no basta y la "
                   "fiscal es especialmente potente. El gran error de la eurozona "
                   "(2010-2012) fue hacer austeridad (m69) justo en el ZLB, cuando "
                   "el multiplicador fiscal era máximo — profundizando la recesión "
                   "que intentaba resolver. EE.UU., con más estímulo, se recuperó "
                   "más rápido. Para un emergente como el Perú, el ZLB nunca ha "
                   "sido vinculante (las tasas son más altas, hay más espacio para "
                   "bajarlas), pero entender el episodio importa porque las "
                   "decisiones de los grandes bancos centrales en el ZLB (QE que "
                   "inundó de liquidez el mundo) fueron el 'push' que movió los "
                   "capitales hacia el Perú (m87, m111)."),
        equilibrio=("La brecha se cierra parcialmente con la combinación de "
                    "herramientas (verificado): el ZLB limita pero no anula la "
                    "capacidad de estímulo. La combinación óptima es fiscal + no "
                    "convencional coordinadas."),
        limitaciones=[
            "La eficacia de QE y guidance es incierta y debatida: el modelo la toma como dada, la evidencia real tiene rango amplio.",
            "Sin costos de las herramientas: el QE infla balances de bancos centrales y activos financieros (desigualdad); el guidance ata las manos futuras.",
            "Sin la dimensión internacional: el QE de los grandes exportó liquidez y complicó a los emergentes (m87) — externalidad no modelada.",
        ],
        evolucion=("Es la aplicación histórica de m12 (trampa), con el menú de "
                   "salidas de m54 (guidance), m91 (fiscal) y m94 (expectativas). "
                   "Cierra el bloque de los peligros deflacionarios (m94-m95), "
                   "opuesto a la estanflación (m93). Su relevancia para el Perú es "
                   "indirecta pero real: el ZLB de los grandes movió los capitales "
                   "globales (m87, m111)."),
    ),
    escenarios=[
        Escenario("solo_convencional", "intentar solo bajar la tasa (ya en cero)",
                  {"qe": 0.0, "guidance": 0.0, "fiscal": 0.0},
                  "nada se mueve: la tasa está en cero y no hay más que bajar — la "
                  "impotencia de la política convencional en el ZLB (m12).",
                  cadena=["recesión profunda", "tasa en el ZLB", "bajar la tasa: imposible (ya en 0)",
                          "sin otras herramientas", "la economía sigue deprimida"]),
        Escenario("respuesta_2009", "combinación completa: fiscal + QE + guidance",
                  {"fiscal": 3.0, "qe": 2.0, "guidance": 1.5},
                  "el menú completo cierra buena parte de la brecha: fiscal potente "
                  "+ no convencionales — la respuesta de EE.UU. en 2009.",
                  cadena=["recesión en el ZLB", "estímulo fiscal (mult alto, m91)",
                          "+ QE (tasas largas) + guidance (expectativas, m54)",
                          "las herramientas se suman", "recuperación (más rápida que Europa)"]),
        Escenario("austeridad_europea", "sin fiscal, solo no convencional",
                  {"fiscal": 0.0, "qe": 2.0, "guidance": 1.5},
                  "sin la herramienta más potente (fiscal), la recuperación es "
                  "lenta e incompleta: el error de la eurozona 2010-2012 (m69 en el "
                  "peor momento).",
                  cadena=["recesión en el ZLB", "austeridad: sin estímulo fiscal (m69)",
                          "solo QE y guidance (menos potentes)", "brecha se cierra poco",
                          "recuperación lenta: el error europeo"]),
        Escenario("japon_decadas", "recesión muy profunda con herramientas tímidas",
                  {"recesion": -9.0, "fiscal": 1.0, "qe": 1.0, "guidance": 0.5},
                  "herramientas insuficientes para una brecha enorme: la economía "
                  "queda deprimida por años — las décadas perdidas de Japón.",
                  cadena=["recesión muy profunda + deflación (m94)", "herramientas tímidas",
                          "la brecha no se cierra", "estancamiento prolongado",
                          "el laboratorio japonés del ZLB"]),
    ],
    verificaciones=[
        Verificacion("bajar la tasa es inútil en el ZLB (m12)", _v_convencional_inutil),
        Verificacion("el fiscal es la herramienta más potente (m91)", _v_fiscal_potente),
        Verificacion("QE y guidance SÍ funcionan (m54)", _v_no_convencionales_funcionan),
        Verificacion("la combinación recupera (no es impotencia)", _v_combinacion_recupera),
    ],
    notas="'Sin munición' es un mito: quedan herramientas, solo peores. La clave es la coordinación fiscal-monetaria.",
)
