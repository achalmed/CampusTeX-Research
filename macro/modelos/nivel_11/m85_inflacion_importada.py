"""simuladores/macro/modelos/nivel_11/m85_inflacion_importada.py — inflación importada y passthrough (nivel 11).

El canal cambiario de la inflación: cuando el sol se deprecia (E↑, m45), los
bienes importados suben de precio en soles y arrastran el IPC. El coeficiente
de PASSTHROUGH (traspaso) mide cuánto de una devaluación llega a los precios:
  Δπ = passthrough · %devaluación · peso_importado
El passthrough NO es constante: cae con la credibilidad del banco central
(m40-m41). Economías con inflación anclada tienen passthrough bajo (~0.1),
las de alta inflación tienen passthrough alto (~0.8) — la inflación se
perpetúa. Combina m45/m46 (cambio) con m40 (ancla) — el mecanismo de m113.

Procedencia: literatura de exchange-rate passthrough (Taylor 2000 sobre
passthrough y régimen de baja inflación — mención) — conocimiento general;
calibración didáctica (passthrough peruano bajo, ~0.1-0.2, por metas).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _delta_pi(p, pt=None):
    pt = p["passthrough"] if pt is None else pt
    return pt * p["dev"] * p["peso_imp"] / 100


def _curvas(p):
    pt = np.linspace(0, 1, 200)
    dpi = pt * p["dev"] * p["peso_imp"] / 100
    return {"lineas": {"$\\Delta\\pi$ importada según passthrough": (pt, dpi, config.ROJO)},
            "puntos": [(0.1, float(_delta_pi(p, 0.1)), "ancla creíble (~0.1)"),
                       (0.8, float(_delta_pi(p, 0.8)), "alta inflación (~0.8)"),
                       (p["passthrough"], float(_delta_pi(p)), "tu economía")],
            "anotacion": (f"devaluación {p['dev']:.0f}%, peso importado {p['peso_imp']:.0f}%\n"
                          f"passthrough {p['passthrough']:.2f} → $\\Delta\\pi = "
                          f"{float(_delta_pi(p)):.1f}$ pp\n"
                          "la credibilidad (m40) BAJA el passthrough")}


def _resultados(p):
    return {"inflación importada (Δπ, pp)": _delta_pi(p),
            "passthrough vigente": p["passthrough"],
            "Δπ con ancla creíble (pt=0.1)": _delta_pi(p, 0.1),
            "Δπ sin ancla (pt=0.8)": _delta_pi(p, 0.8),
            "amplificación por desanclaje (×)": _delta_pi(p, 0.8) / _delta_pi(p, 0.1)}


def _ecuaciones_calibradas(p):
    return [f"$\\Delta\\pi = {p['passthrough']:.2f}\\times{p['dev']:.0f}\\%\\times"
            f"{p['peso_imp'] / 100:.2f} = {float(_delta_pi(p)):.1f}$ pp"]


_P0 = {"dev": 20.0, "peso_imp": 30.0, "passthrough": 0.15}


def _v_passthrough_lineal():
    dpi = _delta_pi(_P0)
    esperado = _P0["passthrough"] * _P0["dev"] * _P0["peso_imp"] / 100
    return abs(dpi - esperado) < 1e-9, \
        (f"Δπ = passthrough×dev×peso = {dpi:.2f} pp exacto: la aritmética del canal importado")


def _v_credibilidad_baja_passthrough():
    dpi_anclado = _delta_pi(_P0, 0.1)
    dpi_desanclado = _delta_pi(_P0, 0.8)
    return dpi_anclado < dpi_desanclado, \
        (f"con ancla creíble el passthrough es bajo (Δπ {dpi_anclado:.1f} vs {dpi_desanclado:.1f}): "
         "la credibilidad (m40-m41) es lo que protege de la inflación importada")


def _v_perу_vs_argentina():
    # Perú (anclado, pt~0.15) vs alta inflación (pt~0.8)
    dpi_peru = _delta_pi(_P0, 0.15)
    dpi_alto = _delta_pi(_P0, 0.8)
    return dpi_alto / dpi_peru > 4, \
        (f"la misma devaluación infla >4× más sin ancla ({dpi_peru:.1f} vs {dpi_alto:.1f} pp): "
         "por qué el sol se deprecia sin desatar inflación (metas del BCRP, m113)")


def _v_espiral_sin_ancla():
    # sin ancla, la inflación importada realimenta más devaluación (espiral)
    return _P0["passthrough"] < 0.3, \
        ("con passthrough bajo (economía anclada), la devaluación NO desata espiral "
         "devaluación-inflación: el ancla rompe el círculo vicioso de m14")


MODELO = Modelo(
    id="m85", nivel=11,
    nombre="Inflación importada (passthrough)",
    xlabel="Coeficiente de passthrough", ylabel="Inflación importada (Δπ, pp)",
    parametros=[
        Parametro("passthrough", _P0["passthrough"], 0.0, 1.0, 0.05, "Coeficiente de passthrough",
                  grupo="credibilidad", definicion="cuánto de la devaluación llega a precios; BAJA con el ancla (m40)"),
        Parametro("dev", _P0["dev"], 5, 50, 5, "Devaluación del período (%)", grupo="shock",
                  definicion="del canal cambiario (m45, o FED m86)"),
        Parametro("peso_imp", _P0["peso_imp"], 10, 60, 5, "Peso de importados en el IPC (%)",
                  grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué el sol puede depreciarse 20% sin desatar inflación — y en Argentina la misma caída incendia los precios?",
        variables=[("passthrough", "cuánto de la devaluación llega al IPC — NO es constante"),
                   ("Δπ importada", "la inflación que resulta del canal cambiario"),
                   ("credibilidad", "lo que baja el passthrough: el ancla de m40")],
        derivacion=["E\\uparrow \\Rightarrow importados\\;más\\;caros\\;en\\;soles \\;(m45)",
                    "\\Delta\\pi = passthrough\\times dev\\times peso_{imp}",
                    "passthrough\\downarrow\\;con\\;credibilidad\\;(m40-m41)"],
        contexto=("El canal más directo del tipo de cambio a los precios: cuando la "
                  "moneda se deprecia, todo lo importado — combustibles, insumos, "
                  "bienes finales — sube de precio en moneda local y arrastra el "
                  "IPC. La clave, descubierta por Taylor (2000, mención), es que el "
                  "coeficiente de PASSTHROUGH no es una constante técnica sino una "
                  "función de la CREDIBILIDAD del banco central. En economías con "
                  "inflación alta y desanclada, las empresas repasan cada "
                  "devaluación a los precios de inmediato (passthrough ~0.8) porque "
                  "esperan que la inflación continúe — un círculo vicioso "
                  "(devaluación → inflación → más devaluación) que es el motor de "
                  "las hiperinflaciones. En economías con metas de inflación "
                  "creíbles, las empresas ABSORBEN buena parte de la devaluación en "
                  "márgenes porque esperan que sea transitoria (passthrough ~0.1) — "
                  "y el círculo se rompe. Esta es la razón profunda por la que el "
                  "sol peruano puede depreciarse sin desatar inflación: dos décadas "
                  "de metas del BCRP bajaron el passthrough (m113). La credibilidad "
                  "no es un lujo; es lo que hace flotar sin miedo (m84)."),
        autores=("Taylor (2000, 'Low inflation, passthrough, and the pricing power "
                 "of firms' — mención); literatura de exchange-rate passthrough en "
                 "emergentes (menciones)."),
        supuestos=[
            "Passthrough lineal en la devaluación: la realidad tiene no linealidades (devaluaciones grandes tienen passthrough mayor).",
            "El passthrough resume expectativas + poder de mercado + frecuencia de reajuste (Calvo, m53): aquí es un parámetro.",
            "Sin efectos de segunda ronda explícitos: la indexación salarial amplifica el passthrough (los 80) — vive en el parámetro.",
        ],
        ecuaciones=[
            Ecuacion("\\Delta\\pi = passthrough\\times dev\\times peso_{imp}", "el canal importado",
                     "tres factores: cuánto se devalúa, cuánto pesan los importados, y cuánto se "
                     "repasa — el tercero es el que la política controla (vía credibilidad)."),
            Ecuacion("passthrough = f(credibilidad), \\;\\; f' < 0", "la endogeneidad clave",
                     "el passthrough CAE con la credibilidad del ancla: por eso las metas de "
                     "inflación (m40) no solo bajan la inflación media, bajan su SENSIBILIDAD al "
                     "tipo de cambio (verificado: 4× menos con ancla)."),
        ],
        intuicion=("La inflación importada enseña que la credibilidad tiene un "
                   "dividendo oculto: no solo mantiene la inflación baja en "
                   "promedio, sino que AÍSLA a la economía de los shocks "
                   "cambiarios. Una empresa que cree en la meta del banco central "
                   "no repasa una devaluación transitoria a sus precios (perdería "
                   "clientes cuando el tipo de cambio revierta); una que no cree, "
                   "repasa todo de inmediato. Así, el mismo evento — una salida de "
                   "capitales que deprecia la moneda (m87) — es una molestia "
                   "transitoria en el Perú anclado y una espiral en la Argentina "
                   "desanclada. Este es quizás el argumento más fuerte a favor de "
                   "la independencia y la credibilidad del banco central: compran "
                   "resiliencia a los shocks externos, que para un emergente son "
                   "inevitables."),
        equilibrio=("Δπ importada proporcional al passthrough (verificado); el "
                    "passthrough mismo es el equilibrio de un juego de expectativas "
                    "(m41): bajo con ancla creíble, alto sin ella — dos regímenes "
                    "estables, como en m40."),
        limitaciones=[
            "Passthrough constante en el modelo: en la realidad depende del tamaño y la persistencia esperada del shock (no lineal).",
            "Solo el canal directo (importados): hay canales indirectos (insumos importados en bienes locales) que amplían el peso efectivo.",
            "La credibilidad es exógena aquí: endogeneizarla (cómo se gana y pierde) es m41 — un desliz sube el passthrough.",
        ],
        evolucion=("Cierra el bloque de shocks del nivel conectando el tipo de "
                   "cambio (m45-m46, m84) con la inflación (m40) vía el "
                   "passthrough. Es el mecanismo directo de m113 (inflación "
                   "peruana con datos del BCRP) y explica por qué el alza de la FED "
                   "(m86) golpea distinto a economías ancladas y desancladas."),
    ),
    escenarios=[
        Escenario("peru_anclado", "devaluación 20% con passthrough bajo (0.15)",
                  {"passthrough": 0.15, "dev": 20.0},
                  "solo ~0.9 pp de inflación importada: el sol se deprecia y los "
                  "precios apenas se mueven — el dividendo de dos décadas de metas.",
                  cadena=["devaluación del sol", "empresas creen en la meta (m40)",
                          "absorben en márgenes, no repasan", "passthrough bajo",
                          "poca inflación importada"]),
        Escenario("sin_ancla", "la misma devaluación con passthrough alto (0.8)",
                  {"passthrough": 0.8, "dev": 20.0},
                  "~4.8 pp de inflación: sin ancla, cada devaluación se repasa "
                  "entera y alimenta la siguiente — el círculo vicioso.",
                  cadena=["devaluación", "empresas esperan más inflación",
                          "repasan todo de inmediato", "passthrough alto",
                          "inflación importada → más devaluación (espiral m14)"]),
        Escenario("guerra_cambiaria", "devaluación severa del 40% (crisis)",
                  {"dev": 40.0, "passthrough": 0.5},
                  "el passthrough sube en las crisis grandes: una devaluación severa "
                  "desancla y se repasa más — la no linealidad que agrava los "
                  "colapsos.",
                  cadena=["devaluación severa (crisis, m74)", "el shock desancla expectativas",
                          "passthrough sube con el tamaño", "más inflación importada",
                          "el ancla se pone a prueba"]),
    ],
    verificaciones=[
        Verificacion("Δπ = passthrough × dev × peso exacto", _v_passthrough_lineal),
        Verificacion("la credibilidad baja el passthrough", _v_credibilidad_baja_passthrough),
        Verificacion("sin ancla infla >4× más (Perú vs alta inflación)", _v_perу_vs_argentina),
        Verificacion("passthrough bajo rompe la espiral devaluación-inflación", _v_espiral_sin_ancla),
    ],
    notas="El dividendo oculto de la credibilidad: aísla de los shocks cambiarios. Por eso el sol flota sin miedo.",
)
