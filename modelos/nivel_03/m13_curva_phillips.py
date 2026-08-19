# m13_curva_phillips.py — curva de Phillips original (nivel 3).
#
#   π = πe − α(u − un)      (πe fijo; en la versión de 1958-1960, πe ≈ 0)
# El "menú" entre inflación y desempleo tal como se leyó en los años 60 —
# incluida la historia de su colapso en los 70, que motiva m14.
#
# Procedencia: Phillips (1958, salarios del Reino Unido 1861-1957) y
# Samuelson-Solow (1960) — menciones históricas de conocimiento general,
# no verificadas contra las fuentes.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _pi(u, p):
    return p["pe"] - p["alpha"] * (u - p["un"])


def _curvas(p):
    u = np.linspace(2, 12, 200)
    pi = _pi(u, p)
    return {"lineas": {"curva de Phillips": (u, pi, config.AZUL2),
                       "inflación cero": (u, np.zeros_like(u), config.GRIS)},
            "puntos": [(p["un"], p["pe"], f"tasa natural un={p['un']:.0f}%"),
                       (p["u_actual"], _pi(p["u_actual"], p), "posición elegida")],
            "anotacion": (f"π en u={p['u_actual']:.1f}%: {_pi(p['u_actual'], p):+.1f}%\n"
                          f"'precio' de −1 pp de desempleo: +{p['alpha']:.1f} pp de inflación")}


def _resultados(p):
    return {"π en la posición elegida (%)": _pi(p["u_actual"], p),
            "pendiente (−α)": -p["alpha"],
            "u con inflación cero (%)": p["un"] + p["pe"] / p["alpha"],
            "costo en u de bajar π en 1 pp": 1 / p["alpha"],
            "brecha u − un (pp)": p["u_actual"] - p["un"]}


_P0 = {"alpha": 1.5, "un": 6.0, "pe": 0.0, "u_actual": 4.0}


def _v_natural():
    return abs(_pi(_P0["un"], _P0) - _P0["pe"]) < 1e-12, "en u = un la inflación es exactamente πe"


def _v_pendiente():
    pend = (_pi(8.0, _P0) - _pi(6.0, _P0)) / 2.0
    return abs(pend + _P0["alpha"]) < 1e-12, f"pendiente = −α = {pend:.2f}"


def _v_menu():
    return _pi(4.0, _P0) > _pi(8.0, _P0), ("menos desempleo 'compra' más inflación: el menú "
                                           "que los años 60 creyeron permanente")


MODELO = Modelo(
    id="m13", nivel=3,
    nombre="Curva de Phillips (original)",
    xlabel="Desempleo u (%)", ylabel="Inflación π (%)",
    parametros=[
        Parametro("u_actual", _P0["u_actual"], 2.0, 11.0, 0.5, "Desempleo elegido por la política"),
        Parametro("alpha", _P0["alpha"], 0.3, 3.0, 0.1, "Sensibilidad α (pendiente)"),
        Parametro("un", _P0["un"], 3.0, 9.0, 0.5, "Tasa natural de desempleo un"),
        Parametro("pe", _P0["pe"], 0.0, 8.0, 0.5, "Inflación esperada πe (fija aquí)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("A. W. Phillips (1958) graficó casi un siglo de datos británicos "
                  "(1861-1957) y encontró una relación negativa asombrosamente estable "
                  "entre desempleo e inflación salarial. Samuelson y Solow (1960) la "
                  "trasladaron a EE.UU. y la presentaron como un MENÚ de política: la "
                  "sociedad podía 'comprar' menos desempleo aceptando más inflación. "
                  "Los años 60 gobernaron con esa carta sobre la mesa."),
        autores=("Phillips (1958); Samuelson y Solow (1960) la bautizaron y la volvieron "
                 "herramienta de política; era la pieza que le faltaba al IS-LM para "
                 "hablar de inflación."),
        supuestos=[
            "Las expectativas de inflación (πe) están FIJAS: los trabajadores no incorporan la inflación pasada al negociar salarios — el supuesto que los 70 demolieron.",
            "La relación es estable y explotable por la política (un 'menú').",
            "un (tasa natural) resume fricciones estructurales del mercado laboral, no elegibles por demanda.",
        ],
        ecuaciones=[
            Ecuacion("\\pi = \\pi^e - \\alpha\\,(u - u_n)", "curva de Phillips",
                     "con desempleo bajo (mercado laboral apretado) los salarios — y con ellos los "
                     "precios — se aceleran; α mide cuánto. πe es el ancla: aquí, una constante."),
        ],
        intuicion=("Es la cara 'laboral' de la demanda agregada: expandir demanda (m10) "
                   "aprieta el mercado de trabajo, y el poder de negociación empuja "
                   "salarios y precios. Mientras nadie ajuste sus expectativas, el "
                   "gobierno puede ELEGIR un punto de la curva — esa es la lectura "
                   "de menú que hizo la política de los 60."),
        equilibrio=("No hay equilibrio interno: cada punto es una combinación (u, π) "
                    "sostenida por la política de demanda. La 'estabilidad' de la curva "
                    "misma es el supuesto crítico — y resultó falso."),
        limitaciones=[
            "COLAPSÓ empíricamente en los años 70: EE.UU. y Europa vivieron inflación Y desempleo altos a la vez (estanflación) — puntos imposibles para esta curva.",
            "Friedman (1968) y Phelps (1967) explicaron por qué ANTES del colapso: πe no se queda quieta; los trabajadores aprenden.",
            "Confunde una correlación de corto plazo con una relación estructural explotable — el ejemplo canónico de la crítica de Lucas (m42).",
        ],
        evolucion=("m14 le añade lo que faltaba: expectativas que se mueven. El menú se "
                   "vuelve transitorio, la curva de largo plazo se hace VERTICAL en un, "
                   "y explotar el trade-off pasa a costar aceleración inflacionaria. Es "
                   "el episodio más didáctico del currículo sobre cómo un modelo muere "
                   "por sus datos — y renace corregido."),
    ),
    escenarios=[
        Escenario("pleno_empleo_60s", "la política empuja u hasta 4% (bajo un=6%)",
                  {"u_actual": 4.0},
                  "π sube a +3%: el punto exacto que los 60 creyeron sostenible para "
                  "siempre — m14 muestra qué pasa cuando πe despierta."),
        Escenario("disciplina", "se tolera u=8% para enfriar precios",
                  {"u_actual": 8.0},
                  "π cae a −3% (deflación): el mismo menú leído al revés."),
        Escenario("curva_empinada", "salarios muy sensibles (α = 2.5)",
                  {"alpha": 2.5},
                  "cada punto de desempleo 'compra' más desinflación: α es el término de "
                  "intercambio del menú."),
    ],
    verificaciones=[
        Verificacion("π(un) = πe", _v_natural),
        Verificacion("pendiente = −α", _v_pendiente),
        Verificacion("trade-off: menos u, más π", _v_menu),
    ],
    notas="La curva que los 70 rompieron: m14 cuenta la reconstrucción (Friedman-Phelps).",
)
