# m42_expectativas_racionales.py — expectativas racionales (nivel 6, cierre).
#
# Oferta de Lucas: solo las SORPRESAS mueven el producto:
#   y_t = ȳ + β(π_t − πe_t)
# Experimento: una expansión monetaria eleva π de 0 a gM desde t_a. Se
# comparan DOS públicos ante la MISMA política:
#   adaptativos (πe = π_{t−1}): un período de boom — luego nada.
#   racionales: si la política fue ANUNCIADA, πe salta con ella → NINGÚN boom
#               (proposición de inefectividad); si fue sorpresa, un período.
# Al final, en ambos mundos queda solo la inflación: m35 otra vez, ahora con
# el reloj de las expectativas como protagonista.
#
# Procedencia: Muth (1961), Lucas (1972, 1976 — crítica), Sargent-Wallace
# (1975, inefectividad) — menciones; conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    ta = int(round(p["t_anuncio"]))
    t = np.arange(T + 1)
    pi = np.where(t >= ta, p["gM"], 0.0)
    pe_adap = np.concatenate(([0.0], pi[:-1]))                    # πe = π_{t−1}
    if p["anunciada"] >= 0.5:                                     # anticipada
        pe_rac = pi.copy()
    else:                                                         # sorpresa en ta
        pe_rac = np.where(t > ta, p["gM"], 0.0)
    y_adap = p["ybar"] + p["beta"] * (pi - pe_adap)
    y_rac = p["ybar"] + p["beta"] * (pi - pe_rac)
    return t, pi, y_adap, y_rac


def _curvas(p):
    t, pi, y_adap, y_rac = _sendas(p)
    return {"lineas": {"$y_t$ con expectativas adaptativas": (t, y_adap, config.ROJO),
                       "$y_t$ con expectativas racionales": (t, y_rac, config.AZUL2),
                       "producto natural $\\bar{y}$": (t, np.full(len(t), p["ybar"]), config.GRIS)},
            "anotacion": (f"política {'ANUNCIADA' if p['anunciada'] >= 0.5 else 'SORPRESIVA'} "
                          f"en $t = {int(p['t_anuncio'])}$\n"
                          f"racionales: {'ningún' if p['anunciada'] >= 0.5 else 'UN período de'} boom\n"
                          f"adaptativos: un período de boom — luego solo inflación")}


def _resultados(p):
    t, pi, y_adap, y_rac = _sendas(p)
    return {"boom máximo (adaptativas)": float(y_adap.max() - p["ybar"]),
            "boom máximo (racionales)": float(y_rac.max() - p["ybar"]),
            "períodos con y>ȳ (adaptativas)": float(np.sum(y_adap > p["ybar"] + 1e-12)),
            "períodos con y>ȳ (racionales)": float(np.sum(y_rac > p["ybar"] + 1e-12)),
            "π final (%) — en ambos mundos": float(pi[-1])}


_P0 = {"gM": 4.0, "beta": 0.5, "t_anuncio": 4.0, "T": 12.0,
       "ybar": 100.0, "anunciada": 1.0}


def _v_inefectividad():
    _, _, _, y_rac = _sendas(_P0)
    return bool(np.all(np.abs(y_rac - _P0["ybar"]) < 1e-12)), \
        ("política anunciada + expectativas racionales ⇒ y = ȳ en TODOS los períodos: "
         "la proposición de inefectividad (Sargent-Wallace)")


def _v_adaptativas_un_boom():
    _, _, y_adap, _ = _sendas(_P0)
    ta = int(_P0["t_anuncio"])
    boom = y_adap - _P0["ybar"]
    ok = (abs(boom[ta] - _P0["beta"] * _P0["gM"]) < 1e-12
          and bool(np.all(np.abs(np.delete(boom, ta)) < 1e-12)))
    return ok, (f"con aprendizaje rezagado el boom es EXACTAMENTE β·gM = "
                f"{_P0['beta'] * _P0['gM']:.1f} y dura UN período: lo que tarda πe en alcanzar a π")


