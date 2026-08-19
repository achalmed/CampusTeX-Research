# m72_burbuja_activos.py — burbuja de activos: precio vs fundamento (nivel 10).
#
# El precio fundamental de un activo es el valor presente de sus dividendos:
#   P* = d / (r − g_d)      (Gordon; d dividendo, g_d su crecimiento)
# Una burbuja es un componente B_t que se aparta del fundamental creciendo
# a la tasa que exige el arbitraje (a nadie le conviene tenerla si no):
#   B_{t+1} = (1+r)·B_t / prob_supervivencia
# Con probabilidad (1−q) de estallar cada período, la burbuja SOBREVIVIENTE
# crece a (1+r)/(1−q) — más rápido, para compensar el riesgo de colapso.
# Al estallar, el precio vuelve al fundamental: caída = B_t / P_t.
#
# Procedencia: modelo de Gordon (mención); burbujas racionales (Blanchard-
# Watson 1982 — mención); exuberancia irracional (Shiller — mención) —
# conocimiento general; calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    fund = p["d"] / (p["r"] / 100 - p["gd"] / 100)
    g_burbuja = (1 + p["r"] / 100) / (1 - p["q"] / 100)
    B = p["B0"] * g_burbuja ** t
    precio = fund + B
    t_est = int(round(p["t_estallido"]))
    precio_real = precio.copy()
    if t_est <= T:
        precio_real[t_est:] = fund                     # estalla: vuelve al fundamental
    return t, np.full(T + 1, fund), precio, precio_real


def _curvas(p):
    t, fund, precio, precio_real = _sendas(p)
    t_est = int(round(p["t_estallido"]))
    caida = (precio[t_est] - fund[0]) / precio[t_est] * 100 if t_est < len(precio) else 0.0
    return {"lineas": {"precio observado (con estallido)": (t, precio_real, config.AZUL2),
                       "fundamental $P^* = d/(r-g_d)$": (t, fund, config.GRIS),
                       "senda de burbuja (si no estalla)": (t, precio, config.ROJO)},
            "puntos": [(t_est, float(fund[0]), f"estallido: −{caida:.0f}%")] if t_est < len(precio) else [],
            "anotacion": (f"fundamental $P^* = {p['d']:.0f}/({p['r'] / 100:.2f}-{p['gd'] / 100:.2f}) "
                          f"= {float(fund[0]):.0f}$\n"
                          f"la burbuja crece a $(1+r)/(1-q) = "
                          f"{(1 + p['r'] / 100) / (1 - p['q'] / 100):.3f}$\n"
                          "más rápido que r: paga por el riesgo de estallar")}


def _resultados(p):
    t, fund, precio, precio_real = _sendas(p)
    t_est = int(round(p["t_estallido"]))
    return {"precio fundamental P*": float(fund[0]),
            "burbuja al estallar B_t": float(precio[t_est] - fund[0]) if t_est < len(precio) else 0.0,
            "precio pre-estallido": float(precio[t_est]) if t_est < len(precio) else float(precio[-1]),
            "caída al estallar (%)": (float(precio[t_est] - fund[0]) / float(precio[t_est]) * 100)
                if t_est < len(precio) else 0.0,
            "tasa de la burbuja (1+r)/(1−q)": (1 + p["r"] / 100) / (1 - p["q"] / 100),
            "prima de crecimiento sobre r (pp)": ((1 + p["r"] / 100) / (1 - p["q"] / 100) - 1) * 100 - p["r"]}


def _ecuaciones_calibradas(p):
    fund = p["d"] / (p["r"] / 100 - p["gd"] / 100)
    g = (1 + p["r"] / 100) / (1 - p["q"] / 100)
    return [f"$P^* = {p['d']:.0f}/({p['r'] / 100:.2f}-{p['gd'] / 100:.2f}) = {fund:.0f}$",
            f"$B_{{t+1}} = \\frac{{1+{p['r'] / 100:.2f}}}{{1-{p['q'] / 100:.2f}}}\\,B_t "
            f"= {g:.3f}\\,B_t$"]


_P0 = {"d": 4.0, "r": 5.0, "gd": 1.0, "B0": 10.0, "q": 10.0, "t_estallido": 12.0, "T": 20.0}


def _v_fundamental_gordon():
    fund = _P0["d"] / (_P0["r"] / 100 - _P0["gd"] / 100)
    return abs(fund - 100.0) < 1e-9, \
        f"P* = d/(r−g_d) = {fund:.0f}: el valor presente de dividendos crecientes (Gordon)"


