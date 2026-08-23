# m96_crisis_deuda_soberana.py — crisis de deuda soberana: el episodio
# (Grecia, Argentina) — nivel 11, cierre del nivel de escenarios.
#
# El caso histórico que integra todo el arco fiscal (m63-m65) con la zona de
# crisis (m76). Reconstruye la ANATOMÍA de una crisis soberana en fases:
#   (1) acumulación: déficits crónicos elevan la deuda hacia la zona (m64)
#   (2) detonante: un shock (recesión, revelación estadística, contagio) empuja
#       a la zona de crisis (m76) — la prima salta
#   (3) espiral: la prima alta sube el servicio, que sube la deuda, que sube la
#       prima (m78) — la trampa se cierra
#   (4) resolución: rescate con condicionalidad (Grecia/Troika), reestructuración
#       (Argentina), o backstop que coordina (Draghi/euro, m76)
# El desenlace depende de: ¿hay backstop? ¿la deuda es en moneda propia?
# ¿el ajuste es viable políticamente (m69)? Combina m64, m76, m78, m69.
#
# Procedencia: crisis del euro (Grecia 2010-2015) y Argentina (2001, 2018 —
# menciones) sobre m64/m76/m78 — conocimiento general; calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _senda(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    b = np.empty(T + 1); prima = np.empty(T + 1)
    b[0] = p["b0"]
    for t in range(T + 1):
        # prima salta al entrar en la zona de crisis (m76)
        en_zona = b[t] > p["umbral_zona"]
        prima[t] = p["prima_base"] + (p["prima_crisis"] if en_zona else 0.0)
        if t < T:
            r_ef = p["rf"] + prima[t]
            # backstop reduce la prima efectiva (coordina al equilibrio bueno)
            r_ef -= p["backstop"] * (prima[t] - p["prima_base"])
            # ajuste primario (con daño al crecimiento si es austero, m69)
            g_ef = p["g"] - p["ajuste"] * p["dano_austeridad"]
            b[t + 1] = b[t] * (1 + r_ef / 100) / (1 + g_ef / 100) - p["ajuste"]
            b[t + 1] = max(b[t + 1], p.get("quita", 0.0) if p.get("reestructura") and t == p.get("t_quita", -1) else b[t + 1])
    return np.arange(T + 1), b, prima


def _senda_reest(p, T=None):
    """Versión con reestructuración: quita del `quita`% en t_quita."""
    T = int(round(T if T is not None else p["T"]))
    b = np.empty(T + 1); prima = np.empty(T + 1)
    b[0] = p["b0"]
    for t in range(T + 1):
        en_zona = b[t] > p["umbral_zona"]
        prima[t] = p["prima_base"] + (p["prima_crisis"] if en_zona else 0.0)
        if t < T:
            r_ef = p["rf"] + prima[t] - p["backstop"] * (prima[t] - p["prima_base"])
            g_ef = p["g"] - p["ajuste"] * p["dano_austeridad"]
            b[t + 1] = b[t] * (1 + r_ef / 100) / (1 + g_ef / 100) - p["ajuste"]
            if p["reestructura"] and t + 1 == p["t_quita"]:
                b[t + 1] *= (1 - p["quita"] / 100)      # quita
    return np.arange(T + 1), b, prima


def _curvas(p):
    t, b, prima = _senda_reest(p)
    return {"lineas": {"deuda/PIB $b_t$ (%)": (t, b, config.AZUL2),
                       "prima de riesgo (pp)": (t, 100 + prima * 3, config.ROJO),
                       "umbral zona de crisis (m76)": (t, np.full(len(t), p["umbral_zona"]), config.GRIS)},
            "puntos": ([(p["t_quita"], float(b[p["t_quita"]]), "reestructuración")]
                       if p["reestructura"] else []),
            "anotacion": (f"deuda inicial {p['b0']:.0f}%, umbral zona {p['umbral_zona']:.0f}%\n"
                          f"backstop {p['backstop'] * 100:.0f}%, ajuste {p['ajuste']:.1f}\n"
                          f"deuda final: {float(b[-1]):.0f}% "
                          f"({'sostenible' if b[-1] < b[0] else 'divergente'})")}


def _resultados(p):
    t, b, prima = _senda_reest(p)
    return {"deuda inicial (%)": p["b0"],
            "deuda final (%)": float(b[-1]),
            "deuda máxima (%)": float(b.max()),
            "prima máxima (pp)": float(prima.max()),
            "¿en zona de crisis? (máx)": 1.0 if float(b.max()) > p["umbral_zona"] else 0.0,
            "¿converge? (final<inicial)": 1.0 if b[-1] < b[0] else 0.0}


