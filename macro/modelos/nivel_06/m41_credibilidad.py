"""simuladores/macro/modelos/nivel_06/m41_credibilidad.py — credibilidad e inconsistencia temporal (nivel 6, ancla).

El juego de Barro-Gordon: un banco central que quiere empleo sobre el
natural (ambición ū) y odia la inflación minimiza
  L = ½π² + ½λ(ū − α(π − πe))²
Mejor respuesta:  π(πe) = λα(ū + α·πe)/(1+λα²)   (pendiente < 1)
Con expectativas racionales (πe = π):  π_disc = λαū  — el SESGO
INFLACIONARIO: inflación positiva SIN ganar empleo (la sorpresa es cero).
Una regla creíble logra π=0 con el MISMO empleo: atarse gana al arbitrio.

Procedencia: Kydland-Prescott (1977) y Barro-Gordon (1983) — menciones;
banquero conservador: Rogoff (1985, mención). Nobel 2004 (K-P).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _br(pe, p):
    return p["lam"] * p["alpha"] * (p["u_amb"] + p["alpha"] * pe) / (1 + p["lam"] * p["alpha"] ** 2)


def _pi_disc(p):
    return p["lam"] * p["alpha"] * p["u_amb"]


def _perdida(pi, pe, p):
    return 0.5 * pi ** 2 + 0.5 * p["lam"] * (p["u_amb"] - p["alpha"] * (pi - pe)) ** 2


def _curvas(p):
    pe = np.linspace(0, 1.6 * max(_pi_disc(p), 1.0), 200)
    disc = _pi_disc(p)
    return {"lineas": {"mejor respuesta del BC: $\\pi(\\pi^e)$": (pe, _br(pe, p), config.AZUL2),
                       "expectativas racionales: $\\pi = \\pi^e$": (pe, pe, config.GRIS)},
            "equilibrio": (disc, disc),
            "puntos": [(0.0, 0.0, "regla creíble: $\\pi = 0$")],
            "anotacion": (f"sesgo inflacionario: $\\pi_{{disc}} = \\lambda\\alpha\\bar{{u}} "
                          f"= {disc:.2f}\\%$\n"
                          f"pérdida bajo discreción: {float(_perdida(disc, disc, p)):.1f}\n"
                          f"pérdida bajo regla: {float(_perdida(0, 0, p)):.1f} — atarse GANA")}


def _resultados(p):
    disc = _pi_disc(p)
    return {"π bajo discreción (sesgo, %)": disc,
            "π bajo regla creíble (%)": 0.0,
            "sorpresa en equilibrio π−πe": 0.0,
            "pérdida bajo discreción": float(_perdida(disc, disc, p)),
            "pérdida bajo regla": float(_perdida(0.0, 0.0, p)),
            "pendiente de la mejor respuesta": p["lam"] * p["alpha"] ** 2 / (1 + p["lam"] * p["alpha"] ** 2)}


def _ecuaciones_calibradas(p):
    disc = _pi_disc(p)
    return [f"$\\pi(\\pi^e) = \\frac{{{p['lam']:.2f} \\times {p['alpha']:.1f}\\,({p['u_amb']:.1f} + "
            f"{p['alpha']:.1f}\\,\\pi^e)}}{{1 + {p['lam'] * p['alpha'] ** 2:.2f}}}$",
            f"$\\pi_{{disc}} = {p['lam']:.2f} \\times {p['alpha']:.1f} \\times {p['u_amb']:.1f} "
            f"= {disc:.2f}\\%$"]


_P0 = {"lam": 1.0, "alpha": 1.0, "u_amb": 4.0}


def _v_sesgo():
    pe = _pi_disc(_P0)
    return abs(float(_br(np.array([pe]), _P0)[0]) - pe) < 1e-12, \
        (f"la mejor respuesta cruza la recta racional exactamente en λαū = {pe:.2f}%: "
         "el sesgo inflacionario de la discreción")


def _v_sorpresa_nula():
    disc = _pi_disc(_P0)
    empleo_disc = _P0["u_amb"] - _P0["alpha"] * (disc - disc)
    empleo_regla = _P0["u_amb"] - _P0["alpha"] * (0 - 0)
    return abs(empleo_disc - empleo_regla) < 1e-12, \
        ("en equilibrio la sorpresa es CERO: la inflación del sesgo no compra "
         "ni un punto de empleo — se paga por nada")


def _v_regla_gana():
    disc = _pi_disc(_P0)
    return float(_perdida(0, 0, _P0)) < float(_perdida(disc, disc, _P0)), \
        (f"pérdida con regla ({float(_perdida(0, 0, _P0)):.1f}) < con discreción "
         f"({float(_perdida(disc, disc, _P0)):.1f}): atarse las manos ES la política óptima")


def _v_conservador():
    sesgo_normal = _pi_disc(_P0)
    sesgo_rogoff = _pi_disc(dict(_P0, lam=0.25))
    return sesgo_rogoff < sesgo_normal, \
        (f"delegar en un banquero que pese menos el empleo (λ: 1→0.25) recorta el sesgo "
         f"de {sesgo_normal:.1f}% a {sesgo_rogoff:.1f}%: el conservador de Rogoff")


MODELO = Modelo(
    id="m41", nivel=6,
    nombre="Credibilidad (inconsistencia temporal)",
    xlabel="Inflación esperada $\\pi^e$ (%)", ylabel="Inflación elegida $\\pi$ (%)",
    parametros=[
        Parametro("u_amb", _P0["u_amb"], 0.5, 8, 0.5, "Ambición de empleo ū (pp)", grupo="tentación",
                  definicion="cuánto empleo sobre el natural quisiera el gobierno"),
        Parametro("lam", _P0["lam"], 0.1, 3, 0.05, "Peso del empleo λ", grupo="preferencias",
                  definicion="bajarlo = nombrar un banquero conservador (Rogoff)"),
        Parametro("alpha", _P0["alpha"], 0.3, 2, 0.1, "Pendiente de Phillips α", grupo="estructura",
                  definicion="cuánto empleo compra una sorpresa de inflación (m14)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un banco central bien intencionado y libre produce MÁS inflación sin ganar empleo — y por qué atarse las manos lo arregla?",
        variables=[("π", "inflación elegida por el BC — su 'movida' en el juego"),
                   ("πe", "expectativas del público — la otra movida (racional)"),
                   ("λαū", "el sesgo inflacionario — el precio de conservar el arbitrio")],
        derivacion=["L = \\tfrac{1}{2}\\pi^2 + \\tfrac{1}{2}\\lambda\\,(\\bar{u} - \\alpha(\\pi - \\pi^e))^2",
                    "\\frac{\\partial L}{\\partial \\pi} = 0 \\Rightarrow \\pi(\\pi^e) = \\frac{\\lambda\\alpha(\\bar{u}+\\alpha\\pi^e)}{1+\\lambda\\alpha^2}",
                    "\\pi^e = \\pi \\Rightarrow \\pi_{disc} = \\lambda\\,\\alpha\\,\\bar{u}"],
        contexto=("Kydland y Prescott (1977) descubrieron un problema que ninguna "
                  "buena voluntad resuelve: el plan óptimo de hoy (prometer inflación "
                  "cero) deja de ser óptimo mañana (una vez que los salarios están "
                  "firmados, una sorpresita de inflación compra empleo). El público, "
                  "racional, anticipa la tentación — y las expectativas suben hasta "
                  "donde al banco ya no le convenga sorprender. Resultado: toda la "
                  "inflación del sesgo, nada del empleo. Barro-Gordon (1983) lo "
                  "escribió como juego; la solución fue institucional: reglas, "
                  "independencia, banqueros conservadores (Rogoff 1985) y, al final "
                  "del camino, las metas de m40."),
        autores=("Kydland y Prescott (1977, Nobel 2004); Barro y Gordon (1983); "
                 "Rogoff (1985) — menciones. Es la microfundación del diseño "
                 "institucional de los bancos centrales modernos."),
        supuestos=[
            "El público es RACIONAL: conoce la función objetivo del BC y no se deja sorprender sistemáticamente (m42).",
            "La sorpresa de inflación compra empleo (Phillips de m14 en versión sorpresa: solo π−πe importa).",
            "Juego de una sola vez: la reputación en juegos repetidos MEJORA las cosas (mención) — la versión estática es el peor caso.",
        ],
        ecuaciones=[
            Ecuacion("\\pi(\\pi^e) = \\frac{\\lambda\\alpha(\\bar{u} + \\alpha\\,\\pi^e)}{1 + \\lambda\\alpha^2}",
                     "la mejor respuesta (la tentación)",
                     "dado lo que el público espera, al BC siempre le conviene un poco más de "
                     "inflación que cero — y el público lo sabe."),
            Ecuacion("\\pi_{disc} = \\lambda\\,\\alpha\\,\\bar{u}", "el sesgo inflacionario",
                     "el cruce con πe=π: inflación proporcional a la ambición (ū), al peso del "
                     "empleo (λ) y a la potencia de la sorpresa (α) — pagada A CAMBIO DE NADA."),
        ],
        intuicion=("Es el problema de Ulises y las sirenas en política monetaria: no "
                   "basta querer portarse bien — hay que no PODER portarse mal. El "
                   "gráfico lo dice todo: la mejor respuesta (tentación) corta a la "
                   "recta racional lejos del origen; solo un mástil institucional "
                   "(regla, independencia, meta pública con rendición de cuentas) "
                   "sostiene el punto (0,0). El θ de m40 es la fuerza de ese mástil, "
                   "y ahora se entiende por qué se gana lento y se pierde rápido."),
        equilibrio=("Equilibrio de Nash con expectativas racionales: π = πe = λαū "
                    "(verificado exacto como cruce BR∩45°). Estable en el sentido "
                    "del juego; socialmente dominado por la regla (pérdidas "
                    "comparadas numéricamente)."),
        limitaciones=[
            "Juego de una vez: con reputación (repetición infinita) la discreción puede sostener π bajas — la credibilidad como capital (mención).",
            "ū exógena: si la ambición viene de fallas reales del mercado laboral, la reforma laboral ataca la RAÍZ del sesgo.",
            "Rigidez de la regla: ante shocks grandes, la regla estricta duele — el diseño moderno mezcla regla y escape (flexible IT, m40).",
        ],
        evolucion=("Cierra el arco institucional del nivel: m38 (la regla), m39 (el "
                   "instrumento), m40 (el ancla) existen PORQUE este juego se pierde "
                   "con discreción. m42 remata el fundamento (expectativas "
                   "racionales) y el nivel 8 heredará esta lógica en el modelo "
                   "completo (m56). El BCRP independiente con meta pública es la "
                   "solución de Rogoff-metas aplicada (mención)."),
    ),
    escenarios=[
        Escenario("banquero_conservador", "delegar en Rogoff: λ baja de 1.0 a 0.25",
                  {"lam": 0.25},
                  "el sesgo cae de 4% a 1%: nombrar a alguien que sufra MENOS por el "
                  "empleo produce MENOS inflación con el mismo empleo — la paradoja "
                  "de la delegación.",
                  cadena=["delegación en conservador", "↓λ", "la tentación de sorprender cae",
                          "el público lo sabe: ↓πe", "sesgo menor sin costo de empleo"]),
        Escenario("gobierno_ambicioso", "la ambición sube: ū de 4 a 6 pp",
                  {"u_amb": 6.0},
                  "el sesgo salta a 6%: querer más empleo del que la estructura da "
                  "no compra empleo — solo inflación (m14, ahora microfundada).",
                  cadena=["↑ū (presión política)", "mayor tentación de sorprender",
                          "el público anticipa", "↑πe hasta anular la sorpresa",
                          "más inflación, mismo empleo"]),
        Escenario("phillips_empinada", "sorpresas potentes: α de 1.0 a 2.0",
                  {"alpha": 2.0},
                  "el sesgo se duplica: cuanto más 'rinde' la sorpresa, más cara "
                  "sale la discreción — las economías indexadas sufren doble.",
                  cadena=["↑α", "cada sorpresa compraría más empleo",
                          "la tentación crece", "πe sube en proporción",
                          "sesgo λαū mayor"]),
    ],
    verificaciones=[
        Verificacion("sesgo = λαū exacto (cruce BR ∩ racionalidad)", _v_sesgo),
        Verificacion("sorpresa nula en equilibrio: se paga por nada", _v_sorpresa_nula),
        Verificacion("la regla domina a la discreción (pérdidas)", _v_regla_gana),
        Verificacion("el conservador de Rogoff recorta el sesgo", _v_conservador),
    ],
    notas="Ulises y las sirenas con función de pérdida: no basta querer portarse bien — hay que no poder portarse mal.",
)
