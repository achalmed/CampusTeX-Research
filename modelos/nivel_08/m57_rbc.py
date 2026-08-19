# m57_rbc.py — el modelo de ciclos reales (RBC) — nivel 8.
#
# El ciclo SIN dinero, SIN rigideces y SIN fallas: productividad AR(1) +
# respuestas ÓPTIMAS de hogares y firmas (motor en _rbc.py):
#   a_t = ρ·a_{t−1} + ε_t ;  n = η·a ;  y = (1+α_n·η)·a ;  c = γ·y ;
#   i = (y − sc·c)/si
# Reproduce los hechos estilizados del ciclo con tres números exactos:
# amplificación y/a, y la jerarquía σ_i > σ_y > σ_c. Provocación fundacional:
# si esto basta, el ciclo no es una falla que corregir sino la respuesta
# eficiente a la tecnología — y la política estabilizadora sobra.
#
# Procedencia: Kydland y Prescott (1982, Nobel 2004), Long y Plosser (1983)
# — menciones; esqueleto log-lineal: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_08 import _rbc
import config


def _simular(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    rng = np.random.default_rng(int(round(p["semilla"])))
    eps = rng.normal(0.0, p["sigma_a"], T + 1)
    a = np.zeros(T + 1)
    for t in range(1, T + 1):
        a[t] = p["rho_a"] * a[t - 1] + eps[t]
    y, n, c, i = _rbc.sendas(a, p["eta"], p["alpha_n"], p["gamma"], p["sc"], p["si"])
    return np.arange(T + 1), a, y, n, c, i


def _curvas(p):
    t, a, y, n, c, i = _simular(p)
    return {"lineas": {"inversión $i_t$ (la más volátil)": (t, i, config.ROJO),
                       "producto $y_t$": (t, y, config.AZUL2),
                       "consumo $c_t$ (el más suave)": (t, c, config.VERDE),
                       "productividad $a_t$ (el impulso)": (t, a, config.GRIS)},
            "anotacion": (f"amplificación $y/a = 1+\\alpha_n\\eta = "
                          f"{1 + p['alpha_n'] * p['eta']:.2f}$\n"
                          f"jerarquía exacta: $\\sigma_i/\\sigma_y = "
                          f"{(1 - p['sc'] * p['gamma']) / p['si']:.2f}$, "
                          f"$\\sigma_c/\\sigma_y = {p['gamma']:.2f}$\n"
                          "ciclo sin dinero: solo tecnología y elecciones óptimas")}


def _resultados(p):
    t, a, y, n, c, i = _simular(p, T=2000)
    return {"amplificación y/a (=1+α_n·η)": 1 + p["alpha_n"] * p["eta"],
            "σ_i/σ_y (teórica y exacta)": (1 - p["sc"] * p["gamma"]) / p["si"],
            "σ_c/σ_y (= γ)": p["gamma"],
            "sd(y) simulada (%)": float(np.std(y)),
            "autocorr(y) (heredada de a)": float(np.corrcoef(y[:-1], y[1:])[0, 1]),
            "ρ del impulso": p["rho_a"]}


def _ecuaciones_calibradas(p):
    return [f"$y = (1 + {p['alpha_n']:.2f} \\times {p['eta']:.1f})\\,a = "
            f"{1 + p['alpha_n'] * p['eta']:.2f}\\,a$",
            f"$c = {p['gamma']:.2f}\\,y, \\quad i = (y - {p['sc']:.2f}\\,c)/{p['si']:.2f} "
            f"= {(1 - p['sc'] * p['gamma']) / p['si']:.2f}\\,y$"]


_P0 = {"rho_a": 0.9, "sigma_a": 1.0, "eta": 1.5, "alpha_n": 0.67,
       "gamma": 0.5, "sc": 0.8, "si": 0.2, "T": 60.0, "semilla": 42.0}


def _v_amplificacion():
    t, a, y, n, c, i = _simular(_P0)
    razon = y[10] / a[10]
    return abs(razon - (1 + _P0["alpha_n"] * _P0["eta"])) < 1e-12, \
        (f"y/a = 1+α_n·η = {razon:.3f} exacto: el trabajo elástico AMPLIFICA el shock "
         "(sin amplificación, el RBC no reproduce la volatilidad del ciclo)")


def _v_jerarquia():
    t, a, y, n, c, i = _simular(_P0, T=2000)
    ri = float(np.std(i) / np.std(y))
    rc = float(np.std(c) / np.std(y))
    teo_i = (1 - _P0["sc"] * _P0["gamma"]) / _P0["si"]
    ok = abs(ri - teo_i) < 1e-9 and abs(rc - _P0["gamma"]) < 1e-9 and ri > 1 > rc
    return ok, (f"σ_i/σ_y = {ri:.2f} y σ_c/σ_y = {rc:.2f} EXACTOS: la inversión triplica al "
                "producto y el consumo lo suaviza — los hechos estilizados, por construcción")


def _v_identidad():
    t, a, y, n, c, i = _simular(_P0)
    res = np.max(np.abs(y - (_P0["sc"] * c + _P0["si"] * i)))
    return res < 1e-12, f"y = sc·c + si·i en toda la muestra (residuo {res:.1e}): la contabilidad manda"


def _v_persistencia_heredada():
    t, a, y, n, c, i = _simular(_P0, T=2000)
    ac_a = float(np.corrcoef(a[:-1], a[1:])[0, 1])
    ac_y = float(np.corrcoef(y[:-1], y[1:])[0, 1])
    return abs(ac_a - ac_y) < 1e-12, \
        ("autocorr(y) = autocorr(a) EXACTA: este esqueleto no añade persistencia — "
         "toda la memoria es del impulso (la crítica que m61 desarrolla)")


MODELO = Modelo(
    id="m57", nivel=8,
    nombre="Ciclos reales (RBC)",
    xlabel="Período $t$", ylabel="Desviaciones (%)",
    parametros=[
        Parametro("rho_a", _P0["rho_a"], 0.0, 0.98, 0.02, "Persistencia del impulso ρ_a", grupo="impulso"),
        Parametro("sigma_a", _P0["sigma_a"], 0.3, 3, 0.1, "Volatilidad tecnológica σ_a", grupo="impulso"),
        Parametro("eta", _P0["eta"], 0.2, 3, 0.1, "Elasticidad del trabajo η (Frisch)", grupo="propagación",
                  definicion="el amplificador — y el parámetro más disputado del RBC"),
        Parametro("alpha_n", _P0["alpha_n"], 0.5, 0.8, 0.01, "Participación del trabajo α_n", grupo="tecnología"),
        Parametro("gamma", _P0["gamma"], 0.2, 0.9, 0.05, "Suavización del consumo γ", grupo="propagación"),
        Parametro("semilla", _P0["semilla"], 1, 999, 1, "Semilla (reproducibilidad)", grupo="experimento"),
        Parametro("T", _P0["T"], 30, 120, 5, "Períodos simulados", grupo="experimento"),
        Parametro("sc", _P0["sc"], 0.6, 0.85, 0.05, "Peso del consumo sc", grupo="estructura"),
        Parametro("si", _P0["si"], 0.15, 0.4, 0.05, "Peso de la inversión si", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Puede el ciclo económico ser la respuesta EFICIENTE a la tecnología — sin dinero, rigideces ni fallas que corregir?",
        variables=[("a_t", "productividad AR(1) — el único impulso"),
                   ("n, y", "trabajo y producto — respuestas ÓPTIMAS (n=ηa amplifica)"),
                   ("c, i", "consumo suave e inversión volátil — la partición eficiente del shock")],
        derivacion=["n_t = \\eta\\,a_t \\;\\;(sustitución\\;intertemporal\\;del\\;ocio)",
                    "y_t = a_t + \\alpha_n n_t = (1+\\alpha_n\\eta)\\,a_t",
                    "c_t = \\gamma y_t;\\;\\; i_t = \\frac{y_t - s_c c_t}{s_i} \\Rightarrow \\sigma_i > \\sigma_y > \\sigma_c"],
        contexto=("En 1982, Kydland y Prescott hicieron la pregunta más incómoda "
                  "posible: ¿y si el ciclo NO es una falla? Tomaron el modelo de "
                  "crecimiento (m26-m29), le pusieron shocks de productividad (los "
                  "ε de m17, ahora con nombre) y agentes que optimizan, y "
                  "reprodujeron los hechos estilizados del ciclo — sin dinero, sin "
                  "Phillips, sin demanda agregada. La provocación reorganizó la "
                  "macro: desde entonces, TODO modelo de ciclo (incluido el NK de "
                  "m56, que es un RBC con Calvo encima) se construye y evalúa a la "
                  "manera RBC — equilibrio, microfundamentos, momentos."),
        autores=("Kydland y Prescott (1982, 'Time to Build…'; Nobel 2004); Long y "
                 "Plosser (1983) — menciones. El método de calibración y momentos "
                 "es su segunda herencia."),
        supuestos=[
            "El impulso es SOLO tecnológico (a_t): medible como residuo de Solow (m29) — con todos sus problemas.",
            "Trabajo muy elástico (η alto): la sustitución intertemporal del ocio amplifica — la evidencia micro dice η bajo (la crítica clásica).",
            "Sin dinero ni rigideces: la neutralidad es total e instantánea (m59 lo usa como banco de pruebas).",
            "Esqueleto log-lineal didáctico: consumo suavizado con γ fijo (la versión completa lo deriva de Euler, m54).",
        ],
        ecuaciones=[
            Ecuacion("y_t = (1+\\alpha_n\\,\\eta)\\,a_t", "la amplificación",
                     "el shock no viaja solo: el trabajo óptimo lo multiplica — con η=1.5 y "
                     "α_n=0.67, cada punto de productividad son 2 de producto (verificado exacto)."),
            Ecuacion("\\sigma_i > \\sigma_y > \\sigma_c", "la jerarquía de volatilidades",
                     "el hogar suaviza consumo (γ<1) y la inversión absorbe el resto de la "
                     "identidad: la firma estadística del ciclo real, exacta por construcción."),
        ],
        intuicion=("El RBC lee la recesión como se lee una mala cosecha: la "
                   "tecnología rinde menos, trabajar vale menos la pena, y la "
                   "respuesta EFICIENTE es producir, invertir y trabajar menos. Si "
                   "esa lectura es correcta, 'estabilizar' el ciclo es tan sensato "
                   "como legislar contra el invierno. El NK responde: la mala "
                   "cosecha no explica por qué el dinero mueve al producto (m59) ni "
                   "qué fue un 'shock tecnológico negativo' en 2009 — el duelo de "
                   "los niveles modernos está servido."),
        equilibrio=("Cada realización del shock produce la respuesta óptima única; "
                    "las razones de volatilidad y la amplificación son constantes "
                    "estructurales verificadas EXACTAS; la persistencia del "
                    "producto es exactamente la del impulso (herencia verificada — "
                    "el esqueleto no propaga: m61)."),
        limitaciones=[
            "η micro es bajo (~0.5): sin trabajo elástico la amplificación muere — el talón de Aquiles empírico (escenario incluido).",
            "¿Qué ES un shock tecnológico negativo? Las recesiones de demanda (2009) no caben sin forzar el residuo (m59-m60).",
            "Sin propagación interna: autocorr(y)=autocorr(a) exacta — el modelo hereda el ciclo, no lo fabrica (m61).",
            "El dinero es un velo total: la evidencia VAR dice lo contrario (m59).",
        ],
        evolucion=("El RBC es la mitad del ADN de la macro moderna: m58 aísla su "
                   "IRF, m59 lo enfrenta al NK en el experimento monetario, m60 "
                   "compara sus multiplicadores fiscales y m61 expone su problema "
                   "de propagación — el camino que llevó a los DSGE medianos "
                   "(Smets-Wouters, mención) que hoy usan los bancos centrales."),
    ),
    escenarios=[
        Escenario("ciclo_tecnologico", "la economía RBC con ρ_a=0.9 y σ_a=1",
                  {"rho_a": 0.9},
                  "recesiones y booms sin un solo precio rígido: la inversión "
                  "triplica la volatilidad del producto y el consumo la parte en "
                  "dos — los hechos estilizados desde la eficiencia.",
                  cadena=["shock a_t", "el ocio se sustituye intertemporalmente (n=ηa)",
                          "y amplificado ×2", "c suavizado (γ)", "i absorbe el resto",
                          "σ_i > σ_y > σ_c"]),
        Escenario("trabajo_rigido", "la crítica micro: η = 0.5",
                  {"eta": 0.5},
                  "la amplificación cae de 2.0 a 1.34: con la elasticidad que miden "
                  "los microeconomistas, el RBC pierde la mitad de su ciclo — el "
                  "debate de calibración en una perilla.",
                  cadena=["η bajo (evidencia micro)", "el trabajo casi no responde",
                          "amplificación 1+α_nη se desinfla", "el ciclo simulado queda corto",
                          "¿shocks más grandes o mecanismos que faltan? (m61)"]),
        Escenario("impulso_persistente", "ρ_a = 0.95: tecnología que se queda",
                  {"rho_a": 0.95},
                  "ciclos largos y amplios — pero TODA la persistencia sigue siendo "
                  "prestada del impulso: el esqueleto no añade memoria propia.",
                  cadena=["↑ρ_a", "los shocks duran", "autocorr(y) sube = autocorr(a)",
                          "ciclo más persistente… por herencia, no por propagación"]),
    ],
    verificaciones=[
        Verificacion("amplificación y/a = 1+α_n·η exacta", _v_amplificacion),
        Verificacion("jerarquía σ_i>σ_y>σ_c con razones exactas", _v_jerarquia),
        Verificacion("identidad y = sc·c + si·i en toda la muestra", _v_identidad),
        Verificacion("persistencia heredada: autocorr(y)=autocorr(a)", _v_persistencia_heredada),
    ],
    notas="La provocación fundacional: el ciclo como respuesta eficiente. El NK (m56) es este modelo + Calvo.",
)
