# m63_deuda_publica.py — la deuda pública: la bola de nieve (nivel 9).
#
# La identidad de m62 iterada en el tiempo:
#   B_{t+1} = (1+r)·B_t − SP_t        (SP: superávit primario; déficit si <0)
# Sin crecimiento del PIB todavía (m64 lo trae), la aritmética es cruel:
#   con SP = 0, la deuda crece EXACTAMENTE a tasa r (interés compuesto);
#   el único SP que congela la deuda es  SP* = r·B_0  (servirla completa);
#   con déficit primario, la bola acelera: intereses sobre intereses.
#
# Procedencia: dinámica de deuda estándar (conocimiento general);
# calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _senda(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    B = np.empty(T + 1)
    B[0] = p["B0"]
    for t in range(T):
        B[t + 1] = (1 + p["r"] / 100) * B[t] - p["SP"]
    return np.arange(T + 1), B


def _curvas(p):
    t, B = _senda(p)
    sp_estrella = p["r"] / 100 * p["B0"]
    return {"lineas": {"deuda $B_t$": (t, B, config.ROJO),
                       "deuda inicial $B_0$": (t, np.full(len(t), p["B0"]), config.GRIS)},
            "anotacion": (f"$B_{{t+1}} = {1 + p['r'] / 100:.3f}\\,B_t - {p['SP']:.0f}$\n"
                          f"$SP^*$ que congela la deuda $= r\\,B_0 = {sp_estrella:.1f}$\n"
                          f"tu $SP = {p['SP']:.0f}$: "
                          f"{'la bola crece' if p['SP'] < sp_estrella else 'la deuda cede o se congela'}")}


def _resultados(p):
    t, B = _senda(p)
    return {"deuda final B_T": float(B[-1]),
            "crecimiento total (%)": 100 * (float(B[-1]) / p["B0"] - 1),
            "SP* que congela (= r·B0)": p["r"] / 100 * p["B0"],
            "intereses del primer año": p["r"] / 100 * p["B0"],
            "años para duplicar (sin SP)": float(np.log(2) / np.log(1 + p["r"] / 100))}


def _ecuaciones_calibradas(p):
    return [f"$B_{{t+1}} = (1+{p['r'] / 100:.2f})\\,B_t - {p['SP']:.0f}$",
            f"$SP^* = {p['r'] / 100:.2f} \\times {p['B0']:.0f} = {p['r'] / 100 * p['B0']:.1f}$"]


_P0 = {"B0": 200.0, "r": 5.0, "SP": -10.0, "T": 30.0}


def _v_recursion():
    t, B = _senda(_P0)
    res = np.max(np.abs(B[1:] - ((1 + _P0["r"] / 100) * B[:-1] - _P0["SP"])))
    return res < 1e-9, f"la recursión de m62 se cumple exacta en toda la senda (residuo {res:.1e})"


def _v_congelamiento():
    sp = _P0["r"] / 100 * _P0["B0"]
    t, B = _senda(dict(_P0, SP=sp), T=100)
    return bool(np.all(np.abs(B - _P0["B0"]) < 1e-6)), \
        (f"con SP = r·B0 = {sp:.0f}, la deuda queda EXACTAMENTE congelada para siempre: "
         "servir los intereses es correr para quedarse en el sitio")


def _v_interes_compuesto():
    t, B = _senda(dict(_P0, SP=0.0), T=50)
    teo = _P0["B0"] * (1 + _P0["r"] / 100) ** 50
    return abs(float(B[-1]) - teo) < 1e-6, \
        (f"con SP=0 la deuda crece exactamente a (1+r)^t: B_50 = {float(B[-1]):,.0f} — "
         "el interés compuesto no necesita cómplices")


def _v_duplicacion():
    t, B = _senda(dict(_P0, SP=0.0), T=60)
    teo = np.log(2) / np.log(1 + _P0["r"] / 100)
    idx = int(np.argmax(B >= 2 * _P0["B0"]))
    return abs(idx - np.ceil(teo)) < 1 + 1e-9, \
        f"la deuda se duplica en ⌈{teo:.1f}⌉ años (regla del ln2): simulación = fórmula"


