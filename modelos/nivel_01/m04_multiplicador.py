# m04_multiplicador.py — multiplicador keynesiano por rondas de gasto (nivel 1).
#
# Un impulso ΔG se re-gasta ronda tras ronda con PMC efectiva ĉ = c(1−t):
#   ronda n aporta  ΔG·ĉⁿ  →  acumulado  ΔY_N = ΔG·(1−ĉ^{N+1})/(1−ĉ)
#   límite N→∞:     ΔY = k·ΔG   con   k = 1/(1−ĉ) = 1/(1−c(1−t))
#
# Procedencia: Kahn (1931, multiplicador de empleo) y Keynes (1936) —
# conocimiento macroeconómico general; suma geométrica: matemática elemental.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _serie(p):
    dG, chat = p["dG"], p["c"] * (1 - p["t"])
    n = np.arange(int(round(p["rondas"])) + 1)
    aporte = dG * chat ** n
    return n, aporte, np.cumsum(aporte), 1 / (1 - chat)


def _curvas(p):
    n, aporte, acum, k = _serie(p)
    tope = np.full_like(n, k * p["dG"], dtype=float)
    return {"lineas": {"$\\Delta Y$ acumulado": (n, acum, config.AZUL2),
                       "gasto de la ronda $n$": (n, aporte, config.ROJO),
                       "límite $k\\,\\Delta G$": (n, tope, config.GRIS)},
            "equilibrio": (float(n[-1]), float(acum[-1])),
            "anotacion": (f"$k = 1/(1-c(1-t)) = {k:.2f}$\n"
                          f"$\\Delta Y$ total teórico = {k * p['dG']:,.1f}\n"
                          f"alcanzado tras {int(n[-1])} rondas: {acum[-1]:,.1f}")}


def _resultados(p):
    n, _, acum, k = _serie(p)
    total = k * p["dG"]
    return {"multiplicador k": k,
            "PMC efectiva c(1−t)": p["c"] * (1 - p["t"]),
            "ΔY total (teórico)": total,
            f"ΔY tras {int(n[-1])} rondas": float(acum[-1]),
            "% del efecto ya materializado": 100 * float(acum[-1]) / total}


def _ecuaciones_calibradas(p):
    chat = p["c"] * (1 - p["t"])
    k = 1 / (1 - chat)
    return [f"$\\hat{{c}} = {p['c']:.2f}\\,(1-{p['t']:.2f}) = {chat:.2f}$",
            f"$k = 1/(1-{chat:.2f}) = {k:.2f}$",
            f"$\\Delta Y = {k:.2f} \\times {p['dG']:.0f} = {k * p['dG']:,.1f}$"]


_P0 = {"dG": 100.0, "c": 0.8, "t": 0.0, "rondas": 20.0}


def _v_suma():
    _, _, acum, k = _serie(_P0)
    chat = _P0["c"]
    cerrada = _P0["dG"] * (1 - chat ** (len(acum))) / (1 - chat)
    return abs(acum[-1] - cerrada) < 1e-9, ("suma ronda a ronda = fórmula cerrada de la "
                                            f"serie geométrica ({acum[-1]:,.2f})")


def _v_monotonia():
    _, _, acum, k = _serie(_P0)
    tope = k * _P0["dG"]
    ok = bool(np.all(np.diff(acum) > 0)) and bool(np.all(acum <= tope + 1e-9))
    return ok, "el acumulado crece en cada ronda y nunca supera k·ΔG"


def _v_convergencia():
    _, _, acum, k = _serie(dict(_P0, rondas=200))
    tope = k * _P0["dG"]
    return abs(acum[-1] - tope) / tope < 1e-9, f"con 200 rondas el acumulado alcanza k·ΔG = {tope:,.1f}"


def _v_impuestos():
    k0 = _serie(_P0)[3]
    k1 = _serie(dict(_P0, t=0.2))[3]
    return k1 < k0, f"los impuestos amortiguan: k pasa de {k0:.2f} a {k1:.2f} (filtración fiscal)"


