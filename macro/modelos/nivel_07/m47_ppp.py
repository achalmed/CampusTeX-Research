"""simuladores/macro/modelos/nivel_07/m47_ppp.py — paridad del poder adquisitivo (nivel 7).

PPP relativa: el tipo de cambio de equilibrio sigue a los diferenciales de
inflación, dejando el RER constante:
  E^{ppp}_{t+1}/E^{ppp}_t = (1+π)/(1+π*)
La evidencia: el E observado se DESVÍA del PPP por años; el desvío decae
con una vida media de 3-5 años (el "PPP puzzle" de Rogoff, mención):
  E_t = E^{ppp}_t · (1 + d_t),   d_t = d_0 · (1/2)^{t/vida}
PPP es brújula de largo plazo, no GPS de corto.

Procedencia: Cassel (1918, mención); evidencia de vidas medias: Rogoff
(1996, "The PPP Puzzle", mención) — conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    factor = (1 + p["pi"] / 100) / (1 + p["pi_star"] / 100)
    e_ppp = p["E0"] * factor ** t
    d = (p["desvio0"] / 100) * 0.5 ** (t / p["vida"])
    e_obs = e_ppp * (1 + d)
    rer = 100 * (1 + d)                       # índice: 100 = nivel PPP
    return t, e_ppp, e_obs, rer


def _curvas(p):
    t, e_ppp, e_obs, rer = _sendas(p)
    return {"lineas": {"$E$ observado (con desvío)": (t, e_obs, config.AZUL2),
                       "$E^{ppp}$ (sigue a $\\pi-\\pi^*$)": (t, e_ppp, config.GRIS)},
            "puntos": [(0.0, float(e_obs[0]), f"desvío inicial {p['desvio0']:.0f}%")],
            "anotacion": (f"$E^{{ppp}}$ crece al "
                          f"{100 * ((1 + p['pi'] / 100) / (1 + p['pi_star'] / 100) - 1):.2f}\\%$ por período\n"
                          f"vida media del desvío: {p['vida']:.0f} períodos\n"
                          "PPP: brújula de largo plazo, no GPS de corto")}


def _resultados(p):
    t, e_ppp, e_obs, rer = _sendas(p)
    return {"crecimiento de E_ppp (%/período)":
                100 * ((1 + p["pi"] / 100) / (1 + p["pi_star"] / 100) - 1),
            "aproximación π−π* (%)": p["pi"] - p["pi_star"],
            f"E_ppp en t={int(p['T'])}": float(e_ppp[-1]),
            f"E observado en t={int(p['T'])}": float(e_obs[-1]),
            f"desvío restante en t={int(p['T'])} (%)": float(rer[-1] - 100),
            "RER inicial (índice)": float(rer[0])}


def _ecuaciones_calibradas(p):
    f = (1 + p["pi"] / 100) / (1 + p["pi_star"] / 100)
    return [f"$E^{{ppp}}_{{t+1}}/E^{{ppp}}_t = {1 + p['pi'] / 100:.3f}/{1 + p['pi_star'] / 100:.3f} "
            f"= {f:.4f}$",
            f"$d_t = {p['desvio0']:.0f}\\% \\times (1/2)^{{t/{p['vida']:.0f}}}$"]


_P0 = {"pi": 12.0, "pi_star": 3.0, "E0": 3.5, "desvio0": 15.0, "vida": 3.0, "T": 10.0}


def _v_crecimiento_exacto():
    t, e_ppp, _, _ = _sendas(_P0)
    razones = e_ppp[1:] / e_ppp[:-1]
    teo = (1 + _P0["pi"] / 100) / (1 + _P0["pi_star"] / 100)
    return bool(np.all(np.abs(razones - teo) < 1e-12)), \
        f"E_ppp crece exactamente a (1+π)/(1+π*) = {teo:.4f} cada período"


def _v_rer_constante_en_ppp():
    p = dict(_P0, desvio0=0.0)
    _, _, _, rer = _sendas(p)
    return bool(np.all(np.abs(rer - 100.0) < 1e-9)), \
        "sobre la senda PPP pura el RER queda clavado en 100: la paridad ES RER constante"


def _v_semivida():
    _, _, _, rer = _sendas(_P0, T=30)
    d0, d_vida = rer[0] - 100, rer[int(_P0["vida"])] - 100
    return abs(d_vida - d0 / 2) < 1e-9, \
        f"a los {int(_P0['vida'])} períodos el desvío es exactamente la mitad ({d_vida:.2f}% de {d0:.0f}%)"


def _v_sin_diferencial():
    p = dict(_P0, pi=3.0)
    _, e_ppp, _, _ = _sendas(p)
    return bool(np.all(np.abs(e_ppp - p["E0"]) < 1e-12)), \
        "con π = π* el E de PPP no se mueve: sin diferencial no hay tendencia cambiaria"


MODELO = Modelo(
    id="m47", nivel=7,
    nombre="Paridad del poder adquisitivo (PPP)",
    xlabel="Período $t$", ylabel="Tipo de cambio $E$ (PEN/USD)",
    parametros=[
        Parametro("pi", _P0["pi"], 0, 60, 1, "Inflación local π (%)", grupo="diferencial",
                  definicion="el motor de la depreciación tendencial"),
        Parametro("pi_star", _P0["pi_star"], 0, 15, 0.5, "Inflación externa π* (%)", grupo="diferencial"),
        Parametro("desvio0", _P0["desvio0"], -30, 40, 5, "Desvío inicial del PPP (%)", grupo="corto plazo",
                  definicion="cuán 'caro' o 'barato' arranca el país"),
        Parametro("vida", _P0["vida"], 1, 8, 0.5, "Vida media del desvío (períodos)", grupo="corto plazo",
                  definicion="la evidencia dice 3-5 años (PPP puzzle)"),
        Parametro("E0", _P0["E0"], 2, 5, 0.1, "Tipo de cambio inicial", grupo="inicial"),
        Parametro("T", _P0["T"], 5, 30, 1, "Períodos simulados", grupo="inicial"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Hacia dónde camina el tipo de cambio cuando pasan los años — y por qué tarda tanto en llegar?",
        variables=[("E_ppp", "el ancla: E que mantiene el RER constante"),
                   ("d_t", "el desvío del PPP — grande a corto, mortal a largo"),
                   ("π − π*", "el diferencial de inflación — la única tendencia")],
        derivacion=["ley\\;de\\;un\\;precio: \\;P = E\\,P^* \\;(absoluta)",
                    "en\\;tasas: \\;\\frac{E'}{E} = \\frac{1+\\pi}{1+\\pi^*} \\;(relativa)",
                    "\\Rightarrow RER\\;constante\\;sobre\\;la\\;senda\\;PPP"],
        contexto=("Cassel (1918) necesitaba re-anclar las monedas tras la Primera "
                  "Guerra: propuso que el cambio 'correcto' iguala poderes de "
                  "compra. Un siglo después la evidencia dicta el veredicto doble: "
                  "a CORTO plazo el PPP falla estrepitosamente (los desvíos duran "
                  "años — vida media de 3 a 5, el 'puzzle' de Rogoff); a LARGO "
                  "plazo, ningún país con 30 puntos de inflación extra evita la "
                  "depreciación tendencial. El índice Big Mac (mención) es su "
                  "versión pop."),
        autores=("Cassel (1918, mención); evidencia moderna: Rogoff (1996, The "
                 "PPP Puzzle, mención); Big Mac Index de The Economist (mención "
                 "lúdica)."),
        supuestos=["Canastas comparables y comerciables (los no transables — cortes de pelo — rompen la absoluta: Balassa-Samuelson, mención).",
                   "El desvío decae geométricamente con vida media dada (forma didáctica del ajuste real).",
                   "π y π* exógenas: las fija el nivel 6 de cada país (m40)."],
        ecuaciones=[
            Ecuacion("\\frac{E^{ppp}_{t+1}}{E^{ppp}_t} = \\frac{1+\\pi}{1+\\pi^*}", "PPP relativa",
                     "la moneda del país que infla más se deprecia en la misma proporción: la "
                     "teoría cuantitativa (m34) exportada al tipo de cambio."),
            Ecuacion("d_t = d_0\\,(1/2)^{t/vida}", "el desvío que muere lento",
                     "todo lo que UIP (m48), shocks y burbujas hacen al E de corto plazo, "
                     "medido como distancia al ancla — y su lenta agonía."),
        ],
        intuicion=("El PPP es la gravedad cambiaria: no explica ningún vuelo del "
                   "dólar de este mes, pero decide dónde aterrizan todos. Para el "
                   "análisis peruano la lectura operativa es doble: la depreciación "
                   "TENDENCIAL del sol es el diferencial de inflación contra EE.UU. "
                   "(pequeño desde las metas de m40), y todo lo demás — cobre, FED, "
                   "pánico — es desvío con fecha de caducidad… de años."),
        equilibrio=("La senda E_ppp es el atractor (RER constante verificado "
                    "exacto); el desvío decae con la vida media declarada "
                    "(verificado). 'Equilibrio' aquí es una TENDENCIA, no un punto."),
        limitaciones=[
            "Vida media de años: para horizontes de política monetaria el PPP casi no informa (m48 manda a corto plazo).",
            "Balassa-Samuelson: países que crecen rápido APRECIAN su RER de equilibrio — el ancla misma se mueve (mención).",
            "Canastas distintas, bienes no transables y aranceles ensucian la comparación absoluta.",
        ],
        evolucion=("El PPP fija el largo plazo; m48 (UIP) toma el corto: tasas de "
                   "interés y expectativas. Dornbusch (mención) los casará con el "
                   "overshooting; m49 los pone dentro de la política; y m102 medirá "
                   "los desvíos del sol con datos del BCRP."),
    ),
    escenarios=[
        Escenario("inflacion_cronica", "π local del 30% con ancla externa del 3%",
                  {"pi": 30.0},
                  "E_ppp se multiplica por 10 en el horizonte: con inflación crónica "
                  "la depreciación no es opinión, es aritmética — los 80 peruanos.",
                  cadena=["π ≫ π*", "los precios locales se disparan en dólares",
                          "el RER se apreciaría sin remedio", "E debe seguir al diferencial",
                          "depreciación tendencial inevitable"]),
        Escenario("desvio_persistente", "vida media de 5 períodos (el puzzle)",
                  {"vida": 5.0},
                  "a los 10 períodos aún queda un cuarto del desvío: la 'gravedad' "
                  "del PPP existe pero es débil — el puzzle de Rogoff.",
                  cadena=["shock desvía a E del PPP", "el arbitraje de bienes es lento",
                          "vida media larga", "años de sobre/subvaluación"]),
        Escenario("monedas_ancladas", "ambos países con 3% de inflación",
                  {"pi": 3.0},
                  "E_ppp plano: dos anclas de m40 hacen un tipo de cambio sin "
                  "tendencia — todo lo que quede es ruido de corto plazo (m48).",
                  cadena=["π = π*", "sin diferencial", "E_ppp constante",
                          "el cambio flota alrededor de un nivel"]),
    ],
    verificaciones=[
        Verificacion("E_ppp crece exactamente a (1+π)/(1+π*)", _v_crecimiento_exacto),
        Verificacion("sobre la senda PPP el RER es constante", _v_rer_constante_en_ppp),
        Verificacion("el desvío se hace mitad en su vida media", _v_semivida),
        Verificacion("sin diferencial no hay tendencia", _v_sin_diferencial),
    ],
    notas="La gravedad cambiaria: no explica el vuelo de este mes, pero decide dónde aterrizan todos.",
)