MODELO = Modelo(
    id="m63", nivel=9,
    nombre="Deuda pública (la bola de nieve)",
    xlabel="Año $t$", ylabel="Deuda $B_t$ (u.m.)",
    parametros=[
        Parametro("SP", _P0["SP"], -30, 30, 2.5, "Superávit primario SP", grupo="decisión",
                  definicion="negativo = déficit primario; la ÚNICA perilla de control"),
        Parametro("r", _P0["r"], 1, 12, 0.5, "Tasa de interés r (%)", grupo="mercado"),
        Parametro("B0", _P0["B0"], 50, 500, 25, "Deuda inicial B0", grupo="herencia"),
        Parametro("T", _P0["T"], 10, 60, 5, "Años simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué las deudas 'manejables' se vuelven inmanejables solas — y cuál es el único freno?",
        variables=[("B_t", "la deuda — crece sola a tasa r si nadie la sirve"),
                   ("SP", "el superávit primario — el único control de la política"),
                   ("SP* = r·B0", "el precio de congelar — servir la herencia completa")],
        derivacion=["B_{t+1} = (1+r)\\,B_t - SP \\;\\;(m62\\;iterada)",
                    "SP = 0 \\Rightarrow B_t = B_0\\,(1+r)^t",
                    "B_{t+1} = B_t \\Rightarrow SP^* = r\\,B_0"],
        contexto=("El interés compuesto — 'la fuerza más poderosa', reza la frase "
                  "apócrifa (mención) — trabaja también contra los fiscos. Esta es "
                  "la mecánica desnuda: sin crecimiento económico que la licúe "
                  "(m64), toda deuda con déficit primario es una bola de nieve, y "
                  "hasta el DÉFICIT CERO pierde: la deuda sigue creciendo a tasa r. "
                  "La única paz es el superávit que sirva los intereses — y su "
                  "tamaño, r·B, lo fijan el pasado (B) y el mercado (r), no el "
                  "ministro."),
        autores=("Aritmética de deuda estándar (manuales de finanzas públicas, "
                 "conocimiento general); la lectura dramática — deuda como bola de "
                 "nieve — es patrimonio del análisis fiscal de los 80-90 (mención)."),
        supuestos=["Sin PIB: los niveles absolutos exageran — el ratio deuda/PIB (m64) es la métrica real y trae el gran alivio (g).",
                   "r constante y exógena: sin prima de riesgo creciente con B (el círculo vicioso llega en m65/m76).",
                   "SP constante: la política real ajusta — la pregunta es si ALCANZA (m65)."],
        ecuaciones=[
            Ecuacion("B_t = B_0(1+r)^t - SP\\,\\frac{(1+r)^t - 1}{r}", "la senda cerrada",
                     "interés compuesto contra anualidad: la carrera entre la herencia "
                     "capitalizándose y el esfuerzo primario acumulándose."),
            Ecuacion("SP^* = r\\,B_0", "el precio de la paz",
                     "congelar la deuda exige entregar cada año exactamente los intereses: ni un "
                     "sol para nada más — por eso el ratio a PIB (m64) cambia todo."),
        ],
        intuicion=("La trampa psicológica fiscal: 'déficit cero' SUENA a disciplina, "
                   "pero con primario cero la deuda crece a tasa r igual — los "
                   "intereses se pagan con deuda nueva. El gráfico lo hace visible: "
                   "la única línea plana es la de SP = r·B0. Todo lo demás — la "
                   "espera, el 'ya casi', el déficit pequeñito — es la bola "
                   "engordando a interés compuesto."),
        equilibrio=("B* existe solo si SP ≥ r·B0 (congelada o decreciente); es "
                    "INESTABLE hacia arriba: una vez que B crece, el SP* requerido "
                    "crece con ella — la persecución que m65 formaliza."),
        limitaciones=[
            "Sin PIB ni inflación: el crecimiento nominal licúa deudas — m64 introduce (r−g), la resta que decide todo.",
            "r fija: los mercados suben r cuando B asusta (m48: prima) — la bola real acelera en las malas.",
            "Sin estructura de plazos ni moneda: la deuda en dólares de los 80 latinoamericanos era otra bestia (m84, m110).",
        ],
        evolucion=("m64 divide esta ecuación por el PIB y aparece el término (r−g) "
                   "— la aritmética amable o cruel según quién gane la carrera. m65 "
                   "convierte la mecánica en diagnóstico (¿cuánta deuda cabe?) y "
                   "m76 en drama (¿qué pasa cuando el mercado dice basta?)."),
    ),
    escenarios=[
        Escenario("deficit_cronico", "déficit primario de 10 por 30 años",
                  {"SP": -10.0},
                  "la deuda pasa de 200 a 1,529: intereses sobre intereses sobre "
                  "déficits — la bola de nieve completa.",
                  cadena=["déficit primario", "se financia con deuda", "más intereses mañana",
                          "que se financian con más deuda", "B crece más que exponencial"]),
        Escenario("deficit_cero_enganoso", "primario equilibrado (SP = 0)",
                  {"SP": 0.0},
                  "aun sin déficit primario, la deuda crece 332% en 30 años: el "
                  "'déficit cero' no detiene el interés compuesto.",
                  cadena=["SP = 0", "los intereses se pagan con deuda nueva",
                          "B crece exactamente a (1+r)^t", "duplicación cada ~14 años"]),
        Escenario("servir_la_deuda", "el superávit exacto: SP = r·B0 = 10",
                  {"SP": 10.0},
                  "la línea perfectamente plana: congelar cuesta TODO el servicio "
                  "de intereses, cada año, para siempre — o hasta que g ayude (m64).",
                  cadena=["SP = r·B0", "los intereses se pagan con primario",
                          "no se emite deuda nueva", "B constante exacta"]),
        Escenario("tasas_de_castigo", "el mercado sube r a 9%",
                  {"r": 9.0},
                  "el mismo déficit ahora duplica la deuda en la mitad del tiempo — "
                  "y el SP* requerido pasa de 10 a 18 sin que nadie votara nada.",
                  cadena=["↑r (mercado, m48)", "la bola acelera",
                          "SP* = r·B0 salta", "la meta se aleja mientras se corre (m65)"]),
    ],
    verificaciones=[
        Verificacion("recursión de m62 exacta en toda la senda", _v_recursion),
        Verificacion("SP = r·B0 congela la deuda exactamente", _v_congelamiento),
        Verificacion("con SP=0, crecimiento (1+r)^t exacto", _v_interes_compuesto),
        Verificacion("duplicación en ln2/ln(1+r) años", _v_duplicacion),
    ],
    notas="El interés compuesto contra el fisco: hasta el 'déficit cero' pierde. El alivio (g) llega en m64.",
)
