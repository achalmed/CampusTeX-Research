# m17_ciclo_economico.py — ciclo económico como impulso-propagación (nivel 3).
#
# La brecha sigue un AR(1) con shocks aleatorios:
#   brecha_t = ρ·brecha_{t−1} + ε_t ,   ε_t ~ N(0, σ²)
# Propiedades teóricas verificables: sd(brecha) = σ/√(1−ρ²), autocorr(1) = ρ.
# La semilla es un PARÁMETRO: misma semilla → misma historia (reproducible).
#
# Procedencia: visión impulso-propagación de Slutsky (1927) y Frisch (1933) —
# menciones históricas de conocimiento general; AR(1) y sus momentos:
# resultados estándar de series de tiempo.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _simular(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    rng = np.random.default_rng(int(round(p["semilla"])))
    eps = rng.normal(0.0, p["sigma"], T + 1)
    brecha = np.zeros(T + 1)
    for t in range(1, T + 1):
        brecha[t] = p["rho"] * brecha[t - 1] + eps[t]
    t = np.arange(T + 1)
    Ypot = p["Y0"] * (1 + p["g_pot"] / 100) ** t
    return t, Ypot, Ypot * (1 + brecha / 100), brecha


def _curvas(p):
    t, Ypot, Y, brecha = _simular(p)
    sd_teo = p["sigma"] / np.sqrt(1 - p["rho"] ** 2)
    recesiones = int(np.sum((brecha[1:] < 0) & (brecha[:-1] >= 0)))
    return {"lineas": {"PIB potencial $Y^*$": (t, Ypot, config.GRIS),
                       "PIB observado $Y$ (shocks AR(1))": (t, Y, config.AZUL2)},
            "anotacion": (f"$\\rho = {p['rho']:.2f}$,  $\\sigma = {p['sigma']:.2f}$,  "
                          f"semilla $= {int(p['semilla'])}$\n"
                          f"sd teórica $= \\sigma/\\sqrt{{1-\\rho^2}} = {sd_teo:.2f}\\%$\n"
                          f"episodios recesivos en la muestra: {recesiones}")}


def _resultados(p):
    _, _, _, brecha = _simular(p)
    sd_teo = p["sigma"] / np.sqrt(1 - p["rho"] ** 2)
    en_recesion = brecha < 0
    rachas, actual = [], 0
    for r in en_recesion:
        actual = actual + 1 if r else 0
        if actual:
            rachas.append(actual)
    return {"sd teórica de la brecha (%)": sd_teo,
            "sd simulada (%)": float(np.std(brecha)),
            "autocorrelación(1) simulada": float(np.corrcoef(brecha[:-1], brecha[1:])[0, 1]),
            "% de períodos en brecha negativa": 100 * float(np.mean(en_recesion)),
            "racha recesiva más larga": float(max(rachas) if rachas else 0)}


_P0 = {"rho": 0.7, "sigma": 1.5, "T": 40.0, "semilla": 42.0, "g_pot": 3.0, "Y0": 100.0}


def _v_reproducible():
    _, _, Y1, _ = _simular(_P0)
    _, _, Y2, _ = _simular(_P0)
    return bool(np.all(Y1 == Y2)), "misma semilla → la misma historia, siempre (reproducibilidad)"


def _v_momentos():
    _, _, _, brecha = _simular(_P0, T=20000)
    sd_teo = _P0["sigma"] / np.sqrt(1 - _P0["rho"] ** 2)
    sd_sim = float(np.std(brecha))
    ac1 = float(np.corrcoef(brecha[:-1], brecha[1:])[0, 1])
    ok = abs(sd_sim - sd_teo) / sd_teo < 0.03 and abs(ac1 - _P0["rho"]) < 0.02
    return ok, (f"con T=20000: sd simulada {sd_sim:.2f} ≈ teórica {sd_teo:.2f}; "
                f"autocorr {ac1:.3f} ≈ ρ={_P0['rho']}")


def _v_estacionario():
    _, _, _, brecha = _simular(_P0, T=20000)
    sd_teo = _P0["sigma"] / np.sqrt(1 - _P0["rho"] ** 2)
    return bool(np.max(np.abs(brecha)) < 8 * sd_teo), ("|ρ|<1 → proceso estacionario: la brecha "
                                                       "nunca se escapa (acotada en ±8 sd)")


