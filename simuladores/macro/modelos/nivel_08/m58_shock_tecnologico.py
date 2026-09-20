"""simuladores/macro/modelos/nivel_08/m58_shock_tecnologico.py — el shock tecnológico: la IRF del RBC (nivel 8).

El experimento limpio del m57: UN shock de productividad a_0 y su
propagación determinista a_t = ρ^t·a_0 por el motor RBC (_rbc.py):
  n = η·a ;  y = (1+α_n·η)·a ;  c = γ·y ;  i = (y − sc·c)/si
La función impulso-respuesta (IRF) es el idioma en que los macroeconomistas
comparan modelos desde Sims (mención): m56 (NK) y m58 (RBC) responden a
sus shocks con IRFs — y el nivel 12 las estimará con datos.

Procedencia: IRF estándar del RBC didáctico (m57) — decisión de diseño
sobre conocimiento general.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_08 import _rbc
import config


def _irfs(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    a = p["a0"] * p["rho_a"] ** t
    y, n, c, i = _rbc.sendas(a, p["eta"], p["alpha_n"], p["gamma"], p["sc"], p["si"])
    return t, a, y, n, c, i


def _curvas(p):
    t, a, y, n, c, i = _irfs(p)
    return {"lineas": {"inversión $i_t$": (t, i, config.ROJO),
                       "producto $y_t$": (t, y, config.AZUL2),
                       "trabajo $n_t = \\eta a_t$": (t, n, config.DORADO),
                       "consumo $c_t$": (t, c, config.VERDE),
                       "productividad $a_t = \\rho^t$": (t, a, config.GRIS)},
            "anotacion": (f"impacto: $i={float(i[0]):.1f}$, $y={float(y[0]):.1f}$, "
                          f"$c={float(c[0]):.1f}$ (por $a_0={p['a0']:.0f}$)\n"
                          f"semivida $= \\ln 2/(-\\ln\\rho) = "
                          f"{np.log(2) / -np.log(p['rho_a']):.1f}$ períodos\n"
                          "todos decaen al MISMO ritmo: el del impulso")}


def _resultados(p):
    t, a, y, n, c, i = _irfs(p)
    return {"impacto en y (=(1+α_nη)a0)": float(y[0]),
            "impacto en i": float(i[0]),
            "impacto en c": float(c[0]),
            "impacto en n (=η·a0)": float(n[0]),
            "semivida común (períodos)": float(np.log(2) / -np.log(p["rho_a"])) if p["rho_a"] < 1 else 9999.0}


def _ecuaciones_calibradas(p):
    return [f"$a_t = {p['a0']:.0f} \\times {p['rho_a']:.2f}^{{\\,t}}$",
            f"$y_0 = {1 + p['alpha_n'] * p['eta']:.2f}, \\;\\; i_0 = "
            f"{(1 + p['alpha_n'] * p['eta']) * (1 - p['sc'] * p['gamma']) / p['si']:.2f}, \\;\\; "
            f"c_0 = {(1 + p['alpha_n'] * p['eta']) * p['gamma']:.2f}$"]


_P0 = {"a0": 1.0, "rho_a": 0.7, "eta": 1.5, "alpha_n": 0.67,
       "gamma": 0.5, "sc": 0.8, "si": 0.2, "T": 14.0}


def _v_decaimiento():
    t, a, y, n, c, i = _irfs(_P0)
    razones = y[1:6] / y[0:5]
    return bool(np.all(np.abs(razones - _P0["rho_a"]) < 1e-12)), \
        f"la IRF de y decae exactamente a ρ = {_P0['rho_a']}: memoria prestada del impulso"


def _v_jerarquia_impacto():
    t, a, y, n, c, i = _irfs(_P0)
    return float(i[0]) > float(y[0]) > float(c[0]) > 0, \
        (f"impactos ordenados: i({float(i[0]):.1f}) > y({float(y[0]):.1f}) > "
         f"c({float(c[0]):.1f}): la inversión sobrerreacciona, el consumo se suaviza")


def _v_trabajo_prociclico():
    t, a, y, n, c, i = _irfs(_P0)
    return bool(np.all(np.abs(n - _P0["eta"] * a) < 1e-12)), \
        ("n = η·a exacto en toda la IRF: el empleo procíclico sale de ELEGIR trabajar "
         "cuando rinde — sin fricciones ni despidos")


def _v_semivida():
    p = dict(_P0, rho_a=0.7)
    t, a, y, n, c, i = _irfs(p, T=60)
    teo = np.log(2) / -np.log(p["rho_a"])
    idx = int(np.argmax(y <= y[0] / 2))
    return abs(idx - np.ceil(teo)) < 1 + 1e-9, \
        f"la semivida simulada ({idx}) coincide con ln2/−lnρ ({teo:.1f}): el reloj del shock"


MODELO = Modelo(
    id="m58", nivel=8,
    nombre="Shock tecnológico (IRF del RBC)",
    xlabel="Período $t$", ylabel="Respuesta (%)",
    parametros=[
        Parametro("rho_a", _P0["rho_a"], 0.0, 1.0, 0.05, "Persistencia ρ_a", grupo="impulso",
                  definicion="ρ=1: el shock es PERMANENTE (conecta con m29)"),
        Parametro("a0", _P0["a0"], 0.5, 3, 0.25, "Tamaño del shock a0 (%)", grupo="impulso"),
        Parametro("eta", _P0["eta"], 0.2, 3, 0.1, "Elasticidad del trabajo η", grupo="propagación"),
        Parametro("gamma", _P0["gamma"], 0.2, 0.9, 0.05, "Suavización del consumo γ", grupo="propagación"),
        Parametro("alpha_n", _P0["alpha_n"], 0.5, 0.8, 0.01, "Participación del trabajo α_n", grupo="tecnología"),
        Parametro("T", _P0["T"], 8, 40, 1, "Períodos simulados", grupo="experimento"),
        Parametro("sc", _P0["sc"], 0.6, 0.85, 0.05, "Peso del consumo sc", grupo="estructura"),
        Parametro("si", _P0["si"], 0.15, 0.4, 0.05, "Peso de la inversión si", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo se lee la 'huella digital' de un modelo — y qué dice la del RBC ante su propio shock?",
        variables=[("a_t = ρ^t", "el impulso aislado — un solo golpe, sin ruido"),
                   ("y, n, c, i", "las respuestas — cada una con su tamaño, todas con el mismo reloj"),
                   ("IRF", "la función impulso-respuesta — el idioma común de los modelos modernos")],
        derivacion=["a_t = \\rho^t a_0 \\;\\;(impulso\\;determinista)",
                    "y_t = (1+\\alpha_n\\eta)\\,a_t;\\;\\; n_t = \\eta a_t;\\;\\; c_t=\\gamma y_t",
                    "i_t = \\frac{y_t - s_c c_t}{s_i} \\;\\;(la\\;más\\;nerviosa)"],
        contexto=("El m57 mostró la economía RBC bajo una lluvia de shocks; este "
                  "modelo enciende UNO solo y mira la onda expansiva. La IRF es el "
                  "formato en que la macro moderna se comunica desde los VAR de "
                  "Sims (mención): m56 respondía a un shock de costos con IRFs "
                  "(a·ρ^t, b·ρ^t); el RBC responde a la tecnología con estas. "
                  "Comparar huellas — modelo contra modelo, modelo contra datos — "
                  "es el método (y será el del nivel 12 con series peruanas)."),
        autores=("El análisis de impulso-respuesta como práctica: Sims (1980, "
                 "mención; Nobel 2011); la IRF tecnológica canónica: la literatura "
                 "RBC de los 80 (menciones)."),
        supuestos=["Los del m57 (motor compartido _rbc.py); el shock es conocido y aislado (sin ruido: es un experimento, no una muestra).",
                   "Linealidad: la IRF escala con a0 y no depende del estado (los modelos con ZLB o crisis la rompen).",
                   "ρ resume TODO el futuro del shock: con ρ=1 el shock es permanente y el 'ciclo' se vuelve crecimiento (m29)."],
        ecuaciones=[
            Ecuacion("IRF_z(t) = \\frac{\\partial z_t}{\\partial a_0} = \\phi_z\\,\\rho^t",
                     "la huella digital",
                     "en este esqueleto TODAS las respuestas son el impulso reescalado: mismos "
                     "relojes, distintos tamaños (φ_i > φ_y > 1 > φ_c)."),
        ],
        intuicion=("La IRF separa dos preguntas que m57 mezclaba: cuánto AMPLIFICA "
                   "el modelo (los impactos: i sobrerreacciona ×6, c apenas ×1) y "
                   "cuánto PROPAGA (la cola: aquí, nada propio — todo decae a ρ, "
                   "verificado). Esa segunda carencia es la puerta de m61: los "
                   "modelos serios se juzgan por si su cola dura MÁS que la del "
                   "impulso."),
        equilibrio=("La IRF es la trayectoria de equilibrio ante el impulso "
                    "unitario: única, lineal en a0, con decaimiento exacto ρ y "
                    "semivida ln2/−lnρ (ambos verificados)."),
        limitaciones=[
            "Sin propagación interna (cola = impulso): la crítica de Cogley-Nason que m61 desarrolla.",
            "IRF lineal e independiente del estado: las respuestas reales dependen de dónde está la economía (expansión vs ZLB).",
            "El impulso tecnológico es inobservable directamente: en datos se identifica con supuestos (VAR estructurales — nivel 12).",
        ],
        evolucion=("Con la huella del RBC en la mano, m59 la contrasta con la del "
                   "NK ante el shock MONETARIO (el experimento que separa a las "
                   "escuelas), m60 hace lo propio con el fiscal, y m61 pregunta por "
                   "la cola: ¿de quién es la persistencia?"),
    ),
    escenarios=[
        Escenario("shock_transitorio", "ρ = 0.5: la tecnología visita y se va",
                  {"rho_a": 0.5},
                  "semivida de 1 período: el ciclo resultante es corto — con "
                  "impulsos así, el RBC necesita MUCHA amplificación para explicar "
                  "recesiones largas.",
                  cadena=["shock corto", "respuestas grandes pero fugaces",
                          "semivida = 1", "sin propagación propia, el ciclo muere con el impulso"]),
        Escenario("shock_persistente", "ρ = 0.95: casi permanente",
                  {"rho_a": 0.95},
                  "semivida de ~13.5 períodos: así calibraban los RBC clásicos — la "
                  "persistencia del ciclo comprada en el impulso (la crítica de m61).",
                  cadena=["↑ρ", "el shock casi no decae", "el ciclo hereda la longevidad",
                          "¿modelo persistente o impulso persistente? (m61)"]),
        Escenario("mejora_permanente", "ρ = 1: el shock que no se va",
                  {"rho_a": 1.0},
                  "nada decae: la 'IRF' es un escalón — el shock permanente de "
                  "productividad ES crecimiento (m29): ciclo y tendencia se tocan.",
                  cadena=["ρ = 1", "a queda arriba para siempre", "y, c, i escalan de nivel",
                          "el 'ciclo' se volvió crecimiento (m29)"]),
    ],
    verificaciones=[
        Verificacion("decaimiento exacto a ρ (memoria prestada)", _v_decaimiento),
        Verificacion("jerarquía de impactos i>y>a>c", _v_jerarquia_impacto),
        Verificacion("empleo procíclico exacto (n=η·a)", _v_trabajo_prociclico),
        Verificacion("semivida = ln2/−lnρ", _v_semivida),
    ],
    notas="La IRF como huella digital: tamaños distintos, mismo reloj — y la cola delata al esqueleto (m61).",
)
