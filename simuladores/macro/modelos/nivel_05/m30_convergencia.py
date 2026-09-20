"""simuladores/macro/modelos/nivel_05/m30_convergencia.py — convergencia: ¿los pobres alcanzan a los ricos?

(nivel 5).

Dos economías con la MISMA estructura (s, α, n, δ, A) y distinto k0: Solow
predice que la pobre crece más rápido y la brecha se cierra (β-convergencia).
Pero si difieren en s (o A), convergen a ESTADOS ESTACIONARIOS DISTINTOS:
convergencia CONDICIONAL, no absoluta — la clave que reconcilia el modelo
con los datos (los países pobres NO alcanzan en general; los parecidos, sí).

Procedencia: dinámica de Solow aplicada a comparación de países; literatura
empírica de convergencia (Barro, Sala-i-Martin; Baumol — menciones) —
conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _ngd(p):
    return p["n"] + p["delta"]


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    ngd = _ngd(p)
    k_r = _solow.trayectoria(p["k0_rico"], p["s_rico"], p["A"], p["alpha"], ngd, T)
    k_p = _solow.trayectoria(p["k0_pobre"], p["s_pobre"], p["A"], p["alpha"], ngd, T)
    y_r = _solow.f(k_r, p["A"], p["alpha"])
    y_p = _solow.f(k_p, p["A"], p["alpha"])
    return np.arange(T + 1), y_p, y_r


def _curvas(p):
    t, y_p, y_r = _sendas(p)
    return {"lineas": {"país pobre ($k_0$ bajo)": (t, y_p, config.ROJO),
                       "país rico ($k_0$ alto)": (t, y_r, config.AZUL2)},
            "anotacion": (f"brecha inicial: {100 * (1 - y_p[0] / y_r[0]):.0f}%  →  "
                          f"final: {100 * (1 - y_p[-1] / y_r[-1]):.0f}%\n"
                          f"$s$ pobre = {p['s_pobre']:.2f}, $s$ rico = {p['s_rico']:.2f}"
                          + ("  (misma estructura)" if abs(p["s_pobre"] - p["s_rico"]) < 1e-9
                             else "  (estructuras distintas)"))}


def _resultados(p):
    t, y_p, y_r = _sendas(p)
    g_p = 100 * (y_p[1] / y_p[0] - 1)
    g_r = 100 * (y_r[1] / y_r[0] - 1)
    return {"y pobre inicial": float(y_p[0]), "y rico inicial": float(y_r[0]),
            "crecimiento inicial pobre (%)": g_p,
            "crecimiento inicial rico (%)": g_r,
            "brecha inicial (%)": 100 * (1 - y_p[0] / y_r[0]),
            f"brecha en t={int(p['T'])} (%)": 100 * (1 - y_p[-1] / y_r[-1])}


_P0 = {"s_pobre": 0.20, "s_rico": 0.20, "k0_pobre": 1.0, "k0_rico": 8.0,
       "A": 1.0, "alpha": 0.33, "n": 0.01, "delta": 0.05, "T": 80.0}


def _v_beta_convergencia():
    r = _resultados(_P0)
    return r["crecimiento inicial pobre (%)"] > r["crecimiento inicial rico (%)"], \
        (f"partiendo atrás se crece más rápido ({r['crecimiento inicial pobre (%)']:.1f}% vs "
         f"{r['crecimiento inicial rico (%)']:.1f}%): β-convergencia — rendimientos decrecientes en acción")


def _v_absoluta_con_misma_estructura():
    _, y_p, y_r = _sendas(_P0, T=3000)
    return abs(y_p[-1] - y_r[-1]) < 1e-9, ("con la MISMA estructura, la brecha desaparece por completo: "
                                           "convergencia absoluta entre economías gemelas")


def _v_condicional():
    p = dict(_P0, s_pobre=0.10)
    _, y_p, y_r = _sendas(p, T=3000)
    brecha = 1 - y_p[-1] / y_r[-1]
    return brecha > 0.25, (f"si el pobre ahorra 0.10 y el rico 0.20, la brecha NO se cierra "
                           f"({100 * brecha:.0f}% permanente): la convergencia es CONDICIONAL a la estructura")


def _v_mitad_de_camino():
    ngd = _ngd(_P0)
    ks = _solow.k_estrella(_P0["s_pobre"], _P0["A"], _P0["alpha"], ngd)
    lam = _solow.velocidad(_P0["alpha"], ngd)
    t_medio = int(np.ceil(np.log(2) / lam))
    k_p = _solow.trayectoria(0.9 * ks, _P0["s_pobre"], _P0["A"], _P0["alpha"], ngd, t_medio + 5)
    brecha0, brecha_t = ks - k_p[0], ks - k_p[t_medio]
    return brecha_t <= brecha0 / 2 + 1e-9, (f"la mitad de la brecha se cierra en ~{t_medio} períodos "
                                            "(el reloj de m27 gobierna también la convergencia entre países)")


MODELO = Modelo(
    id="m30", nivel=5,
    nombre="Convergencia (pobres y ricos)",
    xlabel="Período $t$", ylabel="Ingreso por trabajador ($y_t$)",
    parametros=[
        Parametro("s_pobre", _P0["s_pobre"], 0.05, 0.5, 0.01, "Ahorro del país pobre", grupo="estructura",
                  definicion="igual al rico = convergencia absoluta; distinto = condicional"),
        Parametro("s_rico", _P0["s_rico"], 0.05, 0.5, 0.01, "Ahorro del país rico", grupo="estructura"),
        Parametro("k0_pobre", _P0["k0_pobre"], 0.2, 6.0, 0.2, "Capital inicial pobre", grupo="historia"),
        Parametro("k0_rico", _P0["k0_rico"], 2.0, 12.0, 0.5, "Capital inicial rico", grupo="historia"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α", grupo="estructura"),
        Parametro("A", _P0["A"], 0.5, 2.0, 0.05, "Productividad común A", grupo="estructura"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="estructura"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="estructura"),
        Parametro("T", _P0["T"], 20, 150, 5, "Períodos simulados", grupo="historia"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Los países pobres alcanzan a los ricos — y por qué la respuesta empírica es 'solo los parecidos'?",
        variables=[("y_pobre, y_rico", "sendas de dos economías — endógenas"),
                   ("k0", "la HISTORIA de cada una — condición inicial"),
                   ("s, A, n, δ", "la ESTRUCTURA de cada una — su destino")],
        derivacion=["\\frac{\\Delta k}{k} = s\\,A\\,k^{\\alpha-1} - (n+\\delta)",
                    "k \\downarrow \\;\\Rightarrow\\; k^{\\alpha-1} \\uparrow \\;\\Rightarrow\\; crecer\\;m\\acute{a}s\\;r\\acute{a}pido",
                    "destino: k^*(s, A, n, \\delta) \\;— \\;la\\;estructura,\\;no\\;la\\;historia"],
        contexto=("¿Se cierra la brecha entre naciones? Baumol (1986, mención) "
                  "encontró convergencia… en un club selecto de países ricos; al "
                  "ampliar la muestra, desaparecía. Solow explica ambas cosas con un "
                  "solo mecanismo: los rendimientos decrecientes empujan a cada país "
                  "hacia SU k* — economías con estructuras parecidas convergen entre "
                  "sí (Europa de posguerra, la OCDE), y las de estructuras distintas "
                  "convergen… a destinos distintos. La pregunta correcta no es '¿alcanzarán?' "
                  "sino '¿a qué estado estacionario va cada quien?'"),
        autores=("Aplicación comparada del Solow (1956); evidencia: Baumol (1986), "
                 "Barro y Sala-i-Martin (años 90, β y σ-convergencia — menciones)."),
        supuestos=["Ambas economías son Solow cerrados: sin comercio, migración ni flujos de capital (que ACELERARÍAN la convergencia — su ausencia empírica es la paradoja de Lucas, mención).",
                   "Misma tecnología A disponible (la difusión es gratis aquí).",
                   "Estructuras constantes: s y n no cambian con el nivel de ingreso."],
        ecuaciones=[
            Ecuacion("\\frac{\\Delta k}{k} = s\\,A\\,k^{\\alpha-1} - (n+\\delta)", "crecer según cuán lejos",
                     "el término k^{α−1} decrece con k: el capital escaso rinde más — la ventaja "
                     "del atraso (Gerschenkron, mención) hecha aritmética."),
            Ecuacion("\\lim y_{pobre} = \\lim y_{rico} \\iff misma\\;estructura", "condicional vs absoluta",
                     "igual (s,A,n,δ) → mismo k*: la brecha muere. Distinta estructura → brechas "
                     "PERMANENTES aunque ambos crezcan."),
        ],
        intuicion=("La convergencia no es solidaridad del sistema: es rendimiento "
                   "decreciente. Por eso opera entre Alemania y Francia (gemelos "
                   "estructurales devastados en 1945, con k lejos de k*) y no entre "
                   "Níger y Noruega (estructuras — s, instituciones, A efectiva — "
                   "distintas). Para el Perú la lectura es directa: converger a EE.UU. "
                   "exige parecerse en estructura, no solo acumular."),
        equilibrio=("Cada economía converge monótonamente a su propio k* (m26-m27); "
                    "la 'brecha' es la diferencia de dos transiciones y muere solo si "
                    "los destinos coinciden."),
        limitaciones=[
            "Sin difusión tecnológica ni flujos de capital: en el mundo real la tecnología viaja (acelera convergencia) y el capital NO fluye a los pobres como predice el rendimiento (paradoja de Lucas, mención).",
            "σ-convergencia (dispersión) puede no caer aunque haya β-convergencia (shocks nuevos re-abren brechas).",
            "Si la pobreza misma deprime s o A, la estructura es endógena — exactamente la trampa de m31.",
        ],
        evolucion=("La condicionalidad abre dos agendas: ¿qué pasa si la estructura "
                   "depende del nivel? (trampa de pobreza, m31); ¿y si α efectivo es "
                   "mayor por capital humano? (m33: convergencia lenta como la "
                   "observada). El caso peruano — converger o no con datos del BCRP — "
                   "es m97 (nivel 12)."),
    ),
    escenarios=[
        Escenario("gemelos_estructurales", "misma estructura, historias distintas (posguerra)",
                  {"s_pobre": 0.20, "s_rico": 0.20},
                  "el pobre crece más rápido y la brecha muere: la convergencia del "
                  "'club' europeo de posguerra.",
                  cadena=["mismo k* de destino", "el pobre está más lejos", "rendimientos altos del capital escaso",
                          "crece más rápido (β-convergencia)", "brecha → 0"]),
        Escenario("estructuras_distintas", "el pobre ahorra la mitad (s = 0.10)",
                  {"s_pobre": 0.10},
                  "crece rápido al inicio (β-convergencia hacia SU k*)… y se detiene "
                  "lejos: brecha permanente de ~29% — convergencia condicional.",
                  cadena=["k* pobre < k* rico", "β-convergencia hacia destinos DISTINTOS",
                          "el pobre se frena antes", "brecha permanente", "estructura > historia"]),
        Escenario("milagro_de_ahorro", "el pobre ahorra MÁS que el rico (s = 0.35)",
                  {"s_pobre": 0.35},
                  "el sorpasso: partiendo 8 veces atrás, termina POR ENCIMA — la "
                  "aritmética de Corea del Sur.",
                  cadena=["s pobre > s rico", "k* pobre > k* rico", "β-convergencia + destino mayor",
                          "adelantamiento (sorpasso)", "la historia no condena"]),
    ],
    verificaciones=[
        Verificacion("β-convergencia: el que parte atrás crece más rápido", _v_beta_convergencia),
        Verificacion("misma estructura ⇒ brecha exactamente cero", _v_absoluta_con_misma_estructura),
        Verificacion("estructura distinta ⇒ brecha permanente", _v_condicional),
        Verificacion("el reloj de la convergencia es el de m27", _v_mitad_de_camino),
    ],
    notas="La estructura decide el destino; la historia solo decide desde dónde se parte.",
)
