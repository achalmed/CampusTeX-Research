# m91_gasto_publico.py — aumento masivo del gasto público (nivel 11).
#
# El episodio de estímulo fiscal, integrando el multiplicador (m60) con la
# restricción intertemporal (m63). Un impulso de gasto ΔG tiene un efecto de
# corto plazo (multiplicador, depende del régimen m60) y un costo de largo
# plazo (deuda que hay que servir, m63-m64). El efecto NETO sobre el bienestar
# depende de: (1) el régimen (ZLB amplifica, m60), (2) si el gasto es
# productivo (inversión que crece el potencial, m22/m106) o consumo, y (3) la
# posición fiscal inicial (espacio, m65). Combina m60, m63-m65, m106.
#
# Procedencia: multiplicador por régimen (m60), aritmética de la deuda
# (m63-m64), inversión pública y crecimiento (m106) — conocimiento general;
# calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


_HORIZONTE = 10   # la deuda es permanente: su servicio se paga por muchos años.
                  # capitalizamos el flujo anual (r−g) sobre una década para
                  # comparar peras (impulso de una vez) con peras (costo perpetuo).


def _balance(p):
    impulso_Y = p["dG"] * p["multiplicador"]              # efecto de corto plazo (m60), de una vez
    # si es inversión productiva, eleva el potencial (m106)
    efecto_potencial = p["dG"] * p["productivo"] / 100 * p["retorno"]
    # costo: deuda nueva y su servicio (m63), capitalizado sobre el horizonte (m64).
    # con r>g el servicio anual (r−g) se paga indefinidamente → pesa mucho;
    # con r<g es negativo (la deuda se licúa sola).
    deuda_nueva = p["dG"]
    servicio = deuda_nueva * (p["r"] - p["g"]) / 100 * _HORIZONTE   # bola de nieve neta (m64)
    neto = impulso_Y + efecto_potencial - servicio
    return dict(impulso_Y=impulso_Y, efecto_potencial=efecto_potencial,
                deuda_nueva=deuda_nueva, servicio=servicio, neto=neto)


def _curvas(p):
    b = _balance(p)
    cats = ["impulso CP\n(multiplic. m60)", "efecto potencial\n(si productivo m106)",
            "servicio de deuda\n(m64)", "efecto NETO"]
    vals = [b["impulso_Y"], b["efecto_potencial"], -b["servicio"], b["neto"]]
    cols = [config.AZUL2, config.VERDE, config.ROJO, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"ΔG={p['dG']:.0f}, multiplicador={p['multiplicador']:.2f} (régimen, m60)\n"
                          f"{p['productivo']:.0f}% productivo, r−g={p['r'] - p['g']:+.1f}\n"
                          f"efecto neto: {b['neto']:+.1f} "
                          f"({'vale la pena' if b['neto'] > 0 else 'contraproducente'})")}


def _resultados(p):
    b = _balance(p)
    return {"impulso de corto plazo (m60)": b["impulso_Y"],
            "efecto sobre el potencial (m106)": b["efecto_potencial"],
            "deuda nueva": b["deuda_nueva"],
            "servicio de deuda (m64)": b["servicio"],
            "efecto neto sobre el bienestar": b["neto"]}


def _ecuaciones_calibradas(p):
    b = _balance(p)
    return [f"impulso $= {p['dG']:.0f}\\times{p['multiplicador']:.2f} = {b['impulso_Y']:.1f}$",
            f"servicio $= {p['dG']:.0f}\\times({p['r'] - p['g']:+.1f})/100 = {b['servicio']:.2f}$",
            f"neto $= {b['neto']:+.1f}$"]


_P0 = {"dG": 10.0, "multiplicador": 1.0, "productivo": 50.0, "retorno": 0.3,
       "r": 4.0, "g": 3.0}


def _v_zlb_amplifica():
    b_normal = _balance(dict(_P0, multiplicador=0.7))
    b_zlb = _balance(dict(_P0, multiplicador=1.8))
    return b_zlb["impulso_Y"] > b_normal["impulso_Y"], \
        (f"en el ZLB el multiplicador es mayor (impulso {b_normal['impulso_Y']:.1f}→"
         f"{b_zlb['impulso_Y']:.1f}): el estímulo rinde más cuando la regla duerme (m60, m95)")


def _v_productivo_mejor():
    b_prod = _balance(dict(_P0, productivo=90.0))
    b_consumo = _balance(dict(_P0, productivo=10.0))
    return b_prod["neto"] > b_consumo["neto"], \
        (f"el gasto productivo (inversión) rinde más que el consumo (neto {b_consumo['neto']:.1f}→"
         f"{b_prod['neto']:.1f}): eleva el potencial y ayuda a pagar su propia deuda (m106)")


def _v_rg_favorable_abarata():
    b_favorable = _balance(dict(_P0, r=2.0, g=4.0))       # r<g
    b_adverso = _balance(dict(_P0, r=6.0, g=2.0))         # r>g
    return b_favorable["neto"] > b_adverso["neto"], \
        (f"con r<g el servicio es negativo (la deuda se licúa sola, m64): el estímulo es "
         "mucho más barato — la aritmética de la deuda decide (verificado)")


