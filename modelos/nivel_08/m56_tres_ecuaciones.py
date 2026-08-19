# m56_tres_ecuaciones.py — el modelo nuevo keynesiano de 3 ecuaciones (nivel 8,
# ANCLA MAYOR: aquí converge todo el currículo).
#
#   IS (m54):     x_t = x_{t+1} − σ·(i_t − π_{t+1} − r_n)
#   NKPC (m55):   π_t = β·π_{t+1} + κ·x_t + u_t         (u: shock de costos)
#   Taylor (m38): i_t = r_n + φ_π·π_t + φ_x·x_t         (en desviaciones)
#
# Con el shock AR(1)  u_t = ρ^t·u_0, el sistema racional se resuelve por
# COEFICIENTES INDETERMINADOS: conjeturar π_t = a·u_t, x_t = b·u_t y despejar:
#   b = σ(ρ − φ_π)·a / (1 − ρ + σφ_x)
#   a = 1 / [ (1−βρ) + κσ(φ_π − ρ)/(1 − ρ + σφ_x) ]
# Con φ_π > 1 (principio de Taylor, m38): a acotado y b < 0 — ante un shock
# de costos el banco central INDUCE recesión para domar la inflación. La
# solución se verifica sustituyéndola en las 3 ecuaciones, período a período.
#
# Procedencia: Clarida-Galí-Gertler (1999, "The Science of Monetary Policy"),
# Woodford (2003), Galí (2008) — menciones; método de coeficientes
# indeterminados: estándar (conocimiento general). Calibración didáctica usual.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _coeficientes(p):
    denom_b = 1 - p["rho"] + p["sigma"] * p["phi_x"]
    a = 1 / ((1 - p["beta"] * p["rho"])
             + p["kappa"] * p["sigma"] * (p["phi_pi"] - p["rho"]) / denom_b)
    b = p["sigma"] * (p["rho"] - p["phi_pi"]) * a / denom_b
    return a, b