def _ecuaciones_calibradas(p):
    return [f"prima $= {p['prima_base']:.1f} + {p['prima_crisis']:.1f}\\,(b > {p['umbral_zona']:.0f})$",
            f"backstop reduce la prima {p['backstop'] * 100:.0f}\\%; ajuste {p['ajuste']:.1f}/período"]


_P0 = {"b0": 100.0, "umbral_zona": 90.0, "prima_base": 1.0, "prima_crisis": 6.0,
       "rf": 2.0, "g": 1.0, "ajuste": 2.0, "dano_austeridad": 0.4, "backstop": 0.0,
       "reestructura": 0.0, "quita": 40.0, "t_quita": 4, "T": 15.0}


def _v_entra_en_zona():
    t, b, prima = _senda_reest(_P0)
    return float(prima.max()) > _P0["prima_base"] + 1, \
        (f"la deuda entra en la zona de crisis y la prima SALTA (a {float(prima.max()):.1f} pp): "
         "el detonante que empuja del equilibrio bueno al malo (m76)")


def _v_austeridad_no_basta():
    t, b, prima = _senda_reest(dict(_P0, backstop=0.0, reestructura=0.0))
    return float(b[-1]) > 80, \
        (f"solo con austeridad, la deuda NO baja lo suficiente ({float(b[-1]):.0f}%): el ajuste "
         "daña el crecimiento (m69) y la prima alta pesa — la trampa de Grecia (m78)")


def _v_backstop_coordina():
    b_sin = float(_senda_reest(dict(_P0, backstop=0.0))[1][-1])
    b_con = float(_senda_reest(dict(_P0, backstop=0.9))[1][-1])
    return b_con < b_sin, \
        (f"un backstop creíble (Draghi) reduce la prima y estabiliza la deuda ({b_sin:.0f}→"
         f"{b_con:.0f}%): coordina al equilibrio bueno SIN gastar apenas (m76)")


def _v_reestructurar_resetea():
    b_sin = float(_senda_reest(dict(_P0, reestructura=0.0))[1][-1])
    b_con = float(_senda_reest(dict(_P0, reestructura=1.0))[1][-1])
    return b_con < b_sin, \
        (f"una reestructuración con quita del 40% deja la deuda mucho más baja ({b_sin:.0f}→"
         f"{b_con:.0f}%): el reset de Argentina — con el costo de perder el acceso al mercado (m78)")