def _v_sin_espacio_contraproducente():
    b = _balance(dict(_P0, r=8.0, g=1.0, productivo=10.0, multiplicador=0.5))
    return b["neto"] < 0, \
        ("con r≫g, gasto improductivo y multiplicador bajo (régimen adverso + sin espacio), "
         "el estímulo es CONTRAPRODUCENTE: más deuda sin beneficio (m65)")


MODELO = Modelo(
    id="m91", nivel=11,
    nombre="Aumento masivo del gasto público",
    xlabel="", ylabel="Efectos del estímulo (u.m.)",
    parametros=[
        Parametro("dG", _P0["dG"], 2, 25, 1, "Magnitud del estímulo ΔG", grupo="estímulo"),
        Parametro("multiplicador", _P0["multiplicador"], 0.3, 2, 0.1, "Multiplicador (régimen, m60)",
                  grupo="corto plazo", definicion="ZLB alto, Taylor activo bajo, flotación 0"),
        Parametro("productivo", _P0["productivo"], 0, 100, 10, "Fracción productiva (%)",
                  grupo="calidad", definicion="inversión que crece el potencial (m106) vs consumo"),
        Parametro("r", _P0["r"], 1, 9, 0.5, "Tasa r (%)", grupo="largo plazo"),
        Parametro("g", _P0["g"], 0, 6, 0.5, "Crecimiento g (%)", grupo="largo plazo",
                  definicion="r−g decide el costo de servir la deuda (m64)"),
        Parametro("retorno", _P0["retorno"], 0.1, 0.6, 0.05, "Retorno social de la inversión",
                  grupo="calidad"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuándo un estímulo fiscal masivo vale la pena — y cuándo es solo deuda para nada?",
        variables=[("impulso CP", "el efecto de corto plazo (multiplicador, m60)"),
                   ("servicio", "el costo de largo plazo (la deuda que se sirve, m64)"),
                   ("productivo", "la calidad: inversión que se paga sola vs consumo")],
        derivacion=["corto: \\;\\Delta Y = multiplicador\\times\\Delta G \\;(m60)",
                    "largo: \\;servicio = \\Delta G\\times(r-g) \\;(m64)",
                    "neto = impulso + potencial - servicio"],
        contexto=("El estímulo fiscal es una de las decisiones más debatidas de la "
                  "macroeconomía, y este modelo integra las dos mitades del análisis "
                  "que el currículo construyó por separado. La mitad de CORTO plazo "
                  "es el multiplicador (m60): cuánto producto genera cada sol de "
                  "gasto, que depende críticamente del régimen — grande en el ZLB "
                  "(cuando la política monetaria no puede compensar, m95), pequeño "
                  "con un banco central activo (m56), cero en flotación con "
                  "movilidad perfecta (m49). La mitad de LARGO plazo es la "
                  "restricción intertemporal (m63-m64): el gasto se financia con "
                  "deuda que hay que servir, y el costo neto depende de r−g (con "
                  "r<g la deuda se licúa sola). El veredicto sobre si un estímulo "
                  "'vale la pena' depende de tres cosas: el régimen (¿estamos en el "
                  "ZLB?), la CALIDAD del gasto (¿inversión productiva que eleva el "
                  "potencial y ayuda a pagar su propia deuda, m106, o consumo que "
                  "solo deja pasivo?) y el espacio fiscal inicial (m65). El debate "
                  "del estímulo de 2009 y del gasto COVID de 2020 (m81) giró "
                  "exactamente sobre estos ejes. Para el Perú, con espacio fiscal "
                  "históricamente prudente (m108), la pregunta es cómo usar ese "
                  "espacio: inversión en infraestructura y capital humano (m106, "
                  "m112) que eleve el crecimiento, no consumo que solo deje deuda."),
        autores=("Multiplicador por régimen: m60 (Ramey, Ilzetzki — menciones); "
                 "aritmética de la deuda: m63-m64; inversión pública y crecimiento: "
                 "m106 (conocimiento general)."),
        supuestos=[
            "El multiplicador es dado (resume el régimen de m60): endogeneizarlo exige el modelo completo (m56).",
            "El gasto productivo eleva el potencial con un retorno social dado (m106): la calidad importa tanto como la cantidad.",
            "r−g exógeno: en la realidad un estímulo grande puede subir r (prima, m76) — el espacio no es infinito.",
        ],
        ecuaciones=[
            Ecuacion("neto = mult\\cdot\\Delta G + productivo\\cdot retorno - \\Delta G(r-g)",
                     "el balance completo",
                     "corto plazo (multiplicador) más efecto potencial (si productivo) menos "
                     "servicio de deuda: las tres mitades del veredicto (verificado)."),
            Ecuacion("ZLB \\Rightarrow mult\\uparrow \\;;\\; productivo \\Rightarrow potencial\\uparrow \\;;\\; r<g \\Rightarrow servicio<0",
                     "las tres condiciones que lo hacen valer",
                     "el estímulo ideal: en recesión profunda (ZLB), en inversión productiva, con "
                     "r<g — las tres alinean corto y largo plazo (verificado)."),
        ],
        intuicion=("El estímulo fiscal no es bueno ni malo en abstracto: depende de "
                   "CUÁNDO, en QUÉ y con CUÁNTO espacio. El caso ideal — el que "
                   "justifica un estímulo masivo — es una recesión profunda con la "
                   "política monetaria agotada (ZLB, m95), donde el multiplicador es "
                   "grande, gastado en inversión productiva que eleva el potencial "
                   "(m106) y ayuda a pagar su propia deuda, con r<g que licúa el "
                   "pasivo. El caso pésimo es un estímulo en auge (multiplicador "
                   "bajo, incluso negativo por expulsión m11/m49), en consumo "
                   "improductivo, con r>g y sin espacio fiscal — deuda para nada. "
                   "La mayoría de los casos reales están en el medio, y el arte de "
                   "la política fiscal es reconocer en cuál se está. La lección "
                   "del currículo: separar la pregunta de corto plazo (¿estimula?) "
                   "de la de largo plazo (¿se paga?) y exigir que AMBAS den "
                   "positivo — o al menos que el beneficio de corto supere el costo "
                   "de largo."),
        equilibrio=("El efecto neto suma impulso de corto, efecto potencial y "
                    "servicio de deuda (verificado). Positivo cuando las "
                    "condiciones se alinean (ZLB + productivo + r<g), negativo "
                    "cuando se oponen (auge + consumo + r>g)."),
        limitaciones=[
            "El multiplicador es exógeno: en realidad responde al propio estímulo (un estímulo grande puede subir r y bajar su multiplicador — m76).",
            "El retorno de la inversión pública es incierto y a menudo sobreestimado (elefantes blancos) — la CALIDAD institucional decide (m106).",
            "Estático: la dinámica (el estímulo hoy es deuda mañana es menos espacio pasado mañana) exige la senda completa (m64).",
        ],
        evolucion=("Integra el multiplicador (m60) con la deuda (m63-m64) y la "
                   "inversión productiva (m106) en el veredicto sobre el estímulo. "
                   "Contrasta con la austeridad (m69) y prepara m106 (inversión "
                   "pública peruana → crecimiento) y m107 (gasto → multiplicador "
                   "con datos del MEF)."),
    ),
    escenarios=[
        Escenario("estimulo_ideal", "ZLB + inversión productiva + r<g",
                  {"multiplicador": 1.8, "productivo": 90.0, "r": 2.0, "g": 4.0},
                  "las tres condiciones alinean: multiplicador alto, potencial que "
                  "sube, deuda que se licúa sola — el caso que justifica un estímulo "
                  "masivo (2009 bien hecho).",
                  cadena=["recesión profunda (ZLB, m95)", "multiplicador grande (m60)",
                          "inversión productiva eleva el potencial (m106)", "r<g licúa la deuda (m64)",
                          "efecto neto muy positivo"]),
        Escenario("estimulo_desperdiciado", "auge + consumo + r>g",
                  {"multiplicador": 0.5, "productivo": 10.0, "r": 7.0, "g": 2.0},
                  "las tres se oponen: multiplicador bajo, sin efecto potencial, "
                  "deuda cara — deuda para nada, el estímulo que no debió ser.",
                  cadena=["gasto en auge (multiplicador bajo, m11)", "consumo improductivo",
                          "r>g: la deuda pesa (m64)", "sin beneficio de corto ni de largo",
                          "contraproducente: solo pasivo"]),
        Escenario("inversion_publica", "gasto 90% productivo (infraestructura)",
                  {"productivo": 90.0, "retorno": 0.5},
                  "el efecto potencial domina: la inversión que crece la economía se "
                  "paga en parte sola — el caso peruano ideal (m106, m112).",
                  cadena=["inversión en infraestructura/capital humano", "↑potencial (m22, m106)",
                          "más crecimiento futuro", "ayuda a servir su propia deuda",
                          "el buen uso del espacio fiscal"]),
        Escenario("sin_espacio", "posición fiscal frágil (r=8, g=1)",
                  {"r": 8.0, "g": 1.0, "productivo": 30.0},
                  "el servicio de deuda devora el impulso: sin espacio fiscal (m65), "
                  "hasta un estímulo razonable sale caro — la restricción del "
                  "emergente endeudado.",
                  cadena=["posición fiscal frágil (r≫g)", "cada sol de gasto pesa mucho",
                          "el servicio devora el impulso", "poco margen para estímulo",
                          "el espacio fiscal es un activo (m65)"]),
    ],
    verificaciones=[
        Verificacion("el ZLB amplifica el multiplicador (m60)", _v_zlb_amplifica),
        Verificacion("el gasto productivo rinde más (m106)", _v_productivo_mejor),
        Verificacion("r<g abarata el estímulo (m64)", _v_rg_favorable_abarata),
        Verificacion("sin condiciones, es contraproducente (m65)", _v_sin_espacio_contraproducente),
    ],
    notas="No es bueno ni malo en abstracto: depende de cuándo (ZLB), en qué (productivo) y con cuánto espacio (m65).",
)
