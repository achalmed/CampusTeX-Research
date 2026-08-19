# m25_ajuste_largo_plazo.py — ajuste dinámico hacia el largo plazo (nivel 4).
#
# La película que m23 no mostraba. Tras un shock PERMANENTE de demanda (dG, dM),
# las expectativas se revisan período a período (adaptativas, como m14):
#   Pe_{t+1} = P_t  →  la SRAS sube  →  el equilibrio de corto plazo se desliza
#   por la AD hasta aterrizar en la LRAS:  Y → Y*  y  P → P_LR (cerrado).
# Teorema verificable: a largo plazo la política de DEMANDA no deja producto,
# solo precios (ΔY_LP = 0 exacto; ΔP_LP > 0).
#
# Procedencia: mecanismo de ajuste estándar de la síntesis (manuales) —
# conocimiento general; dinámica Pe_{t+1}=P_t: expectativas adaptativas (m14).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _trayectoria(p, T=None):
    # ojo: en este modelo "T" son períodos; los impuestos van en "T_imp"
    F, bh, Ac = _adas.estructura(dict(p, T=p["T_imp"]))
    F1, M1 = F + p["dG"], p["M"] + p["dM"]
    T = int(round(T if T is not None else p["T"]))
    pe = p["Pe0"]
    Ys, Ps = [], []
    for _ in range(T + 1):
        Y, P = _adas.equilibrio_corto(F1, bh, Ac, M1, pe, p["lam"], p["Ystar"])
        Ys.append(Y); Ps.append(P)
        pe = P                                   # Pe_{t+1} = P_t
    p_lr = _adas.precio_largo_plazo(F1, bh, Ac, M1, p["Ystar"])
    return np.array(Ys), np.array(Ps), p_lr


def _curvas(p):
    F, bh, Ac = _adas.estructura(dict(p, T=p["T_imp"]))
    Ys, Ps, p_lr = _trayectoria(p)
    Y = np.linspace(600, 820, 200)
    ad = bh * (p["M"] + p["dM"]) / (Ac * Y - (F + p["dG"]))
    sras0 = p["Pe0"] + p["lam"] * (Y - p["Ystar"])
    sras_f = p_lr + p["lam"] * (Y - p["Ystar"])
    return {"lineas": {"AD (tras el shock)": (Y, ad, config.AZUL2),
                       "SRAS inicial ($P^e_0$)": (Y, sras0, config.VERDE),
                       "SRAS final ($P^e = P_{LR}$)": (Y, sras_f, config.DORADO),
                       "LRAS ($Y=Y^*$)": (np.full(2, p["Ystar"]), np.linspace(1.6, 2.6, 2), config.GRIS),
                       "trayectoria $(Y_t, P_t)$": (Ys, Ps, config.ROJO)},
            "puntos": [(float(Ys[0]), float(Ps[0]), "corto plazo ($t=0$)"),
                       (p["Ystar"], p_lr, f"largo plazo $({p['Ystar']:,.0f},\\,{p_lr:.2f})$")],
            "anotacion": (f"$P^e_{{t+1}} = P_t$: la SRAS sube sola\n"
                          f"$\\Delta Y$ de largo plazo $= 0$ (neutralidad del impulso)\n"
                          f"$P$: ${p['Pe0']:.2f} \\to {p_lr:.2f}$")}


def _resultados(p):
    Ys, Ps, p_lr = _trayectoria(p)
    dentro = np.where(np.abs(Ys - p["Ystar"]) < 1.0)[0]
    return {"Y de corto plazo (t=0)": float(Ys[0]),
            "P de corto plazo (t=0)": float(Ps[0]),
            "Y de largo plazo": p["Ystar"],
            "P de largo plazo (cerrado)": p_lr,
            "sobre-reacción inicial de Y": float(Ys[0]) - p["Ystar"],
            "períodos hasta |Y−Y*| < 1": float(dentro[0]) if len(dentro) else float(p["T"]),
            "ganancia de Y a largo plazo": 0.0}


_P0 = {"dG": 50.0, "dM": 0.0, "T": 15.0,
       "c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0, "G": 200.0, "T_imp": 100.0,
       "k": 0.5, "h": 10.0, "M": 590.0, "Pe0": 2.0, "lam": 0.004, "Ystar": 700.0}