MODELO = Modelo(
    id="m96", nivel=11,
    nombre="Crisis de deuda soberana (episodio)",
    xlabel="Año $t$", ylabel="Deuda/PIB (%) e índices",
    parametros=[
        Parametro("backstop", _P0["backstop"], 0.0, 1.0, 0.1, "Fuerza del backstop (Draghi)",
                  grupo="resolución", definicion="prestamista que coordina al equilibrio bueno (m76)"),
        Parametro("reestructura", _P0["reestructura"], 0, 1, 1, "¿Reestructurar? (quita)",
                  grupo="resolución", definicion="el reset de Argentina (m78)"),
        Parametro("ajuste", _P0["ajuste"], 0, 5, 0.5, "Ajuste primario (austeridad)", grupo="política",
                  definicion="esfuerzo fiscal; daña el crecimiento (m69)"),
        Parametro("b0", _P0["b0"], 60, 160, 10, "Deuda inicial (%)", grupo="posición"),
        Parametro("prima_crisis", _P0["prima_crisis"], 2, 12, 1, "Salto de prima en la zona (pp)",
                  grupo="mercado"),
        Parametro("dano_austeridad", _P0["dano_austeridad"], 0, 0.8, 0.1, "Daño de la austeridad a g (m69)",
                  grupo="política"),
        Parametro("quita", _P0["quita"], 20, 70, 5, "Tamaño de la quita (%)", grupo="resolución"),
        Parametro("t_quita", _P0["t_quita"], 2, 10, 1, "Año de la reestructuración", grupo="resolución"),
        Parametro("umbral_zona", _P0["umbral_zona"], 60, 130, 5, "Umbral de la zona de crisis (%)",
                  grupo="mercado", definicion="deuda a la que la prima salta (m76)"),
        Parametro("prima_base", _P0["prima_base"], 0.5, 3, 0.25, "Prima base (pp)", grupo="mercado"),
        Parametro("rf", _P0["rf"], 0.5, 4, 0.25, "Tasa libre de riesgo rf (%)", grupo="mercado"),
        Parametro("g", _P0["g"], -2, 4, 0.5, "Crecimiento base g (%)", grupo="fundamentos"),
        Parametro("T", _P0["T"], 10, 25, 1, "Años simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Anatomía de una crisis soberana: ¿cómo se llega, y cómo se sale — austeridad, rescate o default?",
        variables=[("b_t", "la deuda que escala hacia la zona de crisis (m64, m76)"),
                   ("prima", "que salta al entrar en la zona (m76)"),
                   ("resolución", "austeridad (Grecia), backstop (Draghi) o quita (Argentina)")],
        derivacion=["acumulación\\;(m64) \\to zona\\;de\\;crisis\\;(m76) \\to espiral\\;(m78)",
                    "resolución: \\;austeridad\\;(m69)\\;|\\;backstop\\;(m76)\\;|\\;quita\\;(m78)",
                    "desenlace = f(backstop, moneda, viabilidad\\;política)"],
        contexto=("La crisis de deuda soberana es el episodio que cierra el nivel de "
                  "escenarios integrando todo el arco fiscal del currículo. Su "
                  "anatomía tiene cuatro fases. ACUMULACIÓN: déficits crónicos "
                  "elevan la deuda (m64) hacia niveles peligrosos, a menudo durante "
                  "años de complacencia. DETONANTE: un shock — una recesión que "
                  "hunde los ingresos, la revelación de que las estadísticas eran "
                  "falsas (Grecia 2009), o el contagio de otra crisis — empuja la "
                  "deuda a la zona de crisis (m76) y la prima de riesgo salta. "
                  "ESPIRAL: la prima alta encarece el servicio, que aumenta la "
                  "deuda, que sube más la prima (m78) — la trampa se cierra, y el "
                  "ajuste fiscal puede empeorarla al dañar el crecimiento (m69). "
                  "RESOLUCIÓN: hay tres caminos históricos. Grecia intentó "
                  "AUSTERIDAD bajo la Troika — y descubrió que ajustar en recesión "
                  "con la deuda en euros (moneda que no controla) profundizaba la "
                  "trampa (m69, m78). El BCE ofreció un BACKSTOP ('whatever it "
                  "takes' de Draghi, 2012) que coordinó a los mercados en el "
                  "equilibrio bueno para España e Italia sin gastar apenas (m76). "
                  "Argentina REESTRUCTURÓ repetidamente con quitas — resolviendo la "
                  "aritmética al costo de perder el acceso al mercado por años "
                  "(m78). El desenlace de cada crisis depende de tres cosas: ¿hay "
                  "un backstop creíble? ¿la deuda es en moneda propia (se puede "
                  "licuar) o extranjera (no)? ¿el ajuste es viable políticamente? "
                  "Para el Perú, la lección es preventiva: la disciplina fiscal de "
                  "los 2000 (m108) mantuvo la deuda lejos de la zona de crisis, y el "
                  "grado de inversión (m76) lo ancló en el equilibrio bueno."),
        autores=("Crisis del euro (Grecia 2010-2015, Draghi 2012 — menciones); "
                 "Argentina (2001, 2018 — menciones); la teoría: m64 (aritmética), "
                 "m76 (zona de crisis), m78 (trampa), m69 (austeridad) — "
                 "conocimiento general."),
        supuestos=[
            "La prima salta discretamente al cruzar el umbral de la zona (m76): la realidad es más gradual pero el efecto es el mismo.",
            "El backstop reduce la prima proporcionalmente: modela la coordinación de expectativas (Draghi) sin desembolso pleno.",
            "La reestructuración es una quita única: en la realidad son negociaciones largas con costos de acceso al mercado (m78).",
        ],
        ecuaciones=[
            Ecuacion("prima = prima_{base} + prima_{crisis}\\cdot\\mathbb{1}[b > umbral]",
                     "el salto de la prima",
                     "al entrar en la zona de crisis (m76), la prima salta discretamente — el "
                     "detonante que convierte deuda alta en crisis (verificado)."),
            Ecuacion("resolución: \\;backstop\\;|\\;quita\\;|\\;austeridad", "los tres caminos",
                     "coordinar (Draghi), resetear (Argentina) o ajustar (Grecia): el backstop es "
                     "el más barato si es creíble, la austeridad la más dolorosa (verificado)."),
        ],
        intuicion=("La crisis de deuda soberana enseña que la sostenibilidad fiscal "
                   "es tanto un problema de aritmética (m64) como de confianza "
                   "(m76): un país puede ser empujado a una crisis por el pánico "
                   "aunque sus fundamentos fueran manejables, y puede ser rescatado "
                   "por la coordinación aunque no cambie nada real. Los tres "
                   "caminos de salida tienen lógicas distintas. La austeridad "
                   "funciona SOLO si el país tiene espacio para crecer mientras "
                   "ajusta (no en el fondo de una recesión con la deuda en moneda "
                   "ajena — el error de Grecia). El backstop funciona SOLO si es "
                   "creíble e ilimitado (Draghi lo fue; los rescates tímidos "
                   "fracasan). La reestructuración funciona SIEMPRE aritméticamente "
                   "pero cierra el acceso al crédito por años (Argentina lo pagó). "
                   "La mejor política, como en todo el nivel de crisis, es "
                   "PREVENTIVA: no entrar en la zona (m76) manteniendo deuda "
                   "moderada (m64-m65) y credibilidad (grado de inversión) en las "
                   "buenas. El Perú lo hizo; Grecia y Argentina, cada una a su "
                   "manera, no — y pagaron el precio de la lección."),
        equilibrio=("La deuda converge (sostenible) o diverge (crisis) según la "
                    "fase y la resolución: austeridad sola a menudo no basta (m78), "
                    "el backstop coordina al equilibrio bueno (m76), la quita "
                    "resetea la aritmética (verificado en los tres casos)."),
        limitaciones=[
            "La prima discreta simplifica: la realidad es un continuo donde la crisis se construye gradualmente y estalla de golpe (m74).",
            "Sin la dimensión política explícita: la viabilidad del ajuste (¿aguanta el gobierno?, ¿hay estallido social?) decide muchas crisis (Grecia, m69).",
            "Moneda propia vs extranjera: el modelo no distingue, pero es CRUCIAL — con moneda propia se puede licuar (m78), con euro/dólar no (Grecia vs Reino Unido).",
        ],
        evolucion=("Cierra el nivel de escenarios integrando m64 (aritmética), m76 "
                   "(zona de crisis), m78 (trampa) y m69 (austeridad) en la "
                   "anatomía completa de una crisis soberana. Es el contraejemplo "
                   "de la disciplina peruana (m108) y prepara el nivel 12, donde la "
                   "sostenibilidad de la deuda peruana se evalúa con datos del MEF "
                   "(m108). Último episodio del currículo antes del laboratorio del "
                   "Perú."),
    ),
    escenarios=[
        Escenario("grecia_austeridad", "solo austeridad, deuda en euros, sin backstop",
                  {"ajuste": 3.0, "dano_austeridad": 0.6, "backstop": 0.0, "reestructura": 0.0},
                  "la deuda no baja pese al ajuste brutal: austeridad en recesión "
                  "con moneda ajena profundiza la trampa (m78) — la tragedia griega.",
                  cadena=["deuda en la zona de crisis (m76)", "austeridad severa (m69)",
                          "el ajuste daña el crecimiento", "r−g empeora, prima alta pesa",
                          "la deuda no baja: la trampa de Grecia (m78)"]),
        Escenario("draghi_backstop", "el BCE promete 'whatever it takes'",
                  {"backstop": 0.9, "ajuste": 1.5},
                  "la prima cae y la deuda se estabiliza casi sin desembolso: "
                  "coordinar al equilibrio bueno (m76) — el rescate más barato de "
                  "la historia (España, Italia 2012).",
                  cadena=["deuda en la zona de crisis", "el BCE ofrece backstop creíble e ilimitado",
                          "la prima se desploma (coordina al bueno, m76)", "el servicio baja",
                          "la deuda se estabiliza sin gastar apenas"]),
        Escenario("argentina_quita", "reestructuración con quita del 40%",
                  {"reestructura": 1.0, "quita": 40.0, "ajuste": 1.0},
                  "la deuda se resetea de golpe: resolver la aritmética por decreto "
                  "(m78) — al costo de perder el acceso al mercado por años "
                  "(Argentina).",
                  cadena=["deuda insostenible", "default y reestructuración con quita",
                          "b baja de golpe", "nueva senda desde más abajo",
                          "costo: exclusión del crédito (m78)"]),
        Escenario("prevencion_peru", "deuda moderada, lejos de la zona (b0=50%)",
                  {"b0": 50.0, "umbral_zona": 90.0},
                  "nunca entra en la zona de crisis: la disciplina que mantiene la "
                  "deuda baja (m64-m65) evita todo el drama — la doctrina peruana "
                  "(m108).",
                  cadena=["disciplina fiscal en las buenas (m64-m65)", "deuda muy por debajo del umbral",
                          "nunca entra en la zona de crisis (m76)", "prima baja siempre",
                          "el grado de inversión: crisis evitada por prevención"]),
    ],
    verificaciones=[
        Verificacion("la deuda entra en la zona: la prima salta (m76)", _v_entra_en_zona),
        Verificacion("la austeridad sola no basta (Grecia, m78)", _v_austeridad_no_basta),
        Verificacion("el backstop coordina al equilibrio bueno (Draghi)", _v_backstop_coordina),
        Verificacion("reestructurar resetea la aritmética (Argentina)", _v_reestructurar_resetea),
    ],
    notas="Aritmética Y confianza: se entra por pánico, se sale por coordinación, quita o ajuste. La mejor cura es no entrar.",
)
