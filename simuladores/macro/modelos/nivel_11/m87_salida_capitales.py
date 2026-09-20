"""simuladores/macro/modelos/nivel_11/m87_salida_capitales.py — salida de capitales de un emergente (nivel 11).

El sudden stop (m75) con el gatillo del apetito global de riesgo. La entrada
de capital de un emergente se descompone en:
  CF = pull (fundamentos locales: crecimiento, tasa) + push (apetito global)
Cuando el push se revierte (risk-off: FED m86, guerra, pánico), el capital
huye AUNQUE los fundamentos locales no cambien — el "sudden stop" de Calvo
(m75) por contagio. La defensa: reservas (m50) que permiten un ajuste
ordenado en vez de un colapso. Combina m75 (sudden stop), m86 (FED), m43
(reservas) y m84 (la devaluación resultante).

Procedencia: descomposición push/pull de flujos (Calvo-Leiderman-Reinhart
1993 — mención); sudden stop (m75, Calvo en biblioteca) — conocimiento
general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _flujo(p):
    pull = p["fundamentos"]                                # fundamentos locales
    push = p["apetito_global"]                             # apetito global de riesgo
    cf = pull + push
    # el ajuste que fuerza si CF se vuelve negativo (m75):
    ajuste = -cf if cf < 0 else 0.0
    # las reservas amortiguan: cubren hasta `reservas` del ajuste
    ajuste_sin_reservas = ajuste
    ajuste_con_reservas = max(0.0, ajuste - p["reservas"])
    return dict(pull=pull, push=push, cf=cf, ajuste=ajuste,
                ajuste_con_reservas=ajuste_con_reservas)


def _curvas(p):
    f = _flujo(p)
    cats = ["pull\n(fundamentos)", "push\n(apetito global)", "flujo neto\n$CF$",
            "ajuste sin\nreservas", "ajuste con\nreservas"]
    vals = [f["pull"], f["push"], f["cf"], -f["ajuste"], -f["ajuste_con_reservas"]]
    cols = [config.VERDE, config.DORADO, config.AZUL2, config.ROJO, config.AZUL]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"apetito global {p['apetito_global']:+.0f} "
                          f"({'risk-on' if p['apetito_global'] > 0 else 'risk-OFF'})\n"
                          f"flujo neto: {f['cf']:+.0f} "
                          f"({'entra' if f['cf'] > 0 else 'HUYE'})\n"
                          f"las reservas ({p['reservas']:.0f}) cortan el ajuste de "
                          f"{f['ajuste']:.0f} a {f['ajuste_con_reservas']:.0f}")}


def _resultados(p):
    f = _flujo(p)
    return {"pull (fundamentos locales)": f["pull"],
            "push (apetito global)": f["push"],
            "flujo de capital neto CF": f["cf"],
            "ajuste forzado sin reservas": f["ajuste"],
            "ajuste con reservas (m50)": f["ajuste_con_reservas"],
            "amortiguación de las reservas": f["ajuste"] - f["ajuste_con_reservas"]}


def _ecuaciones_calibradas(p):
    f = _flujo(p)
    return [f"$CF = pull + push = {f['pull']:.0f} + ({f['push']:.0f}) = {f['cf']:.0f}$",
            f"ajuste $= \\max(0, -CF - reservas) = {f['ajuste_con_reservas']:.0f}$"]


_P0 = {"fundamentos": 15.0, "apetito_global": -35.0, "reservas": 20.0}


def _v_push_domina():
    f = _flujo(_P0)
    return f["cf"] < 0 and _P0["fundamentos"] > 0, \
        (f"con fundamentos SANOS ({_P0['fundamentos']:+.0f}) el capital HUYE igual (CF {f['cf']:+.0f}) "
         "porque el push global (risk-off) domina: el sudden stop por contagio (m75)")


def _v_reservas_amortiguan():
    f = _flujo(_P0)
    return f["ajuste_con_reservas"] < f["ajuste"], \
        (f"las reservas cortan el ajuste ({f['ajuste']:.0f}→{f['ajuste_con_reservas']:.0f}): "
         "convierten un colapso desordenado en un ajuste manejable (m50, el colchón peruano)")


def _v_risk_on_no_ajuste():
    f = _flujo(dict(_P0, apetito_global=20.0))
    return f["ajuste"] == 0, \
        ("en risk-on (apetito global positivo), el capital ENTRA y no hay ajuste: "
         "los emergentes son cuenta bancaria del apetito global — bendición y maldición")


def _v_fundamentos_no_bastan():
    f_bueno = _flujo(dict(_P0, fundamentos=25.0))
    f_malo = _flujo(dict(_P0, fundamentos=5.0))
    return f_bueno["cf"] < 0 and f_malo["cf"] < 0, \
        ("aun con fundamentos excelentes, un push suficientemente negativo fuerza salida: "
         "el contagio no discrimina — 'globalización de la ignorancia' (Calvo, m75)")


MODELO = Modelo(
    id="m87", nivel=11,
    nombre="Salida de capitales de un emergente",
    xlabel="", ylabel="Flujos de capital (u.m.)",
    parametros=[
        Parametro("apetito_global", _P0["apetito_global"], -50, 30, 5, "Apetito global de riesgo (push)",
                  grupo="global", definicion="risk-on (>0) vs risk-off (<0): lo que el emergente NO controla"),
        Parametro("fundamentos", _P0["fundamentos"], -10, 30, 5, "Fundamentos locales (pull)",
                  grupo="local", definicion="crecimiento, tasa, estabilidad: lo que SÍ controla"),
        Parametro("reservas", _P0["reservas"], 0, 60, 5, "Reservas disponibles (m50)",
                  grupo="defensa", definicion="el colchón que amortigua el ajuste"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué el capital huye de un emergente con buenos fundamentos — y qué lo protege?",
        variables=[("pull", "fundamentos locales — lo que el país controla"),
                   ("push", "apetito global de riesgo — lo que NO controla"),
                   ("reservas", "el colchón que convierte colapso en ajuste ordenado")],
        derivacion=["CF = pull\\;(fundamentos) + push\\;(apetito\\;global)",
                    "risk\\text{-}off: \\;push < 0 \\Rightarrow CF < 0\\;aun\\;con\\;pull > 0",
                    "ajuste = \\max(0, -CF - reservas) \\;\\;(m50\\;amortigua)"],
        contexto=("Los flujos de capital hacia los emergentes se descomponen en dos "
                  "fuerzas (Calvo-Leiderman-Reinhart 1993, mención): el 'pull' de "
                  "los fundamentos locales (¿crece?, ¿paga buena tasa?, ¿es "
                  "estable?) y el 'push' del apetito global de riesgo (¿los "
                  "inversores del mundo quieren riesgo o seguridad?). La lección "
                  "amarga es que el PUSH suele dominar: cuando el mundo entra en "
                  "'risk-off' — por un alza de la FED (m86), una guerra, un pánico "
                  "— el capital huye de TODOS los emergentes a la vez, sin "
                  "distinguir el bueno del malo. Es el sudden stop de Calvo (m75) "
                  "disparado por contagio, lo que él llamó la 'globalización de la "
                  "ignorancia': los inversores tratan a los emergentes como una "
                  "clase de activo, no como países. La única defensa real es "
                  "acumular reservas (m50) en las buenas, que permiten un ajuste "
                  "ordenado — vender reservas para suavizar la salida — en vez de "
                  "un colapso cambiario (m84) o un default (m76). Por eso el Perú, "
                  "escaldado por los 80, acumuló reservas masivas: no puede "
                  "controlar el push, pero puede sobrevivirlo (m110-m111)."),
        autores=("Descomposición push/pull: Calvo, Leiderman y Reinhart (1993 — "
                 "mención); sudden stop y 'globalización de la ignorancia': Calvo "
                 "(m75, en biblioteca) — conocimiento general."),
        supuestos=[
            "CF lineal en pull + push: la realidad tiene no linealidades (los umbrales de pánico son abruptos, m74).",
            "Reservas amortiguan uno a uno hasta agotarse: en la práctica su uso señala debilidad y puede acelerar la fuga (m74).",
            "Sin balances en dólares: si la deuda es en dólares, la salida + devaluación quiebra deudores (m84) — el círculo mortal.",
        ],
        ecuaciones=[
            Ecuacion("CF = pull + push", "las dos fuerzas del flujo",
                     "el apetito global (push) puede voltear el flujo aunque los fundamentos "
                     "(pull) sean sólidos: el emergente es tomador del ciclo global (verificado)."),
            Ecuacion("ajuste = \\max(0, -CF - reservas)", "el colchón que salva",
                     "las reservas absorben la salida hasta agotarse: convierten un colapso en un "
                     "ajuste manejable — la diferencia entre crisis y molestia (verificado)."),
        ],
        intuicion=("La salida de capitales enseña la lección más humillante para un "
                   "emergente: hacer bien las cosas no basta. Un país puede tener "
                   "crecimiento sólido, inflación anclada y cuentas ordenadas, y "
                   "aun así sufrir una fuga masiva porque un inversor en Nueva York "
                   "decidió reducir riesgo. Esta es la asimetría fundamental del "
                   "sistema financiero global: los emergentes reciben capital "
                   "cuando el mundo está eufórico (y a menudo demasiado, inflando "
                   "burbujas locales) y lo pierden cuando el mundo se asusta (y a "
                   "menudo demasiado, forzando ajustes brutales). Como no pueden "
                   "controlar el push, la estrategia racional es la resiliencia: "
                   "reservas altas (m50), baja dolarización (m84), deuda en moneda "
                   "local (m76), ancla creíble (m85). Todo lo que permite decir 'que "
                   "huya el capital, tenemos con qué aguantar' — la doctrina "
                   "peruana post-crisis (m110)."),
        equilibrio=("El flujo es la suma pull+push; el ajuste forzado (si CF<0) lo "
                    "amortiguan las reservas hasta agotarse (verificado). Con "
                    "reservas suficientes, la salida es ordenada; sin ellas, es "
                    "colapso (m74/m84)."),
        limitaciones=[
            "El uso de reservas puede señalar debilidad y acelerar la fuga (segunda generación, m74) — el colchón tiene un límite psicológico, no solo contable.",
            "Push exógeno: en realidad hay retroalimentación (la fuga de un emergente contagia a otros — m80 aplicado a países).",
            "Sin distinción por tipo de flujo: la IED estable no huye como la cartera (m75) — la COMPOSICIÓN del CF importa para la fragilidad.",
        ],
        evolucion=("Es el sudden stop (m75) con gatillo global (m86), y la razón de "
                   "ser de las reservas (m50). Conecta con m84 (la devaluación que "
                   "la salida fuerza) y m85 (la inflación importada resultante). La "
                   "versión peruana — FED y flujos hacia el Perú — es m111."),
    ),
    escenarios=[
        Escenario("risk_off", "pánico global con fundamentos sanos",
                  {"apetito_global": -35.0, "fundamentos": 15.0},
                  "el capital huye pese a los buenos fundamentos: el contagio no "
                  "discrimina — hacer bien las cosas no inmuniza (Calvo).",
                  cadena=["risk-off global (FED, guerra, pánico)", "push muy negativo",
                          "domina sobre los fundamentos sanos", "CF se vuelve negativo",
                          "sudden stop por contagio (m75)"]),
        Escenario("con_reservas", "el mismo shock con reservas altas (Perú)",
                  {"apetito_global": -35.0, "reservas": 40.0},
                  "las reservas cortan el ajuste a la mitad: el colchón convierte "
                  "una crisis en un ajuste manejable — para esto se acumularon "
                  "(m50, m110).",
                  cadena=["misma fuga de capital", "reservas amortiguan (m50)",
                          "ajuste ordenado en vez de colapso", "sin devaluación caótica",
                          "la resiliencia comprada en las buenas"]),
        Escenario("risk_on", "euforia global: apetito +20",
                  {"apetito_global": 20.0},
                  "el capital ENTRA en masa: la otra cara de la moneda — los "
                  "emergentes reciben demasiado en los booms, sembrando la próxima "
                  "burbuja (m72).",
                  cadena=["risk-on global (búsqueda de rendimiento)", "push positivo fuerte",
                          "capital entra en masa", "apreciación y crédito fácil",
                          "posible burbuja local (la semilla del próximo ciclo)"]),
        Escenario("sin_colchon", "fuga severa sin reservas (emergente frágil)",
                  {"apetito_global": -45.0, "reservas": 5.0},
                  "el ajuste cae casi entero sobre la economía: sin reservas, la "
                  "salida se vuelve colapso cambiario (m84) o default (m76) — el "
                  "destino de los 80.",
                  cadena=["fuga severa", "reservas insuficientes", "el ajuste no se amortigua",
                          "colapso cambiario o default", "la crisis que las reservas evitan"]),
    ],
    verificaciones=[
        Verificacion("el push domina: huye con fundamentos sanos", _v_push_domina),
        Verificacion("las reservas amortiguan el ajuste (m50)", _v_reservas_amortiguan),
        Verificacion("risk-on: el capital entra (no hay ajuste)", _v_risk_on_no_ajuste),
        Verificacion("los fundamentos no bastan contra el contagio", _v_fundamentos_no_bastan),
    ],
    notas="Hacer bien las cosas no basta: el push global domina. La defensa es resiliencia comprada en las buenas.",
)
