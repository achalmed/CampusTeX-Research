# m78_trampa_deuda.py — la trampa de deuda (nivel 10).
#
# El caso extremo de m64 con r > g: cuando la aritmética es cruel Y el
# esfuerzo primario no alcanza, la deuda diverge sin límite. Peor: en la
# trampa, el ajuste es CONTRAPRODUCENTE por partida doble —
#   (a) austeridad contrae g (m69): r−g se agranda;
#   (b) la deuda alta sube la prima r (m76): r−g se agranda de nuevo.
# El modelo muestra las TRES salidas históricas cuando el ajuste fiscal no
# basta:  crecer (subir g), licuar (inflación/señoreaje, m36) o reestructurar
# (default/quita, m76). La trampa es donde el nivel 9 (aritmética) se
# encuentra con el nivel 10 (los lazos endógenos que la vuelven explosiva).
#
# Procedencia: dinámica de m64 en régimen r>g con retroalimentaciones de
# m69 y m76 — decisión de diseño sobre conocimiento general. Calibración
# didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _senda(p, T=None, con_lazos=None):
    T = int(round(T if T is not None else p["T"]))
    con_lazos = p["lazos"] if con_lazos is None else con_lazos
    b = np.empty(T + 1)
    b[0] = p["b0"]
    for t in range(T):
        g_ef = p["g"] - (p["austeridad_g"] * p["sp"] if con_lazos else 0.0)   # ajuste contrae g
        r_ef = p["r"] + (p["prima"] * b[t] / 100 if con_lazos else 0.0)       # deuda sube r
        b[t + 1] = b[t] * (1 + r_ef / 100) / (1 + g_ef / 100) - p["sp"]
    return np.arange(T + 1), b


def _curvas(p):
    t, b_lazos = _senda(p, con_lazos=True)
    t2, b_simple = _senda(p, con_lazos=False)
    return {"lineas": {"deuda CON lazos endógenos (m69+m76)": (t, b_lazos, config.ROJO),
                       "deuda con r,g fijos (m64 ingenuo)": (t2, b_simple, config.AZUL2),
                       "nivel inicial $b_0$": (t, np.full(len(t), p["b0"]), config.GRIS)},
            "anotacion": (f"$r-g = {p['r'] - p['g']:+.1f}$ base; con lazos, se AGRANDA solo\n"
                          f"deuda final: ingenua {float(b_simple[-1]):.0f}%, "
                          f"real {float(b_lazos[-1]):.0f}%\n"
                          "en la trampa, ajustar alimenta la trampa")}


def _resultados(p):
    t, b_lazos = _senda(p, con_lazos=True)
    t2, b_simple = _senda(p, con_lazos=False)
    return {"deuda final CON lazos (%)": float(b_lazos[-1]),
            "deuda final SIN lazos (%)": float(b_simple[-1]),
            "amplificación de los lazos (pp)": float(b_lazos[-1] - b_simple[-1]),
            "r − g base (pp)": p["r"] - p["g"],
            "¿diverge? (b sube en el horizonte)": 1.0 if b_lazos[-1] > p["b0"] else 0.0}


def _ecuaciones_calibradas(p):
    return [f"$b_{{t+1}} = b_t\\frac{{1+r_{{ef}}}}{{1+g_{{ef}}}} - {p['sp']:.1f}$",
            f"$r_{{ef}} = {p['r']:.1f} + {p['prima']:.3f}\\,b$ (m76), "
            f"$g_{{ef}} = {p['g']:.1f} - {p['austeridad_g']:.2f}\\,sp$ (m69)"]


_P0 = {"b0": 90.0, "r": 5.0, "g": 2.0, "sp": 1.0, "prima": 0.02,
       "austeridad_g": 0.3, "lazos": 1.0, "T": 25.0}


def _v_diverge_con_rg():
    t, b = _senda(dict(_P0, prima=0.0, austeridad_g=0.0), con_lazos=True)
    # r>g y sp insuficiente: b crece
    return b[-1] > _P0["b0"], \
        (f"con r>g y sp insuficiente, la deuda DIVERGE de {_P0['b0']:.0f}% a {float(b[-1]):.0f}% "
         "aun sin lazos: la trampa base es la aritmética cruel de m64")


def _v_lazos_amplifican():
    b_con = _senda(_P0, con_lazos=True)[1][-1]
    b_sin = _senda(_P0, con_lazos=False)[1][-1]
    return b_con > b_sin, \
        (f"los lazos endógenos amplifican la divergencia ({b_sin:.0f}%→{b_con:.0f}%): "
         "la deuda sube la prima (m76) y el ajuste contrae g (m69) — dos aceleradores")


def _v_crecer_salva():
    t, b = _senda(dict(_P0, g=7.0), con_lazos=True)     # g > r
    return b[-1] < _P0["b0"], \
        (f"si g sube por encima de r (7%>5%), la deuda CONVERGE hacia abajo ({float(b[-1]):.0f}%): "
         "crecer es la salida más limpia de la trampa (m26, m64 amable)")


