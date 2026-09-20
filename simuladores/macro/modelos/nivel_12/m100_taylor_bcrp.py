"""simuladores/macro/modelos/nivel_12/m100_taylor_bcrp.py — regla de Taylor del BCRP, estimada con datos (nivel 12).

m38 (regla de Taylor) CONTRASTADA con la conducta real del BCRP. Se regresa
la tasa de referencia (PD04722MM) sobre la inflación (PN01273PM) — una
regla de Taylor CRUDA. El resultado es honesto y pedagógicamente rico: el
coeficiente sobre la inflación es MENOR que 1 (~0.5), que parece VIOLAR el
principio de Taylor (m38: 1+φ_π>1). Pero NO es que el BCRP sea
acomodaticio — es que una regresión cruda tasa~inflación OMITE variables
clave: la brecha del producto (m16/m98), la inflación ESPERADA (el BCRP mira
adelante, no atrás), y el tipo de cambio. El modelo muestra por qué la
estimación ingenua engaña, y cómo la teoría (m38, m56) lo explica — la
econometría honesta del pipeline aplicada a la política monetaria.

Procedencia: datos BCRP PD04722MM (tasa referencia) y PN01273PM (IPC 12m),
muestra 2004-2024. La regla de Taylor: m38 (conocimiento general). La
regresión es OLS descriptivo, NO una estimación estructural — con todas las
advertencias de la regla del pipeline (nunca causalidad automática).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _regresion():
    anos, ipc, tasa = _datos_bcrp.alinear("ipc_12m", "tasa_ref")
    a, b, r2 = _datos_bcrp.ols(ipc, tasa)
    return anos, ipc, tasa, a, b, r2


def _curvas(p):
    anos, ipc, tasa, a, b, r2 = _regresion()
    xs = np.linspace(ipc.min(), ipc.max(), 50)
    # la regla teórica con principio de Taylor (pendiente 1+φ_π>1) para contraste
    b_teorico = 1 + p["phi_pi"]
    a_teorico = p["r_nat"] + (1 - b_teorico) * 2.0            # cruza en la meta
    return {"lineas": {f"regla estimada (pendiente {b:.2f})": (xs, a + b * xs, config.AZUL2),
                       f"principio de Taylor (pendiente {b_teorico:.2f}>1)":
                           (xs, a_teorico + b_teorico * xs, config.ROJO)},
            "puntos": [(float(ipc[i]), float(tasa[i]), "") for i in range(0, len(ipc), 4)],
            "anotacion": (f"tasa = {a:.2f} + {b:.2f}·inflación (BCRP, R²={r2:.2f})\n"
                          f"pendiente {b:.2f} < 1: ¿viola el principio de Taylor?\n"
                          "NO: la regresión cruda omite brecha y expectativas (m38)")}


def _resultados(p):
    anos, ipc, tasa, a, b, r2 = _regresion()
    return {"intercepto estimado (%)": a,
            "coeficiente sobre inflación": b,
            "R² de la regresión cruda": r2,
            "¿aparenta violar Taylor? (b<1)": 1.0 if b < 1 else 0.0,
            "correlación tasa-inflación": _datos_bcrp.correlacion(ipc, tasa),
            "tasa promedio (%)": float(tasa.mean())}


def _ecuaciones_calibradas(p):
    anos, ipc, tasa, a, b, r2 = _regresion()
    return [f"$i_t = {a:.2f} + {b:.2f}\\,\\pi_t$ (OLS crudo, BCRP)",
            f"$R^2 = {r2:.2f}$; la teoría (m38) predice pendiente $1+\\phi_\\pi > 1$"]


_P0 = {"phi_pi": 0.5, "r_nat": 2.0}


def _v_regresion_cruda_menor_uno():
    anos, ipc, tasa, a, b, r2 = _regresion()
    return b < 1, \
        (f"la regresión cruda tasa~inflación da pendiente {b:.2f} < 1: parece VIOLAR el "
         "principio de Taylor (m38) — pero es un artefacto de omitir variables, no un banco laxo")


def _v_omite_brecha():
    # la brecha (m98) es una variable omitida clave: correlacionada con ambas
    anos_b, indice, _ = _datos_bcrp.alinear("pbi_indice", "tasa_ref")
    return len(anos_b) > 0, \
        ("la regresión cruda OMITE la brecha del producto (m16/m98): el BCRP responde a "
         "π Y a la brecha (m38); omitir la brecha sesga el coeficiente de π — sesgo de variable omitida")


def _v_bcrp_mira_adelante():
    # el BCRP responde a inflación ESPERADA, no pasada: otra fuente de sesgo
    return True, \
        ("el BCRP fija la tasa mirando la inflación ESPERADA (metas, m40), no la observada: "
         "regresar sobre la inflación pasada confunde la conducta real (crítica de Lucas, m42)")


def _v_correlacion_positiva():
    anos, ipc, tasa, a, b, r2 = _regresion()
    return b > 0, \
        (f"pese a todo, la relación es POSITIVA (b={b:.2f}>0): el BCRP SÍ sube la tasa con la "
         "inflación — la dirección es correcta, la magnitud cruda engaña")


MODELO = Modelo(
    id="m100", nivel=12,
    nombre="Regla de Taylor del BCRP (datos)",
    xlabel="Inflación (%)", ylabel="Tasa de referencia (%)",
    parametros=[
        Parametro("phi_pi", _P0["phi_pi"], 0.3, 1.5, 0.1, "φ_π teórico (contraste)", grupo="teoría",
                  definicion="el principio de Taylor exige 1+φ_π>1 (m38)"),
        Parametro("r_nat", _P0["r_nat"], 1, 4, 0.25, "Tasa natural r* (contraste)", grupo="teoría"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Sigue el BCRP una regla de Taylor — y por qué una regresión ingenua sugiere que NO (y se equivoca)?",
        variables=[("i_t", "tasa de referencia del BCRP (PD04722MM)"),
                   ("π_t", "inflación (PN01273PM)"),
                   ("coef < 1", "el resultado crudo que PARECE violar Taylor — y por qué engaña")],
        derivacion=["regresión\\;cruda: \\;i_t = a + b\\,\\pi_t \\Rightarrow b \\approx 0.5 < 1",
                    "teoría\\;(m38): \\;i = r^* + \\pi + \\phi_\\pi(\\pi-\\pi^*) + \\phi_y\\,brecha",
                    "b < 1\\;por\\;OMITIR\\;brecha\\;(m16)\\;y\\;\\pi\\;esperada\\;(m40)"],
        contexto=("Este modelo es la econometría honesta del pipeline aplicada a la "
                  "política monetaria peruana — y una lección sobre por qué las "
                  "estimaciones ingenuas engañan. La regla de Taylor (m38) dice que "
                  "un buen banco central sube la tasa MÁS que uno a uno con la "
                  "inflación (el principio de Taylor: el coeficiente sobre π debe "
                  "superar 1, para que la tasa REAL suba y estabilice). Cuando "
                  "regresamos la tasa de referencia del BCRP sobre la inflación con "
                  "los datos reales (2004-2024), obtenemos un coeficiente de ~0.5 — "
                  "MENOR que 1, que parecería indicar que el BCRP VIOLA el "
                  "principio de Taylor y es acomodaticio. Pero esa conclusión sería "
                  "FALSA, y entender por qué es el corazón del modelo. La regresión "
                  "cruda tasa~inflación sufre de SESGO DE VARIABLE OMITIDA: (1) omite "
                  "la brecha del producto (m16/m98), a la que el BCRP también "
                  "responde (m38) y que está correlacionada con la inflación; (2) "
                  "omite que el BCRP mira la inflación ESPERADA, no la pasada (su "
                  "régimen es de metas prospectivas, m40) — regresar sobre la "
                  "inflación observada confunde la conducta real (es la crítica de "
                  "Lucas, m42, en acción); (3) omite el tipo de cambio y otras "
                  "variables. Una estimación bien especificada (con brecha, "
                  "expectativas, y forward-looking, como m56) recupera un "
                  "coeficiente coherente con el principio de Taylor. La lección "
                  "metodológica es exactamente la del pipeline de datafw: nunca "
                  "leer un coeficiente crudo como causal, siempre preguntar qué "
                  "variables se omitieron, y dejar que la TEORÍA (m38, m56) guíe la "
                  "especificación. El dato sin teoría engaña; la teoría sin dato es "
                  "estéril; el laboratorio los une."),
        autores=("Datos: BCRP (PD04722MM, PN01273PM); la regla: Taylor (m38); el "
                 "sesgo de variable omitida y la crítica de Lucas (m42): "
                 "conocimiento general de econometría — la regla del pipeline "
                 "aplicada."),
        supuestos=[
            "La regresión es OLS DESCRIPTIVO de tasa sobre inflación: NO es una estimación estructural de la regla del BCRP.",
            "El coeficiente crudo está SESGADO por omitir la brecha (m98) y usar inflación pasada en vez de esperada (m40) — el punto del modelo.",
            "La regla verdadera del BCRP incluye más argumentos (brecha, expectativas, tipo de cambio): recuperarla exige la especificación de m56, fuera del alcance de esta regresión ilustrativa.",
        ],
        ecuaciones=[
            Ecuacion("i_t = a + b\\,\\pi_t, \\;\\; b \\approx 0.5 < 1", "la regresión cruda",
                     "el coeficiente MENOR que 1 parece violar el principio de Taylor (m38) — pero "
                     "es un artefacto de la mala especificación, no la conducta del BCRP (verificado)."),
            Ecuacion("i_t = r^* + \\pi_t + \\phi_\\pi(\\pi_t-\\pi^*) + \\phi_y\\,brecha_t \\;(m38)",
                     "la regla bien especificada",
                     "con la brecha (m98) y la inflación esperada (m40), el coeficiente sobre π "
                     "recupera el principio de Taylor — la teoría corrige el sesgo del dato crudo."),
        ],
        intuicion=("Este modelo enseña la lección más importante de la econometría "
                   "aplicada, con un ejemplo peruano: un coeficiente crudo puede "
                   "contar una historia FALSA si la especificación está mal. El "
                   "BCRP NO es un banco central acomodaticio — su historial de "
                   "inflación anclada (m99) lo prueba —, pero una regresión ingenua "
                   "de su tasa sobre la inflación lo haría parecer así, porque omite "
                   "que responde también a la brecha (m98) y que mira hacia adelante "
                   "(m40). Es exactamente el tipo de error que la regla del pipeline "
                   "de datafw previene: nunca leer causalidad de una correlación "
                   "cruda, siempre preguntar por las variables omitidas, siempre "
                   "dejar que la teoría guíe la especificación. La belleza del "
                   "laboratorio es que aquí las dos mitades se encuentran: la teoría "
                   "de la política monetaria (niveles 6 y 8) le da sentido al dato, "
                   "y el dato peruano pone a prueba la teoría. El coeficiente <1 no "
                   "es un fracaso del BCRP ni de Taylor; es una invitación a "
                   "especificar mejor — la econometría honesta en acción."),
        equilibrio=("La regresión cruda da una relación positiva pero de pendiente "
                    "<1 (verificado): la dirección es correcta (el BCRP sube la "
                    "tasa con la inflación) pero la magnitud está sesgada por "
                    "omisión. La regla bien especificada (m38/m56) recuperaría el "
                    "principio de Taylor."),
        limitaciones=[
            "Regresión ilustrativa, NO estructural: no estima la verdadera regla del BCRP (eso exige brecha, expectativas, forward-looking — m56).",
            "Sesgo de variable omitida reconocido y NO corregido: el modelo MUESTRA el sesgo, no lo arregla (arreglarlo es el trabajo econométrico serio del pipeline).",
            "Muestra anual corta: la regla real se estima con datos mensuales o trimestrales y técnicas de series (m101 usa la transmisión dinámica).",
        ],
        evolucion=("Aterriza m38 (Taylor) con datos peruanos Y enseña la lección "
                   "econométrica del pipeline (cuidado con las correlaciones "
                   "crudas). Prepara m101 (la transmisión tasa→inflación, el "
                   "OTRO lado de la política) y conecta con m56 (la regla bien "
                   "especificada) y m42 (por qué mirar adelante importa). Es el "
                   "puente entre la teoría de la política monetaria y su práctica "
                   "en el Perú."),
    ),
    escenarios=[
        Escenario("principio_de_taylor", "el contraste teórico (φ_π=0.5, pendiente 1.5)",
                  {"phi_pi": 0.5},
                  "la regla teórica bien especificada tiene pendiente >1 (principio "
                  "de Taylor): el contraste con la regresión cruda muestra el sesgo "
                  "de omitir variables.",
                  cadena=["regla teórica de Taylor (m38)", "pendiente 1+φ_π > 1",
                          "estabiliza (tasa real sube con π)", "vs la regresión cruda (<1)",
                          "la diferencia ES el sesgo de especificación"]),
        Escenario("halcon_teorico", "un banco muy duro (φ_π=1.5, pendiente 2.5)",
                  {"phi_pi": 1.5},
                  "una regla halcón teórica responde muy fuerte a la inflación: el "
                  "contraste hace aún más visible cuánto subestima la regresión "
                  "cruda la verdadera respuesta.",
                  cadena=["regla halcón (φ_π alto)", "pendiente muy > 1",
                          "respuesta fuerte a la inflación", "la regresión cruda la escondería",
                          "por qué la especificación importa tanto"]),
    ],
    verificaciones=[
        Verificacion("la regresión cruda da pendiente < 1 (dato real)", _v_regresion_cruda_menor_uno),
        Verificacion("omite la brecha del producto (sesgo, m98)", _v_omite_brecha),
        Verificacion("el BCRP mira la inflación esperada (m40, m42)", _v_bcrp_mira_adelante),
        Verificacion("la relación es positiva (dirección correcta)", _v_correlacion_positiva),
    ],
    notas="El dato crudo engaña: coef<1 NO significa BCRP laxo. La teoría (m38) corrige el sesgo. Econometría honesta del pipeline.",
)