def _v_neutralidad_demanda():
    p = dict(_P0)
    Ys, Ps, p_lr = _trayectoria(p, T=400)
    return abs(Ys[-1] - p["Ystar"]) < 1e-6, ("tras el ajuste completo el impulso de demanda NO deja "
                                             f"producto: Y_∞ = {Ys[-1]:,.2f} = Y* (solo quedan precios)")


def _v_convergencia_p():
    Ys, Ps, p_lr = _trayectoria(dict(_P0), T=400)
    return abs(Ps[-1] - p_lr) < 1e-6, (f"P converge exactamente al P de largo plazo cerrado "
                                       f"({p_lr:.3f}): la iteración y la fórmula coinciden")


def _v_monotonia():
    Ys, Ps, _ = _trayectoria(dict(_P0), T=100)
    ok = bool(np.all(np.diff(Ys) < 1e-12)) and bool(np.all(np.diff(Ps) > -1e-12))
    return ok, "la brecha se cierra sin oscilar: Y baja y P sube monótonamente hacia la LRAS"


def _v_corto_plazo_reacciona():
    Ys, _, _ = _trayectoria(dict(_P0), T=2)
    return Ys[0] > _P0["Ystar"], (f"en t=0 el impulso SÍ mueve producto (Y={Ys[0]:,.1f} > Y*): "
                                  "keynesiano a corto, clásico a largo — la síntesis completa")