MODELO = Modelo(
    id="m04", nivel=1,
    nombre="Multiplicador keynesiano",
    xlabel="Ronda de gasto ($n$)", ylabel="Variación del producto ($\\Delta Y$)",
    parametros=[
        Parametro("dG", _P0["dG"], 10, 300, 10, "Impulso inicial de gasto ΔG"),
        Parametro("c", _P0["c"], 0.1, 0.95, 0.05, "Propensión marginal a consumir c"),
        Parametro("t", _P0["t"], 0.0, 0.5, 0.05, "Tasa impositiva t (filtración fiscal)"),
        Parametro("rondas", _P0["rondas"], 5, 60, 1, "Rondas de gasto simuladas"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta=("¿Cuánto producto total genera un sol adicional de gasto — y por qué "
                  "más que un sol?"),
        variables=[("ΔY", "variación acumulada del producto — endógena"),
                   ("ΔG", "impulso inicial de gasto — exógeno"),
                   ("n", "ronda de gasto (tiempo lógico del proceso)"),
                   ("ĉ = c(1−t)", "fracción re-gastada efectiva — parámetro compuesto")],
        derivacion=["\\Delta Y = \\Delta G\\,(1 + \\hat{c} + \\hat{c}^2 + \\dots)",
                    "\\sum_{n=0}^{\\infty} \\hat{c}^{\\,n} = \\frac{1}{1-\\hat{c}} \\;\\;(0 \\le \\hat{c} < 1)",
                    "k = \\frac{1}{1 - c\\,(1-t)}"],
        contexto=("En el debate británico sobre las obras públicas contra el desempleo, "
                  "Richard Kahn (1931) formalizó cuánto empleo total generaba un empleo "
                  "público adicional; Keynes (1936) convirtió esa aritmética en la pieza "
                  "central de su teoría: el gasto autónomo genera ingreso, que genera "
                  "consumo, que genera más ingreso — una serie geométrica con suma finita."),
        autores=("Kahn (1931); Keynes (1936). Extensión dinámica clásica: interacción "
                 "multiplicador-acelerador de Samuelson (1939)."),
        supuestos=[
            "Hay capacidad ociosa y precios fijos: la demanda adicional se convierte en producto, no en inflación.",
            "La PMC (c) es constante durante todas las rondas.",
            "Sin respuesta de la tasa de interés ni del tipo de cambio (llegan en m10 y m49).",
            "El impulso ΔG no altera las decisiones privadas de gasto (sin expectativas: contrasta con m67).",
        ],
        ecuaciones=[
            Ecuacion("\\Delta Y_n = \\Delta G \\cdot \\hat{c}^{\\,n}, \\quad \\hat{c} = c(1-t)",
                     "aporte de la ronda n",
                     "el gasto inicial se vuelve ingreso; de cada unidad, el hogar re-gasta c y "
                     "el fisco retiene t: a la ronda siguiente vuelve solo ĉ = c(1−t)."),
            Ecuacion("\\Delta Y_N = \\Delta G\\,\\frac{1-\\hat{c}^{\\,N+1}}{1-\\hat{c}}",
                     "acumulado tras N rondas",
                     "suma parcial de la serie geométrica: útil para ver la VELOCIDAD del efecto, "
                     "no solo su total."),
            Ecuacion("k = \\frac{1}{1-c(1-t)}", "multiplicador",
                     "límite de la suma: mientras mayor la fracción re-gastada, mayor el efecto "
                     "total de un mismo impulso."),
        ],
        intuicion=("El multiplicador es un espejo de las filtraciones (m01): el efecto de "
                   "un impulso muere cuando todo el ingreso adicional se fuga hacia "
                   "ahorro e impuestos. Con c=0.8 y sin impuestos, k=5; basta t=0.2 para "
                   "bajarlo a 2.8. La simulación por rondas enseña además que el efecto "
                   "no es instantáneo: tras 20 rondas se ha materializado ~99% del total."),
        equilibrio=("La serie converge sii 0 ≤ ĉ < 1 (garantizado por la 'ley psicológica'). "
                    "La convergencia geométrica ES la estabilidad del proceso de gasto."),
        limitaciones=[
            "Con pleno empleo el multiplicador se vuelve inflación, no producto (m18-m20).",
            "Ignora el financiamiento del impulso: si ΔG sube la tasa de interés, expulsa inversión privada (m10, m11).",
            "Sin expectativas: hogares previsores que anticipan impuestos futuros ahorran el impulso (equivalencia ricardiana, m67).",
            "Los multiplicadores fiscales estimados empíricamente suelen ser MENORES que el k simple, y dependen del régimen (m70).",
        ],
        evolucion=("El multiplicador es la mecánica del nivel 1; m05 lo usa en reversa "
                   "(paradoja del ahorro) y m06-m10 lo disciplinan con el mercado de "
                   "dinero: en IS-LM el k efectivo es menor porque la tasa de interés "
                   "sube con el ingreso. La batalla empírica moderna es m70."),
        referencias=["Kahn (1931), The Relation of Home Investment to Unemployment — mención",
                     "Keynes (1936), Teoría General — mención, no verificado contra edición"],
    ),
    escenarios=[
        Escenario("pmc_alta", "hogares que re-gastan casi todo (c = 0.9)",
                  {"c": 0.9},
                  "k salta de 5 a 10: economías con poco ahorro amplifican los shocks "
                  "de demanda — en ambas direcciones.",
                  cadena=["↑c", "más re-gasto en cada ronda", "la serie decae más lento",
                          "↑k = 1/(1−c)", "ΔY total mayor"]),
        Escenario("pmc_baja", "hogares más ahorradores (c = 0.6)",
                  {"c": 0.6},
                  "k cae a 2.5: el mismo impulso fiscal rinde la mitad.",
                  cadena=["↓c", "↑ filtración por ahorro en cada ronda", "la serie muere antes", "↓k"]),
        Escenario("con_impuestos", "se introduce una tasa impositiva t = 0.2",
                  {"t": 0.2},
                  "el fisco es un estabilizador automático: filtra ingreso en cada ronda "
                  "y amortigua el ciclo (k: 5 → 2.8).",
                  cadena=["t > 0", "el fisco filtra ingreso en cada ronda", "ĉ = c(1−t) menor",
                          "↓k", "estabilizador automático"]),
    ],
    verificaciones=[
        Verificacion("suma por rondas = fórmula cerrada", _v_suma),
        Verificacion("acumulado creciente y acotado por k·ΔG", _v_monotonia),
        Verificacion("convergencia al límite teórico", _v_convergencia),
        Verificacion("impuestos reducen el multiplicador", _v_impuestos),
    ],
    notas="Comparar con m02 (identidad: ΔY=ΔG uno a uno) y con m10 (k moderado por la tasa de interés).",
)