def _irfs(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    u = p["u0"] * p["rho"] ** t
    a, b = _coeficientes(p)
    pi = a * u
    x = b * u
    i_dev = p["phi_pi"] * pi + p["phi_x"] * x        # desviación de la neutral
    return t, u, pi, x, i_dev


def _curvas(p):
    t, u, pi, x, i_dev = _irfs(p)
    return {"lineas": {"inflación $\\pi_t = a\\,u_t$": (t, pi, config.ROJO),
                       "brecha $x_t = b\\,u_t$": (t, x, config.AZUL2),
                       "tasa $i_t$ (desviación)": (t, i_dev, config.VERDE),
                       "shock de costos $u_t$": (t, u, config.GRIS)},
            "anotacion": (f"$a = {_coeficientes(p)[0]:.3f}$,  $b = {_coeficientes(p)[1]:.3f}$\n"
                          f"$\\phi_\\pi = {p['phi_pi']:.2f}$ "
                          f"({'cumple' if p['phi_pi'] > 1 else 'VIOLA'} el principio de Taylor)\n"
                          "solución racional exacta: conjeturar y verificar")}


def _resultados(p):
    a, b = _coeficientes(p)
    return {"π de impacto (a·u0)": a * p["u0"],
            "brecha de impacto (b·u0)": b * p["u0"],
            "tasa de impacto (desviación)": (p["phi_pi"] * a + p["phi_x"] * b) * p["u0"],
            "coeficiente a (π por unidad de u)": a,
            "coeficiente b (x por unidad de u)": b,
            "persistencia heredada ρ": p["rho"]}


def _ecuaciones_calibradas(p):
    a, b = _coeficientes(p)
    return [f"$x_t = x_{{t+1}} - {p['sigma']:.1f}(i_t - \\pi_{{t+1}} - r_n)$",
            f"$\\pi_t = {p['beta']:.2f}\\,\\pi_{{t+1}} + {p['kappa']:.2f}\\,x_t + u_t$",
            f"$i_t = r_n + {p['phi_pi']:.2f}\\,\\pi_t + {p['phi_x']:.2f}\\,x_t$",
            f"$\\Rightarrow\\; \\pi_t = {a:.3f}\\,u_t, \\quad x_t = {b:.3f}\\,u_t$"]


_P0 = {"beta": 0.97, "kappa": 0.2, "sigma": 1.0, "phi_pi": 1.5, "phi_x": 0.5,
       "rho": 0.7, "u0": 1.0, "T": 12.0}


def _v_solucion_exacta():
    t, u, pi, x, i_dev = _irfs(_P0, T=30)
    res_is = x[:-1] - (x[1:] - _P0["sigma"] * (i_dev[:-1] - pi[1:]))
    res_pc = pi[:-1] - (_P0["beta"] * pi[1:] + _P0["kappa"] * x[:-1] + u[:-1])
    ok = bool(np.max(np.abs(res_is)) < 1e-9) and bool(np.max(np.abs(res_pc)) < 1e-9)
    return ok, ("la conjetura (a·u, b·u) satisface la IS y la NKPC en TODOS los períodos "
                f"(residuo máx {max(np.max(np.abs(res_is)), np.max(np.abs(res_pc))):.1e}): "
                "un DSGE mínimo resuelto a mano")


def _v_principio_taylor():
    a, b = _coeficientes(_P0)
    return a > 0 and b < 0, (f"con φ_π=1.5>1: a={a:.2f} acotado y b={b:.2f}<0 — el banco "
                             "central INDUCE recesión para domar el shock de costos (lean against)")


def _v_decae_a_rho():
    t, u, pi, x, _ = _irfs(_P0)
    razones = pi[1:6] / pi[0:5]
    return bool(np.all(np.abs(razones - _P0["rho"]) < 1e-12)), \
        f"las IRFs heredan exactamente la persistencia del shock (razón = ρ = {_P0['rho']})"


def _v_halcon():
    a0, b0 = _coeficientes(_P0)
    a1, b1 = _coeficientes(dict(_P0, phi_pi=3.0))
    return a1 < a0 and abs(b1) > abs(b0), \
        (f"el halcón (φ_π=3) compra menos inflación (a: {a0:.2f}→{a1:.2f}) con más recesión "
         f"(b: {b0:.2f}→{b1:.2f}): la frontera de sacrificio hecha coeficientes")


def _v_complaciente_acomoda():
    a1, b1 = _coeficientes(dict(_P0, phi_pi=0.5))
    return b1 > 0 and a1 > _coeficientes(_P0)[0], \
        (f"violando el principio (φ_π=0.5<ρ): b={b1:.2f}>0 — el BC deja caer la tasa real y "
         f"CONVALIDA el shock con brecha positiva y más inflación (a={a1:.2f}): Burns otra vez")


MODELO = Modelo(
    id="m56", nivel=8,
    nombre="El modelo de 3 ecuaciones (IS + NKPC + Taylor)",
    xlabel="Período $t$", ylabel="Desviaciones (pp)",
    parametros=[
        Parametro("phi_pi", _P0["phi_pi"], 0.3, 3.5, 0.1, "Respuesta a inflación φ_π", grupo="regla",
                  definicion="el principio de Taylor exige >1 (m38)"),
        Parametro("phi_x", _P0["phi_x"], 0.0, 1.5, 0.05, "Respuesta a la brecha φ_x", grupo="regla"),
        Parametro("rho", _P0["rho"], 0.0, 0.95, 0.05, "Persistencia del shock ρ", grupo="shock"),
        Parametro("u0", _P0["u0"], 0.25, 3, 0.25, "Tamaño del shock de costos u0", grupo="shock"),
        Parametro("kappa", _P0["kappa"], 0.05, 0.6, 0.05, "Pendiente NKPC κ (m55)", grupo="estructura"),
        Parametro("sigma", _P0["sigma"], 0.5, 2, 0.1, "Sensibilidad de la IS σ (m54)", grupo="estructura"),
        Parametro("beta", _P0["beta"], 0.90, 0.99, 0.01, "Descuento β", grupo="estructura"),
        Parametro("T", _P0["T"], 8, 30, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cómo responde una economía racional CON regla a un shock de costos — y qué compra exactamente la dureza del banco central?",
        variables=[("π_t, x_t", "inflación y brecha — endógenas racionales (a·u, b·u)"),
                   ("i_t", "la tasa — dictada por la regla, período a período"),
                   ("u_t", "el shock de costos AR(1) — el villano de m19/m24, ahora con solución exacta"),
                   ("a, b", "los coeficientes de la solución — TODA la política está en ellos")],
        derivacion=["conjetura: \\;\\pi_t = a\\,u_t, \\;\\; x_t = b\\,u_t, \\;\\; u_{t+1} = \\rho u_t",
                    "NKPC: \\;a = \\beta\\rho a + \\kappa b + 1",
                    "IS+Taylor: \\;b(1-\\rho+\\sigma\\phi_x) = \\sigma(\\rho-\\phi_\\pi)\\,a",
                    "\\Rightarrow\\; a = \\frac{1}{(1-\\beta\\rho) + \\frac{\\kappa\\sigma(\\phi_\\pi-\\rho)}{1-\\rho+\\sigma\\phi_x}}"],
        contexto=("Este es el lenguaje en que piensan los bancos centrales del "
                  "siglo XXI: tres ecuaciones donde converge TODO el currículo — la "
                  "demanda racional de m54, la oferta de Calvo de m55 y la regla de "
                  "m38, con el fundamento institucional de m41 y las expectativas "
                  "de m42. Clarida, Galí y Gertler (1999) lo bautizaron 'la ciencia "
                  "de la política monetaria'. Y es, en rigor, un DSGE mínimo: aquí "
                  "se RESUELVE analíticamente (conjeturar y verificar), sin cajas "
                  "negras — cada coeficiente se puede auditar."),
        autores=("Clarida, Galí y Gertler (1999); Woodford (2003, Interest and "
                 "Prices); Galí (2008, libro canónico) — menciones."),
        supuestos=[
            "Expectativas RACIONALES con el shock AR(1) como única incertidumbre: E[u_{t+1}] = ρu_t.",
            "El principio de Taylor (φ_π>1) garantiza solución única y estable — violarlo abre la puerta a la indeterminación (aquí se muestra el cambio de signo de b).",
            "Sin ZLB, sin economía abierta, sin capital: el esqueleto puro (los niveles 9-11 visten el resto).",
        ],
        ecuaciones=[
            Ecuacion("x_t = x_{t+1} - \\sigma(i_t - \\pi_{t+1} - r_n)", "IS dinámica (m54)",
                     "la demanda descuenta la senda entera de tasas reales."),
            Ecuacion("\\pi_t = \\beta\\,\\pi_{t+1} + \\kappa\\,x_t + u_t", "NKPC (m55)",
                     "la inflación descuenta la senda entera de brechas — más el shock de costos."),
            Ecuacion("i_t = r_n + \\phi_\\pi\\pi_t + \\phi_x x_t", "regla de Taylor (m38)",
                     "el cierre: la política como función de reacción — el sistema queda de 3×3 y "
                     "la solución AR(1) lo diagonaliza."),
        ],
        intuicion=("Ante un shock de costos, el sistema negocia un triángulo: cuánta "
                   "inflación tolerar (a), cuánta recesión inducir (b) y cuánta tasa "
                   "mover (φ·). La regla ELIGE el punto: el halcón compra menos a "
                   "con más |b|; el complaciente que viola el principio (φ_π<ρ) "
                   "termina con MÁS inflación Y brecha positiva — Burns (m24) "
                   "derivado desde microfundamentos. La lección profunda: en un "
                   "mundo racional, la 'personalidad' del banco central (φ_π, φ_x) "
                   "no mueve una tasa — mueve TODOS los coeficientes de la economía "
                   "(la crítica de Lucas, m42, hecha aritmética)."),
        equilibrio=("Solución única con φ_π>1: (π, x, i) = (a, b, φπa+φxb)·u_t, "
                    "verificada ecuación por ecuación y período a período con "
                    "residuo < 1e-9. Las IRFs heredan exactamente la persistencia ρ "
                    "del shock — este esqueleto aún no propaga (m61 explica por qué "
                    "eso importa)."),
        limitaciones=[
            "Sin inercia: como la NKPC pura (m55), el modelo olvida el shock a velocidad ρ exacta — la persistencia inflacionaria real exige híbridos (mención).",
            "El ZLB rompe la linealidad: con shocks grandes la regla pide tasas imposibles (m12) y la solución cambia de régimen.",
            "Divina coincidencia implícita: con shocks SOLO de demanda, la regla estabiliza π y x a la vez; los de costos (u) fuerzan el trade-off — por eso u es el experimento canónico.",
        ],
        evolucion=("Aquí culmina la síntesis del currículo troncal (m01→m56): "
                   "keynesianos y clásicos conviven como corto y largo plazo del "
                   "MISMO sistema racional. Lo que sigue son los contrapesos: el "
                   "RBC (m57-m61) disputa que las fluctuaciones necesiten rigideces, "
                   "el nivel 9 añade la restricción fiscal y el 12 estimará piezas "
                   "de este modelo con datos peruanos (m100-m101)."),
    ),
    escenarios=[
        Escenario("shock_de_costos", "u0 = 1% con ρ = 0.7 y la regla estándar",
                  {"u0": 1.0},
                  "π sube 1.92%, la brecha cae −1.92% y la tasa sube 1.92pp: el "
                  "triángulo del dilema (m19) con coeficientes exactos y auditables.",
                  cadena=["u > 0 (costos)", "π sube por la NKPC", "la regla dicta ↑i más que π",
                          "la tasa real sube (m38)", "la IS abre brecha negativa",
                          "la brecha contiene a π vía κ", "todo decae a ρ"]),
        Escenario("banco_halcon", "φ_π = 3: dureza máxima",
                  {"phi_pi": 3.0},
                  "la inflación de impacto cae a 1.12% pero la recesión se agranda a "
                  "−3.21%: la frontera de sacrificio no se elimina — se elige un punto.",
                  cadena=["φ_π alto", "cada punto de π trae mucha tasa",
                          "la brecha negativa se profundiza", "κ·x contiene más a π",
                          "menos inflación, más recesión: elección, no magia"]),
        Escenario("banco_complaciente", "φ_π = 0.5: se viola el principio de Taylor",
                  {"phi_pi": 0.5},
                  "b se vuelve POSITIVO: la tasa real cae con el shock, la demanda "
                  "se estimula y la inflación casi se duplica — los años 70 (m24, "
                  "Burns) emergen del álgebra.",
                  cadena=["φ_π < ρ", "la tasa nominal sube menos que π", "la REAL baja",
                          "la IS estimula (b>0)", "la brecha positiva alimenta a π",
                          "convalidación: el fantasma de m14/m24"]),
        Escenario("shock_persistente", "ρ = 0.9: costos que no se van",
                  {"rho": 0.9},
                  "a salta a 3.06: la persistencia del shock multiplica su costo "
                  "total — y el descuento racional lo trae TODO al impacto.",
                  cadena=["↑ρ", "el mercado descuenta un shock largo (m55)",
                          "π de impacto mucho mayor", "la regla aprieta más tiempo",
                          "la brecha acumulada crece con ρ"]),
    ],
    verificaciones=[
        Verificacion("la solución satisface las 3 ecuaciones en todo t", _v_solucion_exacta),
        Verificacion("principio de Taylor: a>0 acotado y b<0", _v_principio_taylor),
        Verificacion("las IRFs decaen exactamente a ρ", _v_decae_a_rho),
        Verificacion("halcón: menos π, más recesión (frontera)", _v_halcon),
        Verificacion("violar el principio ⇒ b>0 (convalidación, Burns)", _v_complaciente_acomoda),
    ],
    notas="Aquí converge el currículo: m54+m55+m38 con m41/m42 debajo — un DSGE mínimo resuelto y auditado a mano.",
)
