"""simuladores/macro/modelos/nivel_08/m59_shock_monetario.py — el shock monetario: RBC vs NK (nivel 8).

EL experimento que separa a las dos escuelas modernas. Mismo shock dM en
dos mundos:
  RBC (precios flexibles):  p_t = dM desde t=0  ⇒  y_t = 0 SIEMPRE
  NK  (Calvo, m53):         p_t = (1−θ^{t+1})·dM  ⇒  y_t = θ^{t+1}·dM
Ambos coinciden en el largo plazo (neutralidad, m35); difieren en TODO el
tránsito. La evidencia VAR (Christiano-Eichenbaum-Evans, mención) encuentra
efectos reales significativos y persistentes del dinero: punto para el NK.

Procedencia: contraste didáctico estándar entre paradigmas — conocimiento
general; evidencia: CEE (1999, mención).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    pth = p["theta"] ** (t + 1)
    y_nk = pth * p["dM"]
    p_nk = (1 - pth) * p["dM"]
    y_rbc = np.zeros(T + 1)
    return t, y_nk, p_nk, y_rbc


def _curvas(p):
    t, y_nk, p_nk, y_rbc = _sendas(p)
    return {"lineas": {"producto NK: $y_t = \\theta^{t+1}dM$": (t, y_nk, config.AZUL2),
                       "precios NK: $p_t$": (t, p_nk, config.ROJO),
                       "producto RBC: $y_t = 0$": (t, y_rbc, config.GRIS),
                       "shock $dM$ (destino común)": (t, np.full(len(t), p["dM"]), config.DORADO)},
            "anotacion": (f"mismo shock, dos mundos:\n"
                          f"RBC: neutralidad instantánea (todo a precios en $t=0$)\n"
                          f"NK: el dinero trabaja {1 / (1 - p['theta']):.1f} períodos "
                          f"(área real = {p['theta'] / (1 - p['theta']) * p['dM']:.1f})")}


def _resultados(p):
    return {"impacto real NK (θ·dM)": p["theta"] * p["dM"],
            "impacto real RBC": 0.0,
            "área real NK (θ/(1−θ)·dM)": p["theta"] / (1 - p["theta"]) * p["dM"],
            "precios RBC en t=0 (=dM)": p["dM"],
            "destino común (largo plazo)": p["dM"]}


def _ecuaciones_calibradas(p):
    return [f"$RBC: \\;p_0 = {p['dM']:.0f}, \\;y_t = 0$",
            f"$NK: \\;y_t = {p['theta']:.2f}^{{\\,t+1}} \\times {p['dM']:.0f}$"]


_P0 = {"theta": 0.7, "dM": 10.0, "T": 12.0}


def _v_rbc_neutral():
    t, y_nk, p_nk, y_rbc = _sendas(_P0, T=100)
    return bool(np.all(np.abs(y_rbc) < 1e-12)), \
        "en el mundo RBC el dinero no mueve el producto NI UN período: neutralidad instantánea (m42)"


def _v_nk_trabaja():
    t, y_nk, p_nk, y_rbc = _sendas(_P0)
    razones = y_nk[1:6] / y_nk[0:5]
    ok = abs(float(y_nk[0]) - _P0["theta"] * _P0["dM"]) < 1e-12 \
        and bool(np.all(np.abs(razones - _P0["theta"]) < 1e-12))
    return ok, (f"en el mundo NK el impacto es θ·dM = {_P0['theta'] * _P0['dM']:.0f} y decae a "
                f"razón θ: el dinero trabaja mientras haya precios de Calvo sin reajustar")


def _v_destino_comun():
    t, y_nk, p_nk, y_rbc = _sendas(_P0, T=400)
    ok = abs(float(p_nk[-1]) - _P0["dM"]) < 1e-9 and abs(float(y_nk[-1])) < 1e-9
    return ok, ("ambos mundos terminan igual (p=dM, y=0): la disputa es SOLO por el "
                "tránsito — la neutralidad de largo plazo (m35) es terreno común")


def _v_area_real():
    t, y_nk, p_nk, y_rbc = _sendas(_P0, T=2000)
    area = float(np.sum(y_nk))
    teo = _P0["theta"] / (1 - _P0["theta"]) * _P0["dM"]
    return abs(area - teo) < 1e-6, \
        (f"el efecto real acumulado del dinero = θ/(1−θ)·dM = {teo:.1f} exacto: "
         "lo que la rigidez 'compra' tiene fórmula cerrada")


MODELO = Modelo(
    id="m59", nivel=8,
    nombre="Shock monetario (RBC vs NK)",
    xlabel="Período $t$", ylabel="Respuesta al shock $dM$",
    parametros=[
        Parametro("theta", _P0["theta"], 0.0, 0.9, 0.05, "Rigidez de Calvo θ (mundo NK)", grupo="estructura",
                  definicion="θ=0 colapsa el NK en el RBC: un solo mundo"),
        Parametro("dM", _P0["dM"], 2, 25, 1, "Shock monetario dM", grupo="experimento"),
        Parametro("T", _P0["T"], 6, 30, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿El dinero mueve al producto? El experimento que separa a las dos escuelas modernas — y lo que dicen los datos.",
        variables=[("y_RBC", "cero por construcción — la neutralidad instantánea"),
                   ("y_NK", "θ^{t+1}·dM — el tránsito que la rigidez compra"),
                   ("θ", "el único parámetro en disputa — y toda la política en juego")],
        derivacion=["RBC: \\;precios\\;flexibles \\Rightarrow p = dM,\\; y = 0 \\;(m42)",
                    "NK: \\;Calvo \\Rightarrow p_t = (1-\\theta^{t+1})dM \\;(m53)",
                    "y_t^{NK} = \\theta^{t+1}\\,dM \\;\\to\\; 0 \\;(destino\\;común)"],
        contexto=("Tras m56 y m57, la macro moderna quedó con dos esqueletos "
                  "rivales que comparten método (equilibrio, racionalidad, IRFs) y "
                  "difieren en UNA célula: θ. Este modelo ejecuta el experimento "
                  "discriminante — un shock monetario idéntico en ambos mundos. El "
                  "RBC predice nada; el NK predice una comba θ^{t+1}. La evidencia "
                  "VAR (Christiano-Eichenbaum-Evans, mención) encuentra combas: "
                  "producto respondiendo por trimestres a sorpresas monetarias. El "
                  "asalto lo ganó el NK — con la réplica RBC de que identificar "
                  "'sorpresas' monetarias en datos es un arte disputado (mención)."),
        autores=("El contraste como método: la literatura de los 90; evidencia "
                 "canónica: Christiano, Eichenbaum y Evans (1999, mención); la "
                 "réplica de identificación: literatura VAR posterior (mención)."),
        supuestos=["Los dos mundos comparten TODO salvo θ: el experimento es limpio por construcción.",
                   "El shock dM es sorpresivo y de una vez (los anunciados reactivan a m42).",
                   "Formas reducidas de m53/m42: los mundos completos (m56/m57) darían combas más ricas, no distinta moraleja."],
        ecuaciones=[
            Ecuacion("y_t^{RBC} = 0, \\quad y_t^{NK} = \\theta^{t+1}dM", "las dos predicciones",
                     "cero contra comba: pocas veces dos paradigmas difieren tan nítido en un "
                     "experimento tan simple — por eso este es EL test."),
            Ecuacion("\\int y^{NK} = \\frac{\\theta}{1-\\theta}\\,dM", "el precio de la rigidez",
                     "el efecto real acumulado tiene fórmula cerrada: con θ=0.7, cada sol de "
                     "shock compra 2.33 soles-período de producto."),
        ],
        intuicion=("La disputa RBC-NK no es teológica: es el valor de UN parámetro "
                   "con consecuencias de política enormes. Si θ≈0, el banco central "
                   "solo administra inflación (m42) y la estabilización sobra; si "
                   "θ≈0.7, la ventana de m53 existe y la regla de m56 tiene trabajo "
                   "real. Los datos — VARs, microdatos de precios (mención) — votan "
                   "por θ intermedio-alto en horizontes cortos: el consenso DSGE es "
                   "un RBC con Calvo, no un bando puro."),
        equilibrio=("Ambos mundos convergen al MISMO punto (neutralidad verificada): "
                    "la macro moderna no discute el destino (nivel 6 entero), "
                    "discute el tránsito — su duración 1/(1−θ) y su área θ/(1−θ)·dM, "
                    "ambas verificadas exactas."),
        limitaciones=[
            "Formas reducidas: los mundos completos añaden persistencia endógena (hábitos, indexación — los DSGE medianos, mención m61).",
            "La 'sorpresa monetaria' empírica es difícil de aislar: la crítica de identificación sigue viva (mención).",
            "θ no es constante: cae con inflación alta (los 80 peruanos tenían θ≈0) — la rigidez es un lujo de la estabilidad (m40).",
        ],
        evolucion=("Con el veredicto monetario a favor del NK, m60 repite el duelo "
                   "con el shock FISCAL (multiplicadores por régimen) y m61 cierra "
                   "el nivel con la asignatura pendiente de ambos: la propagación. "
                   "La versión peruana del experimento — tasa BCRP → producto e "
                   "inflación — es m101."),
    ),
    escenarios=[
        Escenario("el_experimento", "dM = 10 en ambos mundos (θ = 0.7)",
                  {"theta": 0.7},
                  "el RBC no se inmuta; el NK produce una comba de impacto 7 que "
                  "muere en ~3 períodos: la evidencia VAR se parece a la comba.",
                  cadena=["dM sorpresivo", "RBC: precios saltan ya (y=0)",
                          "NK: 70% de precios anclados", "y = θ·dM al impacto",
                          "reajustes de Calvo período a período", "destino común: neutralidad"]),
        Escenario("mundo_unico", "θ = 0: el NK colapsa en el RBC",
                  {"theta": 0.0},
                  "las dos líneas de producto se funden en cero: sin rigidez no hay "
                  "disputa — todo el debate moderno vive dentro de θ.",
                  cadena=["θ = 0", "todos reajustan en t=0", "NK ≡ RBC",
                          "el dinero es velo instantáneo (m42)"]),
        Escenario("rigidez_alta", "θ = 0.85: contratos largos",
                  {"theta": 0.85},
                  "el efecto real dura ~6.7 períodos y acumula 57: en economías "
                  "estables (ancladas, m40) la política monetaria es más potente — "
                  "la paradoja de la credibilidad.",
                  cadena=["ancla creíble ⇒ precios duermen (θ alto)",
                          "el mismo dM rinde más producto", "área θ/(1−θ) crece",
                          "la estabilidad hace potente al banco central"]),
    ],
    verificaciones=[
        Verificacion("RBC: neutralidad instantánea exacta (y=0 ∀t)", _v_rbc_neutral),
        Verificacion("NK: impacto θ·dM y decaimiento θ exactos", _v_nk_trabaja),
        Verificacion("destino común: la neutralidad de m35 es terreno compartido", _v_destino_comun),
        Verificacion("área real NK = θ/(1−θ)·dM exacta", _v_area_real),
    ],
    notas="Dos paradigmas, un parámetro: θ. Los datos votan comba — el consenso es un RBC con Calvo.",
)