def _v_reestructurar_resetea():
    # una quita del 40% en t=0 baja b0 bajo el umbral de divergencia local
    t, b = _senda(dict(_P0, b0=_P0["b0"] * 0.6), con_lazos=True)
    b_sin_quita = _senda(_P0, con_lazos=True)[1][-1]
    return b[-1] < b_sin_quita, \
        (f"una quita del 40% (default, m76) deja la deuda mucho más baja al final "
         f"({float(b[-1]):.0f}% vs {b_sin_quita:.0f}%): reestructurar resetea la aritmética — con su costo")


MODELO = Modelo(
    id="m78", nivel=10,
    nombre="Trampa de deuda",
    xlabel="Año $t$", ylabel="Deuda/PIB $b_t$ (%)",
    parametros=[
        Parametro("prima", _P0["prima"], 0.0, 0.06, 0.005, "Prima endógena (m76)", grupo="lazos",
                  definicion="la deuda sube su propia tasa"),
        Parametro("austeridad_g", _P0["austeridad_g"], 0.0, 0.8, 0.1, "Daño del ajuste a g (m69)",
                  grupo="lazos", definicion="cuánto contrae el crecimiento cada punto de sp"),
        Parametro("sp", _P0["sp"], -1, 4, 0.5, "Esfuerzo primario sp (% PIB)", grupo="decisión"),
        Parametro("g", _P0["g"], 0, 8, 0.5, "Crecimiento base g (%)", grupo="fundamentos"),
        Parametro("r", _P0["r"], 2, 10, 0.5, "Tasa base r (%)", grupo="fundamentos"),
        Parametro("b0", _P0["b0"], 40, 160, 10, "Deuda inicial b0 (%)", grupo="posición"),
        Parametro("lazos", _P0["lazos"], 0, 1, 1, "¿Lazos endógenos activos?", grupo="experimento"),
        Parametro("T", _P0["T"], 10, 40, 5, "Años simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué hay deudas de las que no se sale ajustando — y cuáles son las únicas tres salidas?",
        variables=[("b_t", "la deuda — diverge cuando la trampa se cierra"),
                   ("r_ef, g_ef", "tasa y crecimiento EFECTIVOS: endógenos a la deuda y al ajuste"),
                   ("las 3 salidas", "crecer, licuar o reestructurar — no hay una cuarta")],
        derivacion=["b_{t+1} = b_t\\frac{1+r_{ef}}{1+g_{ef}} - sp \\;\\;(m64)",
                    "r_{ef} = r + \\pi b \\;(m76), \\quad g_{ef} = g - \\kappa\\,sp \\;(m69)",
                    "trampa: \\;r_{ef} > g_{ef}\\;y\\;sp\\;insuficiente \\Rightarrow b\\to\\infty"],
        contexto=("La trampa de deuda es donde el nivel 9 (la aritmética de m64) "
                  "se encuentra con el nivel 10 (los lazos endógenos que la vuelven "
                  "explosiva). La aritmética base ya era cruel con r>g; los dos "
                  "lazos la vuelven una trampa: (1) ajustar contrae el crecimiento "
                  "(m69), agrandando r−g; (2) la deuda alta sube la prima de riesgo "
                  "(m76), subiendo r y agrandando r−g otra vez. El resultado es que "
                  "más esfuerzo puede producir MÁS deuda — la austeridad como pala "
                  "para salir de un pozo. Cuando el ajuste fiscal no basta, la "
                  "historia registra solo tres salidas: crecer (la más limpia, pero "
                  "no siempre disponible), licuar con inflación (m36, el impuesto "
                  "silencioso) o reestructurar con quita (m76, el default "
                  "ordenado). Grecia intentó ajustar (falló, m69); Argentina "
                  "reestructuró (repetidamente); los países del euro fueron "
                  "rescatados. Nadie ajusta su salida de una trampa profunda."),
        autores=("Síntesis de m64 (aritmética), m69 (austeridad autodestructiva) y "
                 "m76 (prima endógena); la taxonomía de salidas — crecer/licuar/"
                 "reestructurar — es patrimonio del análisis de crisis de deuda "
                 "(Reinhart-Rogoff, menciones)."),
        supuestos=[
            "Lazos lineales (prima ∝ b, daño a g ∝ sp): la realidad es más convexa, lo que hace la trampa más abrupta.",
            "Sin default parcial dentro de la senda: la reestructuración se modela como un reset de b0.",
            "g exógeno salvo el daño del ajuste: la salida 'crecer' asume que se PUEDE (reformas, suerte, términos de intercambio — m105).",
        ],
        ecuaciones=[
            Ecuacion("r_{ef} - g_{ef} = (r - g) + \\pi b + \\kappa\\,sp", "los dos aceleradores",
                     "la brecha que decide todo (m64) se agranda sola con la deuda (prima) y con "
                     "el propio ajuste (recesión): la trampa se cierra desde dos lados."),
            Ecuacion("salidas: \\;g\\uparrow \\;\\lor\\; inflación \\;\\lor\\; quita",
                     "las únicas tres puertas",
                     "crecer licúa por el denominador (m64), la inflación por el numerador real "
                     "(m36), la quita por decreto (m76): no existe una cuarta — el ajuste solo, no basta."),
        ],
        intuicion=("La trampa de deuda es la lección más dura del currículo fiscal: "
                   "hay pozos de los que no se sale cavando. Cuando r_ef supera a "
                   "g_ef y el esfuerzo factible no alcanza, cada año de 'disciplina' "
                   "puede dejar más deuda que el anterior, porque el ajuste mata el "
                   "crecimiento y la deuda encarece la tasa. Reconocer la trampa a "
                   "tiempo es la diferencia entre una reestructuración ordenada y "
                   "una década perdida. La defensa, como siempre en este nivel, es "
                   "preventiva: no entrar — mantener r−g favorable (crecer, m26; "
                   "credibilidad para prima baja, m76) y deuda moderada (m64-m65) "
                   "en las buenas. El Perú construyó ese colchón deliberadamente "
                   "(m108)."),
        equilibrio=("Sin trampa (g>r o sp suficiente): b converge a un nivel "
                    "finito. En la trampa (r_ef>g_ef, sp insuficiente): b DIVERGE — "
                    "no hay equilibrio, solo la elección entre las tres salidas. "
                    "Los lazos endógenos verificados como amplificadores de la "
                    "divergencia base."),
        limitaciones=[
            "Determinista: la trampa real interactúa con las profecías autocumplidas de m76 (el salto al equilibrio malo puede meterte en la trampa de golpe).",
            "Las tres salidas tienen costos no modelados: crecer requiere reformas que tardan, licuar destruye el ahorro, reestructurar cierra el acceso al crédito (Reinhart-Rogoff, mención).",
            "Sin moneda extranjera: la deuda en dólares hace que 'licuar' no funcione (la inflación no reduce deuda en dólares) — cierra una salida (m84).",
        ],
        evolucion=("Cierra la aritmética fiscal de crisis, uniendo m64/m69/m76 en "
                   "una sola dinámica. El paso final del nivel es agregarlo todo: "
                   "m79 (el lazo real-financiero) y m80 (la crisis sistémica) "
                   "muestran cómo la trampa de un país se vuelve el problema de "
                   "todos. La sostenibilidad peruana con datos MEF es m108."),
    ),
    escenarios=[
        Escenario("trampa_cerrada", "r>g, ajuste insuficiente, lazos activos",
                  {"sp": 1.0, "lazos": 1.0},
                  "la deuda diverge de 90% al alza pese al esfuerzo primario: cavar "
                  "hace más profundo el pozo — la trampa en acción.",
                  cadena=["r>g y sp bajo", "b sube", "la prima sube r (m76)",
                          "el ajuste contrae g (m69)", "r−g se agranda solo",
                          "más deuda pese al esfuerzo: divergencia"]),
        Escenario("salida_crecer", "reformas suben g a 7% (> r)",
                  {"g": 7.0},
                  "la deuda converge hacia abajo: cuando g supera a r, el "
                  "denominador de m64 licúa la deuda sin dolor — la salida más "
                  "limpia, si está disponible.",
                  cadena=["g > r (crecimiento, m26)", "el denominador corre más que la deuda",
                          "r−g se vuelve favorable", "b converge a la baja",
                          "crecer es la mejor política de deuda"]),
        Escenario("salida_reestructurar", "quita del 40% (default ordenado, m76)",
                  {"b0": 54.0},
                  "empezar desde 54% en vez de 90% deja la deuda mucho más baja: "
                  "la reestructuración resetea la aritmética — con el costo de "
                  "perder acceso al crédito (Argentina, mención).",
                  cadena=["default/quita negociada", "b0 cae de golpe",
                          "la nueva senda parte más abajo", "posible convergencia",
                          "costo: exclusión del mercado (Reinhart-Rogoff)"]),
        Escenario("sin_lazos", "la misma trampa con r,g fijos (m64 ingenuo)",
                  {"lazos": 0.0},
                  "la deuda diverge pero MUCHO menos: los lazos endógenos "
                  "(prima+recesión) son lo que convierte una aritmética adversa en "
                  "una trampa explosiva.",
                  cadena=["r,g fijos (sin retroalimentación)", "divergencia aritmética base",
                          "pero sin la aceleración de m76+m69", "la trampa 'ingenua' es más lenta",
                          "los lazos son el veneno"]),
    ],
    verificaciones=[
        Verificacion("r>g con sp insuficiente ⇒ la deuda diverge", _v_diverge_con_rg),
        Verificacion("los lazos endógenos amplifican la divergencia", _v_lazos_amplifican),
        Verificacion("crecer (g>r) salva: convergencia a la baja", _v_crecer_salva),
        Verificacion("reestructurar resetea la aritmética", _v_reestructurar_resetea),
    ],
    notas="Pozos de los que no se sale cavando: tres salidas (crecer/licuar/reestructurar), ninguna cuarta.",
)