def _v_burbuja_supera_r():
    g = (1 + _P0["r"] / 100) / (1 - _P0["q"] / 100)
    return g - 1 > _P0["r"] / 100, \
        (f"la burbuja crece {(g - 1) * 100:.1f}% > r={_P0['r']:.0f}%: DEBE superar a r para "
         "compensar la chance de estallar — más riesgo, más prisa (Blanchard-Watson)")


def _v_arbitraje():
    g = (1 + _P0["r"] / 100) / (1 - _P0["q"] / 100)
    q = _P0["q"] / 100
    retorno_esperado = (1 - q) * g - 1                 # sobrevive: gana g; estalla: pierde todo
    return abs(retorno_esperado - _P0["r"] / 100) < 1e-9, \
        (f"retorno esperado = (1−q)·g − 1 = {retorno_esperado * 100:.1f}% = r: la burbuja "
         "racional no ofrece almuerzo gratis — solo compensa su propio riesgo")


def _v_estallido_al_fundamental():
    t, fund, precio, precio_real = _sendas(_P0)
    t_est = int(_P0["t_estallido"])
    return abs(float(precio_real[t_est]) - float(fund[0])) < 1e-9, \
        (f"al estallar, el precio vuelve EXACTO al fundamental ({float(fund[0]):.0f}): "
         "la burbuja era todo lo que sobraba — y desaparece de golpe")