MODELO = Modelo(
    id="m25", nivel=4,
    nombre="Ajuste hacia el largo plazo",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dG", _P0["dG"], -100, 100, 10, "Shock permanente de gasto dG"),
        Parametro("dM", _P0["dM"], -150, 150, 10, "Shock permanente de dinero dM"),
        Parametro("T", 15.0, 3, 40, 1, "Períodos de ajuste simulados"),
        Parametro("lam", _P0["lam"], 0.001, 0.012, 0.001, "Rigidez λ (velocidad del ajuste)"),
        Parametro("Pe0", _P0["Pe0"], 1.5, 2.8, 0.1, "Expectativa inicial Pe0"),
        Parametro("Ystar", _P0["Ystar"], 620, 780, 10, "Producto potencial Y*"),
        Parametro("M", _P0["M"], 450, 750, 10, "Dinero nominal M"),
        Parametro("G", _P0["G"], 120, 300, 10, "Gasto público base G"),
        Parametro("T_imp", _P0["T_imp"], 20, 250, 10, "Impuestos T"),
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de I a r (b)"),
        Parametro("k", _P0["k"], 0.25, 0.9, 0.05, "Demanda de dinero por Y (k)"),
        Parametro("h", _P0["h"], 5, 22, 1, "Demanda de dinero por r (h)"),
        Parametro("c0", _P0["c0"], 60, 180, 10, "Consumo autónomo c0"),
        Parametro("I0", _P0["I0"], 80, 260, 10, "Inversión autónoma I0"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Cómo y cuán rápido vuelve la economía al potencial tras un impulso de demanda?",
        contexto=("La síntesis neoclásica prometía que 'a largo plazo' la economía "
                  "vuelve sola al potencial — pero ¿cómo y cuán rápido? Este modelo "
                  "muestra el mecanismo: cada período con brecha positiva sorprende "
                  "los precios al alza, los contratos siguientes incorporan la "
                  "sorpresa (Pe sube), la SRAS se desplaza y el producto extra se "
                  "evapora en precios. Keynes aceptaba la lógica y respondía con su "
                  "célebre 'a largo plazo, todos muertos' (mención): si el ajuste es "
                  "lento, la política de demanda importa aunque su efecto final sea nulo."),
        autores=("Mecanismo de ajuste de la síntesis (manuales); la dinámica de "
                 "expectativas es la adaptativa de m14 (Friedman-Phelps) aplicada al "
                 "nivel de precios."),
        supuestos=[
            "Shock de demanda PERMANENTE (dG o dM se quedan); las expectativas se revisan con un período de rezago (adaptativas).",
            "Y* y λ constantes durante el ajuste (sin histéresis).",
            "Con expectativas RACIONALES el tránsito se corta: el salto a la LRAS puede ser inmediato si el shock es anticipado (m42) — este modelo es el caso 'aprendiendo del pasado'.",
        ],
        ecuaciones=[
            Ecuacion("P^e_{t+1} = P_t \\;\\Rightarrow\\; SRAS_{t+1} \\text{ más arriba}",
                     "el motor del ajuste",
                     "la sorpresa de hoy es el contrato de mañana: mientras Y>Y* los precios "
                     "efectivos superan a los esperados y la SRAS sube sin que nadie decida nada."),
            Ecuacion("Y_t \\to Y^*, \\quad P_t \\to P_{LR} = \\frac{(b/h)\\,M'}{A_c Y^* - F'}",
                     "el destino",
                     "el punto fijo de la iteración es exactamente AD∩LRAS: la fórmula cerrada de "
                     "m22, ahora alcanzada por una trayectoria verificable."),
            Ecuacion("\\Delta Y_{LP} = 0, \\quad \\Delta P_{LP} > 0", "neutralidad del impulso de demanda",
                     "el teorema del nivel 4: la demanda elige cuándo y a qué precios se produce, "
                     "pero no CUÁNTO se produce de forma permanente."),
        ],
        intuicion=("El corto y el largo plazo no son dos teorías sino dos fotogramas "
                   "de la misma película, y λ decide la velocidad de proyección: con "
                   "precios rígidos el impulso fiscal rinde años; con precios ágiles, "
                   "meses. Todo el debate de política estabilizadora — ¿intervenir o "
                   "esperar? — es una discusión sobre la velocidad de esta película "
                   "y el costo de la brecha mientras dura (m16)."),
        equilibrio=("Punto fijo globalmente estable de la iteración Pe_{t+1}=P_t "
                    "(convergencia monótona verificada): la LRAS es un atractor. La "
                    "sobre-reacción inicial de Y es exactamente lo que el ajuste "
                    "posterior devuelve."),
        limitaciones=[
            "Expectativas adaptativas: agentes racionales que ENTIENDEN el shock saltan directo al largo plazo (crítica de Lucas, m42) — la película se vuelve un corte.",
            "Sin costos de la transición: la brecha positiva parece gratis; con Phillips (m14) el tránsito deja inflación heredada.",
            "El shock de OFERTA persistente no converge así: si ds contamina Pe cada período, la espiral no se cierra sola (los 70 completos)."],
        evolucion=("Cierra el nivel 4 y el arco corto-largo plazo del currículo: la "
                   "cruz keynesiana (m05) y la dicotomía clásica (m22) resultaron ser "
                   "la MISMA economía vista a distinta velocidad de obturación. El "
                   "interior de Y* (por qué crece) es el nivel 5 (Solow, m26); la "
                   "política óptima durante el tránsito es el nivel 6 (m38-m41)."),
    ),
    escenarios=[
        Escenario("fiscal_permanente", "dG=+50 para siempre",
                  {"dG": 50.0, "dM": 0.0},
                  "t=0: Y salta a 720 (keynesiano); t→∞: Y de vuelta en 700 y P 9% "
                  "más alto (clásico) — la síntesis en una trayectoria."),
        Escenario("monetario_permanente", "dM=+60 para siempre",
                  {"dG": 0.0, "dM": 60.0},
                  "misma película con motor monetario: a largo plazo solo P sube "
                  "(~10%) — la neutralidad de m22 alcanzada dinámicamente."),
        Escenario("precios_agiles", "λ alta (0.01): el ajuste corre",
                  {"lam": 0.01},
                  "la brecha se cierra en pocos períodos: con precios flexibles el "
                  "mundo es casi clásico desde el día uno — λ es el 'largo' del corto plazo."),
        Escenario("austeridad_permanente", "dG=−50: la película en reversa",
                  {"dG": -50.0},
                  "recesión transitoria y deflación permanente: el ajuste también "
                  "funciona hacia abajo… si los precios bajan (rigidez asimétrica, m21)."),
    ],
    verificaciones=[
        Verificacion("neutralidad de largo plazo: Y_∞ = Y* exacto", _v_neutralidad_demanda),
        Verificacion("P converge al P_LR cerrado (iteración = fórmula)", _v_convergencia_p),
        Verificacion("convergencia monótona (sin oscilaciones)", _v_monotonia),
        Verificacion("a corto plazo el impulso SÍ mueve Y", _v_corto_plazo_reacciona),
    ],
    notas="La película completa: keynesiano en t=0, clásico en t=∞, y λ decide cuánto dura el tránsito.",
)