MODELO = Modelo(
    id="m17", nivel=3,
    nombre="Ciclo económico (impulso-propagación)",
    xlabel="Período $t$", ylabel="PIB (índice, $Y_0=100$)",
    parametros=[
        Parametro("rho", _P0["rho"], 0.0, 0.95, 0.05, "Persistencia ρ (propagación)"),
        Parametro("sigma", _P0["sigma"], 0.3, 4.0, 0.1, "Volatilidad de shocks σ (impulso)"),
        Parametro("semilla", _P0["semilla"], 1, 999, 1, "Semilla (reproducibilidad)"),
        Parametro("T", _P0["T"], 20, 120, 5, "Períodos simulados"),
        Parametro("g_pot", _P0["g_pot"], 0.0, 6.0, 0.25, "Crecimiento potencial (%)"),
        Parametro("Y0", _P0["Y0"], 50, 200, 10, "PIB inicial (índice)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Pueden shocks aleatorios sin ningún ciclo dentro generar los ciclos que vemos?",
        contexto=("¿Por qué hay ciclos? Las teorías del siglo XIX buscaban causas "
                  "cíclicas (cosechas, crédito, manchas solares). Slutsky (1927) mostró "
                  "algo desconcertante: SUMAR shocks aleatorios sin ningún ciclo dentro "
                  "produce series que parecen ciclos. Frisch (1933) lo convirtió en el "
                  "paradigma impulso-propagación: impulsos aleatorios + una estructura "
                  "que los propaga con inercia = fluctuaciones recurrentes sin reloj "
                  "interno. Toda la macro moderna del ciclo (RBC, nuevo keynesiana) "
                  "vive dentro de ese paradigma."),
        autores=("Slutsky (1927, suma de causas aleatorias); Frisch (1933, "
                 "impulso-propagación); la medición clásica de ciclos es Burns-Mitchell "
                 "(NBER); Lucas definió el ciclo moderno como desviaciones "
                 "autocorrelacionadas respecto de la tendencia."),
        supuestos=[
            "Los shocks ε son exógenos, imprevisibles y sin estructura (ruido blanco): TODO el patrón visible viene de la propagación ρ.",
            "Propagación lineal y constante (un solo ρ resume mercados, políticas y expectativas).",
            "La tendencia Y* es independiente del ciclo (sin histéresis, igual que m16).",
        ],
        ecuaciones=[
            Ecuacion("\\text{brecha}_t = \\rho\\,\\text{brecha}_{t-1} + \\varepsilon_t", "AR(1)",
                     "ρ es la memoria de la economía: contratos, inventarios, hábitos. Con ρ=0 no "
                     "habría ciclos, solo ruido; con ρ→1 los shocks serían casi permanentes."),
            Ecuacion("sd(\\text{brecha}) = \\frac{\\sigma}{\\sqrt{1-\\rho^2}}", "volatilidad del ciclo",
                     "la varianza observada AMPLIFICA la de los shocks: con ρ=0.7 el ciclo es 40% "
                     "más volátil que sus impulsos — la propagación fabrica ciclo."),
            Ecuacion("corr(\\text{brecha}_t, \\text{brecha}_{t-1}) = \\rho", "persistencia",
                     "la firma estadística del ciclo: momentos verificables contra la simulación."),
        ],
        intuicion=("El ciclo no necesita causa cíclica: basta mala suerte con memoria. "
                   "Dos perillas separan mundos: σ (cuán fuerte golpea la suerte) y ρ "
                   "(cuánto dura el golpe). La política estabilizadora, vista así, es "
                   "una disputa por ρ — amortiguar la propagación — más que por los "
                   "impulsos, que nadie controla."),
        equilibrio=("Con |ρ|<1 el proceso es ESTACIONARIO: la brecha fluctúa acotada "
                    "alrededor de 0 con varianza constante. No hay equilibrio puntual "
                    "sino una distribución de equilibrio — el primer encuentro del "
                    "currículo con esa idea."),
        limitaciones=[
            "ρ y σ son cajas negras: no dicen QUÉ propaga (inventarios, crédito, rigideces) ni QUÉ golpea (tecnología, política, exterior) — eso lo disputan RBC (m57) y los nuevos keynesianos.",
            "Shocks normales e independientes: las crisis reales traen colas gordas y volatilidad agrupada (nivel 10).",
            "Simetría: sube y baja igual; los datos sugieren recesiones más abruptas que las expansiones.",
        ],
        evolucion=("Es el esqueleto estadístico sobre el que el nivel 8 pondrá economía: "
                   "los RBC (m57) microfundamentan ρ con decisiones intertemporales y "
                   "leen ε como shocks de productividad; m18-m19 tipifican los impulsos "
                   "(demanda vs oferta); y m98 confrontará este AR(1) con la brecha "
                   "peruana estimada de las series del BCRP."),
        procedencia=("visión impulso-propagación (Slutsky 1927, Frisch 1933 — menciones); "
                     "momentos del AR(1): resultados estándar de series de tiempo (conocimiento general)"),
    ),
    escenarios=[
        Escenario("shocks_persistentes", "economía con mucha inercia (ρ = 0.9)",
                  {"rho": 0.9},
                  "la misma mala suerte dura años: la sd del ciclo se duplica sin tocar "
                  "σ — la propagación, no el impulso, hace la diferencia."),
        Escenario("shocks_violentos", "impulsos grandes (σ = 3)",
                  {"sigma": 3.0},
                  "economía expuesta (materias primas, clima): ciclo violento aun con "
                  "propagación normal — el caso de economías pequeñas y abiertas."),
        Escenario("economia_estable", "poca inercia y shocks suaves (ρ=0.4, σ=0.8)",
                  {"rho": 0.4, "sigma": 0.8},
                  "la 'Gran Moderación': ciclos apenas visibles — hasta que la "
                  "estructura cambia (nivel 10)."),
        Escenario("otra_historia", "la misma economía con otra suerte (semilla 7)",
                  {"semilla": 7.0},
                  "idénticos parámetros, historia distinta: separar estructura de azar "
                  "es LA lección metodológica de este modelo."),
    ],
    verificaciones=[
        Verificacion("reproducibilidad exacta por semilla", _v_reproducible),
        Verificacion("momentos simulados = teóricos (T grande)", _v_momentos),
        Verificacion("estacionariedad: la brecha no se escapa", _v_estacionario),
    ],
    notas="Primer modelo ESTOCÁSTICO del laboratorio: el equilibrio es una distribución, no un punto.",
)