MODELO = Modelo(
    id="m72", nivel=10,
    nombre="Burbuja de activos",
    xlabel="Período $t$", ylabel="Precio del activo",
    parametros=[
        Parametro("q", _P0["q"], 1, 30, 1, "Prob. de estallar por período (%)", grupo="riesgo",
                  definicion="cuanto más probable el colapso, MÁS rápido crece la sobreviviente"),
        Parametro("B0", _P0["B0"], 0, 50, 5, "Tamaño inicial de la burbuja B0", grupo="burbuja"),
        Parametro("t_estallido", _P0["t_estallido"], 3, 19, 1, "Período del estallido", grupo="experimento"),
        Parametro("d", _P0["d"], 1, 10, 0.5, "Dividendo d", grupo="fundamental"),
        Parametro("r", _P0["r"], 2, 10, 0.5, "Tasa de descuento r (%)", grupo="fundamental"),
        Parametro("gd", _P0["gd"], 0, 4, 0.5, "Crecimiento del dividendo g_d (%)", grupo="fundamental"),
        Parametro("T", _P0["T"], 12, 30, 2, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Puede un precio despegarse del valor 'real' de un activo SIN que nadie sea irracional — y por qué el estallido es inevitable?",
        variables=[("P*", "el fundamental — valor presente de dividendos (Gordon)"),
                   ("B_t", "la burbuja — el sobreprecio que crece para sobrevivir"),
                   ("q", "la prob. de estallar — que se autoimpone la prisa")],
        derivacion=["P^* = \\frac{d}{r - g_d} \\;\\;(Gordon)",
                    "arbitraje: \\;(1-q)\\,g_B\\,B - B = r\\,B",
                    "g_B = \\frac{1+r}{1-q} > 1+r"],
        contexto=("Las burbujas parecen exigir tontos, pero Blanchard y Watson "
                  "(1982, mención) mostraron que pueden ser RACIONALES: si todos "
                  "esperan que el sobreprecio siga subiendo lo suficiente, comprar "
                  "caro es óptimo — la 'teoría del más tonto' formalizada. La "
                  "condición de arbitraje impone la tragedia: para compensar la "
                  "probabilidad q de estallar, la burbuja debe crecer MÁS rápido "
                  "que la tasa de interés, lo que la hace cada vez más grande y su "
                  "estallido cada vez más violento. Tulipanes, puntocom, hipotecas "
                  "de 2008: la aritmética es la misma; la irracionalidad de Shiller "
                  "(exuberancia, mención) solo cambia de dónde sale q."),
        autores=("Fundamental: Gordon (mención); burbujas racionales: Blanchard y "
                 "Watson (1982, mención); exuberancia irracional y evidencia: "
                 "Shiller (mención); imposibilidad en horizonte finito con agentes "
                 "racionales: Tirole (mención)."),
        supuestos=[
            "Fundamental de Gordon con r > g_d (si no, el valor presente diverge — mención).",
            "Burbuja racional: crece exactamente lo que el arbitraje exige (la irracional crece 'porque sí' — mismo estallido).",
            "Estallido exógeno en t dado: en la realidad el gatillo es endógeno (liquidez, crédito, m71) e impredecible.",
        ],
        ecuaciones=[
            Ecuacion("g_B = \\frac{1+r}{1-q}", "la prisa de la burbuja",
                     "cuanto mayor el riesgo de estallar (q), más rápido debe subir la burbuja "
                     "que sobrevive — la aceleración que precede a todo crac."),
            Ecuacion("(1-q)\\,g_B - 1 = r", "el arbitraje sin almuerzo gratis",
                     "el retorno ESPERADO (ganar g_B con prob 1−q, perder todo con q) iguala a r: "
                     "la burbuja racional no promete nada extra — solo paga su riesgo (verificado)."),
        ],
        intuicion=("La burbuja racional es una cadena de apuestas donde cada "
                   "eslabón es individualmente sensato y el conjunto es una bomba "
                   "de tiempo: todos saben que estallará, nadie sabe cuándo, y "
                   "salir antes cuesta la ganancia. El gráfico muestra la crueldad "
                   "aritmética: como la burbuja acelera, cuanto más tarde estalla, "
                   "más alto es el precio y más brutal la caída al fundamental. "
                   "Por eso las burbujas largas dejan cráteres — y por qué el "
                   "crédito que las financia (m71) convierte el crac en crisis."),
        equilibrio=("El fundamental P* es el único equilibrio SIN burbuja; con "
                    "burbuja hay un continuo de sendas explosivas, todas terminando "
                    "en el mismo colapso al fundamental (verificado). La "
                    "indeterminación — cuál senda, cuándo estalla — es la marca de "
                    "las expectativas autocumplidas (como m74)."),
        limitaciones=[
            "El gatillo es exógeno aquí; en crisis reales lo jala el crédito y el apalancamiento (m71) — la burbuja peligrosa es la APALANCADA (2008 vs puntocom).",
            "Horizonte infinito: con agentes racionales y horizonte finito las burbujas no pueden existir (Tirole, mención) — hacen falta fricciones o irracionalidad.",
            "Un activo aislado: el contagio entre mercados (inmobiliario→bancario→real) es el nivel sistémico (m80).",
        ],
        evolucion=("Da el detonante que m71 esperaba: la burbuja apalancada que "
                   "estalla golpea balances frágiles. m73 (corrida) y m79 "
                   "(acelerador) cierran el mecanismo de propagación, y m80 lo "
                   "vuelve sistémico. La burbuja inmobiliaria de 2008 es el hilo "
                   "que conecta todo el nivel."),
    ),
    escenarios=[
        Escenario("burbuja_racional", "sobreprecio de 10 creciendo con q=10%",
                  {"q": 10.0, "t_estallido": 12.0},
                  "el precio triplica al fundamental antes de estallar y cae ~66% "
                  "de golpe: la senda puntocom (mención) en un gráfico.",
                  cadena=["expectativa de subida", "comprar caro es óptimo (más tonto)",
                          "la burbuja crece a (1+r)/(1−q)", "acelera hacia el estallido",
                          "colapso al fundamental: −66%"]),
        Escenario("estallido_tardio", "la misma burbuja estalla en t=18",
                  {"q": 10.0, "t_estallido": 18.0},
                  "seis períodos más de euforia = precio mucho más alto = caída aún "
                  "más brutal: esperar no salva, agrava.",
                  cadena=["la burbuja sigue acelerando", "precio pre-crac mayor",
                          "la distancia al fundamental crece", "el cráter es más profundo"]),
        Escenario("mercado_nervioso", "alta prob. de estallar: q=25%",
                  {"q": 25.0},
                  "la burbuja crece 40% por período — vertiginoso: cuando el "
                  "mercado sabe que es frágil, la prisa del arbitraje la vuelve "
                  "aún más explosiva.",
                  cadena=["↑q (todos temen el crac)", "el arbitraje exige más retorno",
                          "g_B se dispara", "la burbuja se infla más rápido",
                          "la fragilidad se autoalimenta"]),
    ],
    verificaciones=[
        Verificacion("fundamental = d/(r−g_d) exacto (Gordon)", _v_fundamental_gordon),
        Verificacion("la burbuja crece más rápido que r", _v_burbuja_supera_r),
        Verificacion("arbitraje: retorno esperado = r (sin almuerzo gratis)", _v_arbitraje),
        Verificacion("al estallar, vuelta exacta al fundamental", _v_estallido_al_fundamental),
    ],
    notas="Racional y condenada: cada eslabón es sensato, el conjunto es una bomba. El crédito (m71) la vuelve crisis.",
)
