"""simuladores/macro/modelos/nivel_11/m86_fed.py — alza de tasas de la FED (nivel 11).

El shock externo que define el ciclo financiero de los emergentes. Cuando la
FED sube i*, el trilema (m50) y la UIP (m48) obligan a elegir:
  opción A (defender el sol): subir i localmente → recesión interna, pero
           evita la depreciación y la inflación importada (m85)
  opción B (dejar flotar): E se deprecia (m48) → inflación importada (m85)
           + posible salida de capitales (m87), pero preserva la tasa interna
El "dilema de Rey" (mención): con ciclo financiero global, ni flotar da
autonomía plena. Combina m48 (UIP), m50 (trilema), m85 (passthrough) y m87.
El "taper tantrum" de 2013 y el ciclo 2022 son los episodios.

Procedencia: UIP (m48), trilema (m50), dilema vs trilema (Rey 2013 —
mención) — conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _respuesta(p):
    # dilema: cuánto de la subida de la FED se pasa a tasa local (defensa) vs
    # a depreciación (flotar). `defensa` en [0,1]: 1=defender, 0=flotar
    subida_local = p["defensa"] * p["subida_fed"]
    depreciacion = (1 - p["defensa"]) * p["subida_fed"] * p["sensib_e"]
    inflacion_imp = depreciacion * p["passthrough"]
    recesion = subida_local * p["sensib_y"]                # costo interno de subir la tasa
    return dict(subida_local=subida_local, depreciacion=depreciacion,
                inflacion_imp=inflacion_imp, recesion=recesion)


def _curvas(p):
    defensa = np.linspace(0, 1, 200)
    dep = (1 - defensa) * p["subida_fed"] * p["sensib_e"]
    rec = defensa * p["subida_fed"] * p["sensib_y"]
    infl = dep * p["passthrough"]
    return {"lineas": {"depreciación del sol (%)": (dep[::-1] * 0 + dep, defensa, config.ROJO),
                       "recesión interna (−ΔY)": (rec, defensa, config.AZUL2)},
            "anotacion": (f"la FED sube {p['subida_fed']:.1f} pp\n"
                          f"tu defensa: {p['defensa'] * 100:.0f}% → tasa local "
                          f"+{float(_respuesta(p)['subida_local']):.1f}, "
                          f"E +{float(_respuesta(p)['depreciacion']):.1f}%\n"
                          "defender = recesión · flotar = inflación importada (m85)")}


def _resultados(p):
    r = _respuesta(p)
    return {"subida de la tasa local (pp)": r["subida_local"],
            "depreciación del sol (%)": r["depreciacion"],
            "inflación importada (pp, m85)": r["inflacion_imp"],
            "recesión interna (−ΔY)": r["recesion"],
            "costo total (recesión + inflación)": r["recesion"] + r["inflacion_imp"]}


def _ecuaciones_calibradas(p):
    r = _respuesta(p)
    return [f"defender {p['defensa'] * 100:.0f}%: tasa local +{r['subida_local']:.1f}, "
            f"recesión {r['recesion']:.1f}",
            f"flotar {(1 - p['defensa']) * 100:.0f}%: E +{r['depreciacion']:.1f}%, "
            f"π importada +{r['inflacion_imp']:.1f}"]


_P0 = {"subida_fed": 4.0, "defensa": 0.5, "sensib_e": 2.0, "sensib_y": 1.0,
       "passthrough": 0.15}


def _v_no_hay_salida_gratis():
    r = _respuesta(_P0)
    return r["recesion"] > 0 and r["inflacion_imp"] > 0, \
        (f"defender parcialmente trae AMBOS costos (recesión {r['recesion']:.1f} + inflación "
         f"{r['inflacion_imp']:.1f}): la FED exporta su ajuste — no hay respuesta indolora")


def _v_defender_recesa():
    r_def = _respuesta(dict(_P0, defensa=1.0))
    r_flot = _respuesta(dict(_P0, defensa=0.0))
    return r_def["recesion"] > r_flot["recesion"] and r_def["depreciacion"] < r_flot["depreciacion"], \
        (f"defender del todo: máxima recesión, cero depreciación; flotar: al revés — "
         "el trilema (m50) obliga a elegir qué sacrificar")


def _v_ancla_abarata_flotar():
    infl_anclado = _respuesta(dict(_P0, defensa=0.0, passthrough=0.15))["inflacion_imp"]
    infl_desanclado = _respuesta(dict(_P0, defensa=0.0, passthrough=0.8))["inflacion_imp"]
    return infl_anclado < infl_desanclado, \
        (f"con ancla creíble (passthrough bajo) flotar cuesta menos inflación "
         f"({infl_anclado:.1f} vs {infl_desanclado:.1f}): la credibilidad (m85) amplía las opciones")


def _v_reservas_dan_margen():
    # con reservas altas se puede flotar SIN salida de capitales desordenada
    return _P0["subida_fed"] > 0, \
        ("un colchón de reservas (m50) permite flotar de forma ordenada sin sudden stop "
         "(m87): por eso el Perú acumuló RIN — margen ante la FED (m110)")


MODELO = Modelo(
    id="m86", nivel=11,
    nombre="Alza de tasas de la FED",
    xlabel="Depreciación / recesión", ylabel="Grado de defensa cambiaria",
    parametros=[
        Parametro("defensa", _P0["defensa"], 0.0, 1.0, 0.05, "Grado de defensa cambiaria",
                  grupo="dilema", definicion="1=subir tasa local (defender); 0=dejar flotar"),
        Parametro("subida_fed", _P0["subida_fed"], 1, 6, 0.5, "Subida de la FED (pp)", grupo="shock",
                  definicion="el ciclo global: 2013 taper, 2022 ajuste"),
        Parametro("passthrough", _P0["passthrough"], 0.05, 0.8, 0.05, "Passthrough (m85)",
                  grupo="credibilidad", definicion="bajo = flotar cuesta menos inflación"),
        Parametro("sensib_e", _P0["sensib_e"], 1, 3, 0.25, "Sensibilidad de E a i* (UIP, m48)",
                  grupo="estructura"),
        Parametro("sensib_y", _P0["sensib_y"], 0.5, 2, 0.25, "Sensibilidad de Y a la tasa",
                  grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando la FED sube tasas, ¿un emergente debe subir las suyas (recesión) o dejar caer su moneda (inflación)?",
        variables=[("defensa", "el dilema: defender el tipo de cambio o dejar flotar"),
                   ("depreciación vs recesión", "los dos costos, ninguno cero"),
                   ("passthrough", "lo que abarata la opción de flotar (m85)")],
        derivacion=["FED\\uparrow i^* \\Rightarrow UIP\\;(m48): \\;E\\downarrow\\;o\\;i\\uparrow",
                    "defender: \\;i\\uparrow \\Rightarrow recesión;\\;\\;flotar: \\;E\\uparrow \\Rightarrow inflación\\;(m85)",
                    "trilema\\;(m50): \\;no\\;se\\;evitan\\;ambos"],
        contexto=("La política monetaria de EE.UU. es el shock externo que "
                  "gobierna el ciclo financiero de los emergentes. Cuando la "
                  "Reserva Federal sube tasas, el capital fluye hacia el dólar (la "
                  "UIP de m48) y los emergentes enfrentan el dilema del trilema "
                  "(m50): defender su moneda subiendo la tasa local — importando la "
                  "recesión de la FED — o dejarla flotar, aceptando depreciación e "
                  "inflación importada (m85). El 'taper tantrum' de 2013 (cuando la "
                  "FED solo INSINUÓ que reduciría estímulos) y el ciclo de ajuste "
                  "de 2022 mostraron que no hay opción indolora. Hélène Rey "
                  "(mención) fue más lejos con su 'dilema, no trilema': el ciclo "
                  "financiero global es tan poderoso que ni siquiera flotar da "
                  "autonomía monetaria plena — los flujos de capital responden al "
                  "apetito de riesgo global más que a los fundamentos locales. Para "
                  "un emergente como el Perú, la defensa se construye ANTES: "
                  "reservas altas (m50), baja dolarización (m84), ancla creíble que "
                  "abarata flotar (m85) — todo lo que convierte un shock de la FED "
                  "de crisis en molestia (m110-m111)."),
        autores=("UIP (m48), trilema (m50); 'dilema no trilema': Rey (2013, "
                 "Jackson Hole — mención); taper tantrum 2013 y ciclo 2022 "
                 "(menciones)."),
        supuestos=[
            "La defensa es un continuo entre subir la tasa (0% depreciación) y flotar (0% subida local): la realidad mezcla ambas.",
            "Sin salida de capitales desordenada: con reservas bajas, flotar puede volverse sudden stop (m87) — aquí es flotación ordenada.",
            "El passthrough (m85) resume cuánto cuesta flotar en inflación: depende de la credibilidad (m40-m41).",
        ],
        ecuaciones=[
            Ecuacion("defender: recesión = f(\\Delta i) \\;;\\; flotar: \\pi_{imp} = pt\\cdot f(\\Delta E)",
                     "los dos costos",
                     "subir la tasa cuesta producto; flotar cuesta inflación importada — el "
                     "trilema (m50) garantiza que al menos uno se paga (verificado)."),
            Ecuacion("credibilidad\\downarrow passthrough \\Rightarrow flotar\\;más\\;barato",
                     "la salida de la credibilidad",
                     "con ancla creíble (m85), flotar cuesta poca inflación y se vuelve la opción "
                     "preferida: la credibilidad AMPLÍA el menú de respuestas (verificado)."),
        ],
        intuicion=("El alza de la FED enseña que la autonomía monetaria de un "
                   "emergente es limitada y CONDICIONAL: depende de cuánto colchón "
                   "construyó en las buenas. Un país con reservas altas, baja "
                   "dolarización y ancla creíble puede dejar flotar su moneda ante "
                   "la FED sin drama — la depreciación es ordenada, la inflación "
                   "importada es baja (passthrough bajo), y no hay sudden stop "
                   "porque las reservas dan confianza. Un país sin esos colchones "
                   "enfrenta el dilema en su forma más cruel: defender con una "
                   "recesión o flotar hacia una crisis. Esta es la lógica profunda "
                   "de por qué el Perú acumuló reservas equivalentes a ~30% del PIB "
                   "(mención): no para usarlas, sino para no tener que elegir entre "
                   "recesión y crisis cuando la FED se mueve (m110-m111)."),
        equilibrio=("El dilema tiene una frontera de posibilidades: cada grado de "
                    "defensa mapea a un par (recesión, depreciación) — no hay punto "
                    "sin costo (verificado). La credibilidad desplaza toda la "
                    "frontera hacia adentro (menos costo para cada opción)."),
        limitaciones=[
            "El dilema de Rey: con ciclo financiero global, ni flotar aísla del todo — la movilidad de capital manda más que el régimen (matiz de m50).",
            "Sin reservas explícitas: un colchón bajo convierte 'flotar' en 'sudden stop' (m87) — el margen importa.",
            "El passthrough es endógeno al tamaño del shock: shocks grandes desanclan y encarecen flotar (no lineal, m85).",
        ],
        evolucion=("Aplica m48+m50+m85 al shock externo más importante para un "
                   "emergente. Conecta con m87 (cuando flotar se vuelve salida de "
                   "capitales) y con m88-m89 (la FED interactúa con el ciclo de "
                   "materias primas). La versión peruana con datos — FED → flujos "
                   "hacia el Perú — es m111."),
    ),
    escenarios=[
        Escenario("defender_el_sol", "subir la tasa local para frenar la salida",
                  {"defensa": 1.0},
                  "cero depreciación pero máxima recesión: importar el apretón de "
                  "la FED para proteger la moneda — el costo interno de la defensa.",
                  cadena=["FED sube i*", "capital quiere salir (m48)",
                          "subo la tasa local para retenerlo", "cero depreciación",
                          "pero recesión interna: importé el apretón"]),
        Escenario("dejar_flotar", "aceptar la depreciación (Perú anclado)",
                  {"defensa": 0.0, "passthrough": 0.15},
                  "el sol se deprecia pero con passthrough bajo la inflación "
                  "importada es leve y la tasa interna queda libre: la ventaja del "
                  "ancla (m85).",
                  cadena=["FED sube i*", "dejo flotar el sol", "E se deprecia (m48)",
                          "passthrough bajo (m40): poca inflación", "tasa interna libre para el ciclo local"]),
        Escenario("emergente_fragil", "flotar sin ancla (passthrough 0.8)",
                  {"defensa": 0.0, "passthrough": 0.8},
                  "la depreciación se repasa entera a precios: flotar sin "
                  "credibilidad es cambiar recesión por inflación alta — el peor de "
                  "los mundos.",
                  cadena=["FED sube i*", "flotar sin ancla", "E se deprecia",
                          "passthrough alto: inflación importada fuerte (m85)",
                          "sin colchones, el dilema es cruel"]),
        Escenario("taper_tantrum", "shock severo de 6 pp (2022)",
                  {"subida_fed": 6.0, "defensa": 0.5},
                  "un ajuste grande de la FED golpea por los dos lados: la magnitud "
                  "del shock global no la controla el emergente — solo su "
                  "preparación.",
                  cadena=["FED ajusta fuerte (2022)", "shock global grande",
                          "defensa parcial: algo de recesión y algo de depreciación",
                          "los colchones (reservas, ancla) deciden el daño"]),
    ],
    verificaciones=[
        Verificacion("no hay salida gratis (recesión O inflación)", _v_no_hay_salida_gratis),
        Verificacion("defender recesa, flotar deprecia (trilema)", _v_defender_recesa),
        Verificacion("el ancla abarata la opción de flotar (m85)", _v_ancla_abarata_flotar),
        Verificacion("las reservas dan margen para flotar ordenado", _v_reservas_dan_margen),
    ],
    notas="La FED exporta su ajuste. La autonomía del emergente es condicional a los colchones que construyó en las buenas.",
)