def _v_sorpresa_iguala():
    p = dict(_P0, anunciada=0.0)
    _, _, y_adap, y_rac = _sendas(p)
    return bool(np.all(np.abs(y_adap - y_rac) < 1e-12)), \
        ("si la política es SORPRESA, racionales y adaptativos reaccionan idéntico "
         "(un boom de un período): solo lo no anticipado funciona — una vez")


def _v_solo_precios():
    t, pi, y_adap, y_rac = _sendas(_P0, T=60)
    ok = (abs(float(y_adap[-1]) - _P0["ybar"]) < 1e-12
          and abs(float(pi[-1]) - _P0["gM"]) < 1e-12)
    return ok, ("a largo plazo, en ambos mundos y = ȳ y π = gM: la política dejó solo "
                "precios — la neutralidad (m35) con el reloj de expectativas explícito")


MODELO = Modelo(
    id="m42", nivel=6,
    nombre="Expectativas racionales",
    xlabel="Período $t$", ylabel="Producto $y_t$ (índice)",
    parametros=[
        Parametro("anunciada", _P0["anunciada"], 0, 1, 1, "¿Política anunciada? (1 sí, 0 sorpresa)",
                  grupo="experimento",
                  definicion="TODO el resultado depende de este interruptor"),
        Parametro("gM", _P0["gM"], 1, 10, 0.5, "Expansión: inflación resultante (%)", grupo="experimento"),
        Parametro("beta", _P0["beta"], 0.1, 1.5, 0.1, "Potencia de la sorpresa β", grupo="estructura",
                  definicion="cuánto producto compra un punto de π no anticipada"),
        Parametro("t_anuncio", _P0["t_anuncio"], 1, 8, 1, "Período del cambio", grupo="experimento"),
        Parametro("T", _P0["T"], 8, 30, 1, "Períodos simulados", grupo="experimento"),
        Parametro("ybar", _P0["ybar"], 80, 120, 5, "Producto natural ȳ", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="Si el público entiende la política tan bien como quien la hace, ¿qué le queda por hacer a la política?",
        variables=[("y_t", "producto — solo se mueve con SORPRESAS"),
                   ("πe_t", "expectativas — el corazón del modelo: ¿miran atrás o entienden?"),
                   ("anunciada", "el experimento: información vs sorpresa")],
        derivacion=["y_t = \\bar{y} + \\beta\\,(\\pi_t - \\pi^e_t) \\;\\;(oferta\\;de\\;Lucas)",
                    "racionales: \\; \\pi^e_t = E[\\pi_t | información_t]",
                    "política\\;anunciada \\Rightarrow \\pi^e_t = \\pi_t \\Rightarrow y_t = \\bar{y}\\;\\forall t"],
        contexto=("Muth (1961) propuso una disciplina brutal: en el modelo, la gente "
                  "entiende el modelo. Lucas (1972) la llevó a la macro y todo "
                  "cambió: si el producto solo responde a sorpresas y el público "
                  "anticipa la política sistemática, la política sistemática NO "
                  "mueve el producto (Sargent-Wallace 1975). Los booms de m14 y m25 "
                  "eran hijos del aprendizaje lento; con racionalidad, la "
                  "desinflación anunciada y creíble puede ser gratis — y la crítica "
                  "de Lucas (1976) advierte que TODOS los coeficientes estimados "
                  "bajo un régimen mueren con el régimen."),
        autores=("Muth (1961); Lucas (1972; crítica 1976; Nobel 1995); Sargent y "
                 "Wallace (1975) — menciones."),
        supuestos=[
            "El público conoce la ESTRUCTURA y la regla de política: errores solo por información, nunca sistemáticos.",
            "Los precios son flexibles dado πe: toda la fricción está en la información (los NK añadirán rigidez REAL, m53).",
            "La 'sorpresa' es el único canal real del dinero (oferta de Lucas).",
        ],
        ecuaciones=[
            Ecuacion("y_t = \\bar{y} + \\beta(\\pi_t - \\pi^e_t)", "oferta de Lucas",
                     "producir sobre lo natural exige ENGAÑAR: precios efectivos sobre los "
                     "esperados. Sin sorpresa, no hay palanca."),
            Ecuacion("\\pi\\;anunciada \\Rightarrow y_t = \\bar{y}", "proposición de inefectividad",
                     "lo anticipado ya está en los contratos: la política sistemática solo "
                     "elige la inflación — el sesgo de m41 nace exactamente aquí."),
        ],
        intuicion=("Contra un público que aprende con rezago, la política juega "
                   "ajedrez contra alguien que repite la última jugada; contra uno "
                   "racional, juega contra alguien que lee su estrategia. El gráfico "
                   "es el veredicto: la línea roja (adaptativos) regala un boom de "
                   "un período; la azul (racionales, anunciada) ni se inmuta. La "
                   "esperanza que deja: si las sorpresas no dan producto, la "
                   "DESINFLACIÓN creíble tampoco lo quita — el fundamento del θ alto "
                   "de m40."),
        equilibrio=("y = ȳ es el único reposo; los desvíos duran lo que dure la "
                    "información incompleta (un período aquí). Verificado: "
                    "inefectividad exacta, boom adaptativo = β·gM exacto, sorpresa "
                    "iguala mundos, largo plazo solo precios."),
        limitaciones=[
            "Demasiado filo: con contratos largos y rigideces reales, la política anticipada SÍ tiene efectos (nuevos keynesianos, m53-m56) — racionalidad no implica impotencia.",
            "Racionalidad plena es cara: aprendizaje, atención limitada y heterogeneidad la matizan (menciones).",
            "La inefectividad es sobre el PRODUCTO: la política sigue eligiendo inflación, bienestar y distribución.",
        ],
        evolucion=("Cierra el nivel 6 y arma la síntesis moderna: expectativas "
                   "racionales (m42) + rigideces nominales (m21) + regla de Taylor "
                   "(m38) = el modelo nuevo keynesiano de 3 ecuaciones (m53-m56, "
                   "nivel 8). Y deja la lección metodológica que gobierna el nivel "
                   "12: estimar reglas y curvas peruanas exige respetar los cambios "
                   "de régimen (1990, 2002) — la crítica de Lucas en la práctica."),
    ),
    escenarios=[
        Escenario("politica_anunciada", "expansión comunicada con anticipación",
                  {"anunciada": 1.0},
                  "los racionales reprecian TODO al anuncio: ni un período de boom — "
                  "la inefectividad en su forma pura; los adaptativos regalan uno.",
                  cadena=["anuncio creíble", "πe racional salta YA", "π−πe = 0 siempre",
                          "y = ȳ en todo t", "solo queda la inflación elegida"]),
        Escenario("politica_sorpresa", "el banco central actúa sin avisar",
                  {"anunciada": 0.0},
                  "ambos públicos son sorprendidos UN período: lo no anticipado "
                  "funciona — una vez, y al costo de enseñarle al público a desconfiar (m41).",
                  cadena=["acción sin anuncio", "π sube sin que πe lo supiera",
                          "sorpresa: boom de un período", "πe se corrige al ver",
                          "el truco no se puede repetir sistemáticamente"]),
        Escenario("sorpresas_potentes", "economía muy sensible: β = 1.2",
                  {"beta": 1.2, "anunciada": 0.0},
                  "la sorpresa rinde más producto… y por eso mismo (m41) la "
                  "tentación y el sesgo son mayores: β alto es un arma de doble filo.",
                  cadena=["↑β", "cada punto de sorpresa compra más y",
                          "boom mayor — una vez", "y mayor tentación en m41"]),
    ],
    verificaciones=[
        Verificacion("inefectividad: anunciada+racionales ⇒ y=ȳ siempre", _v_inefectividad),
        Verificacion("adaptativas: boom = β·gM, un solo período", _v_adaptativas_un_boom),
        Verificacion("la sorpresa iguala a los dos públicos", _v_sorpresa_iguala),
        Verificacion("a largo plazo, solo precios (m35 revisitada)", _v_solo_precios),
    ],
    notas="Cierra el nivel 6: contra un público que entiende, la política solo elige la inflación — salvo que existan rigideces (nivel 8).",
)
