# m53_nk_basico.py — el nuevo keynesianismo básico: rigidez de Calvo (nivel 8).
#
# La reconciliación: expectativas RACIONALES (m42) + rigideces NOMINALES.
# Con la lotería de Calvo, cada período solo (1−θ) de las firmas puede
# reajustar su precio; una fracción θ queda anclada:
#   duración esperada del precio = 1/(1−θ)
#   tras un shock monetario dM, el nivel de precios ajusta gradualmente
#   p_t = (1 − θ^{t+1})·dM   ⇒   y_t = dM − p_t = θ^{t+1}·dM
# El dinero mueve al producto EXACTAMENTE mientras queden precios viejos —
# aunque todos sean racionales y el shock sea conocido: la respuesta a m42.
#
# Procedencia: Calvo (1983, "Staggered prices in a utility-maximizing
# framework" — EN LA BIBLIOTECA de Edison, no verificado aún contra el PDF);
# competencia monopolística: Dixit-Stiglitz (mención); costos de menú:
# Mankiw (mención) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    pth = p["theta"] ** (t + 1)
    precios = (1 - pth) * p["dM"]
    producto = pth * p["dM"]
    return t, precios, producto


def _curvas(p):
    t, precios, producto = _sendas(p)
    return {"lineas": {"efecto real $y_t = \\theta^{t+1}dM$": (t, producto, config.AZUL2),
                       "ajuste de precios $p_t$": (t, precios, config.ROJO),
                       "shock $dM$ (neutralidad final)": (t, np.full(len(t), p["dM"]), config.GRIS)},
            "anotacion": (f"$\\theta = {p['theta']:.2f}$: duración esperada del precio "
                          f"$= 1/(1-\\theta) = {1 / (1 - p['theta']):.1f}$ períodos\n"
                          f"efecto real acumulado $= \\theta/(1-\\theta) \\cdot dM = "
                          f"{p['theta'] / (1 - p['theta']) * p['dM']:.1f}$\n"
                          "racionales + precios de Calvo ⇒ el dinero trabaja")}


def _resultados(p):
    t, precios, producto = _sendas(p, T=200)
    return {"efecto real de impacto (θ·dM)": p["theta"] * p["dM"],
            "duración esperada del precio 1/(1−θ)": 1 / (1 - p["theta"]),
            "efecto real acumulado θ/(1−θ)·dM": p["theta"] / (1 - p["theta"]) * p["dM"],
            "precios al final (= dM)": float(precios[-1]),
            "producto al final (= 0)": float(producto[-1])}


def _ecuaciones_calibradas(p):
    return [f"$p_t = (1-{p['theta']:.2f}^{{\\,t+1}})\\,{p['dM']:.0f}$",
            f"$y_t = {p['theta']:.2f}^{{\\,t+1}} \\times {p['dM']:.0f}$",
            f"$duración = 1/(1-{p['theta']:.2f}) = {1 / (1 - p['theta']):.1f}$"]


_P0 = {"theta": 0.7, "dM": 10.0, "T": 12.0}


def _v_flexible_neutral():
    _, precios, producto = _sendas(dict(_P0, theta=0.0))
    ok = abs(float(producto[0])) < 1e-12 and abs(float(precios[0]) - _P0["dM"]) < 1e-12
    return ok, ("con θ=0 (precios flexibles) TODO va a precios desde t=0: el mundo de "
                "m42 es el caso particular sin rigidez")


def _v_reparto_exacto():
    t, precios, producto = _sendas(_P0)
    return bool(np.all(np.abs(precios + producto - _P0["dM"]) < 1e-12)), \
        "en cada t, precios + producto = dM exacto: el shock se reparte, nunca se pierde"


def _v_duracion_calvo():
    theta = _P0["theta"]
    t = np.arange(4000)
    duracion_num = float(np.sum((t + 1) * (1 - theta) * theta ** t))
    return abs(duracion_num - 1 / (1 - theta)) < 1e-6, \
        (f"la vida media del precio (suma de la geométrica) = {duracion_num:.2f} "
         f"= 1/(1−θ): la lotería de Calvo tiene reloj exacto")


def _v_neutralidad_final():
    _, precios, producto = _sendas(_P0, T=400)
    ok = abs(float(precios[-1]) - _P0["dM"]) < 1e-9 and abs(float(producto[-1])) < 1e-9
    return ok, ("al final, precios = dM y producto = 0: la neutralidad de m35 se respeta — "
                "la rigidez compra TRÁNSITO, no destino")


MODELO = Modelo(
    id="m53", nivel=8,
    nombre="Nuevo keynesiano básico (rigidez de Calvo)",
    xlabel="Período $t$", ylabel="Respuesta al shock $dM$",
    parametros=[
        Parametro("theta", _P0["theta"], 0.0, 0.9, 0.05, "Rigidez de Calvo θ", grupo="estructura",
                  definicion="probabilidad de NO poder reajustar el precio este período"),
        Parametro("dM", _P0["dM"], 2, 25, 1, "Shock monetario dM", grupo="experimento"),
        Parametro("T", _P0["T"], 6, 30, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si todos son racionales y nadie se sorprende, ¿por qué el dinero sigue moviendo al producto?",
        variables=[("θ", "la rigidez — probabilidad de quedarse con el precio viejo"),
                   ("y_t", "el efecto real — vive mientras haya precios viejos"),
                   ("1/(1−θ)", "la duración esperada del precio — el reloj de Calvo")],
        derivacion=["cada\\;período: \\;(1-\\theta)\\;de\\;las\\;firmas\\;reajusta",
                    "p_t = (1-\\theta^{t+1})\\,dM \\;\\;(ajuste\\;acumulado)",
                    "y_t = dM - p_t = \\theta^{t+1}\\,dM"],
        contexto=("m42 dejó a la política monetaria sin oficio: con racionalidad, lo "
                  "anticipado no hace nada. La salida nueva keynesiana no tocó las "
                  "expectativas — tocó los PRECIOS: si reajustar cuesta (menús, "
                  "contratos, atención), las firmas con poder de mercado (competencia "
                  "monopolística) reajustan de a pocas. Calvo (1983 — el paper está "
                  "en la biblioteca de Edison) lo volvió tratable con su lotería: "
                  "cada período una fracción aleatoria (1−θ) puede cambiar precios. "
                  "Resultado: racionales + rigidez ⇒ el dinero mueve al producto "
                  "aunque TODOS entiendan la política."),
        autores=("Calvo (1983 — en biblioteca, pendiente de verificación contra el "
                 "PDF); competencia monopolística: Dixit-Stiglitz (1977, mención); "
                 "costos de menú: Mankiw (1985, mención); síntesis: la escuela "
                 "nueva keynesiana de los 90."),
        supuestos=[
            "Lotería de Calvo: la CHANCE de reajustar es independiente de cuánto necesites hacerlo (irrealista y confesado: simplifica la agregación).",
            "Competencia monopolística de fondo: las firmas PUEDEN dejar precios viejos sin quebrar (tienen margen).",
            "Forma reducida didáctica: el reparto exacto θ/1−θ resume el NK completo (m54-m56 lo microfundan).",
        ],
        ecuaciones=[
            Ecuacion("y_t = \\theta^{\\,t+1}\\,dM", "el efecto real con reloj",
                     "el dinero trabaja mientras queden precios sin reajustar: cada período "
                     "sobrevive una fracción θ del efecto — geométrico, verificable, mortal."),
            Ecuacion("E[duración] = \\frac{1}{1-\\theta}", "el reloj de Calvo",
                     "con θ=0.7, el precio típico vive ~3.3 períodos: ESa es la ventana real de "
                     "la política monetaria — la 'comba' de m35, ahora microfundada."),
        ],
        intuicion=("La rigidez no niega la racionalidad: la firma que no puede "
                   "tocar su precio responde con CANTIDADES, racionalmente. Por eso "
                   "el reparto precios/producto ya no es un supuesto (como el λ de "
                   "m21) sino un resultado del reloj θ. Y la neutralidad final "
                   "queda intacta (verificada): la rigidez compra tránsito, no "
                   "destino — el nivel 6 completo sobrevive dentro del NK."),
        equilibrio=("Convergencia geométrica exacta a la neutralidad (verificada); "
                    "el estado final es el de m35 y el tránsito es la nueva "
                    "economía: TODO el contenido de política vive en θ."),
        limitaciones=[
            "La lotería es una ficción estadística: en la realidad reajusta quien más lo necesita (menús dependientes del estado — mención) y θ cae con inflación alta.",
            "Forma reducida: la NKPC verdadera (m55) conecta θ con la pendiente κ y mira al FUTURO.",
            "Sin capital ni economía abierta: el esqueleto mínimo.",
        ],
        evolucion=("Este es el fundamento micro del nivel: m54 (IS con Euler) y m55 "
                   "(NKPC, donde θ se vuelve κ) son sus dos ecuaciones canónicas y "
                   "m56 el sistema completo. La regla del BCRP con metas opera "
                   "exactamente sobre esta ventana θ (m100-m101)."),
    ),
    escenarios=[
        Escenario("rigidez_tipica", "θ = 0.7: precios que viven ~3.3 períodos",
                  {"theta": 0.7},
                  "el shock rinde 7 de producto al impacto y un acumulado de 23: la "
                  "ventana estándar de la política monetaria trimestral.",
                  cadena=["dM llega", "solo 30% de firmas reajusta", "el resto vende más al precio viejo",
                          "y = θ·dM al impacto", "cada período reajustan más", "neutralidad al final"]),
        Escenario("precios_flexibles", "θ = 0: el mundo de m42",
                  {"theta": 0.0},
                  "todo a precios desde el primer día — el clásico/RBC como caso "
                  "particular del NK con la rigidez apagada.",
                  cadena=["dM llega", "TODAS las firmas reajustan ya",
                          "p = dM al instante", "y = 0: neutralidad inmediata (m42)"]),
        Escenario("rigidez_extrema", "θ = 0.9: contratos larguísimos",
                  {"theta": 0.9},
                  "duración esperada de 10 períodos y efecto acumulado de 90: en "
                  "economías muy indexadas hacia ADELANTE, la política es potentísima "
                  "— y los errores también.",
                  cadena=["θ altísimo", "casi nadie reajusta", "el efecto real sobrevive períodos",
                          "acumulado θ/(1−θ) enorme", "potencia y riesgo crecen juntos"]),
    ],
    verificaciones=[
        Verificacion("θ=0 ⇒ neutralidad instantánea (m42 como caso)", _v_flexible_neutral),
        Verificacion("reparto exacto: precios + producto = dM en todo t", _v_reparto_exacto),
        Verificacion("duración esperada del precio = 1/(1−θ)", _v_duracion_calvo),
        Verificacion("neutralidad final intacta (la rigidez compra tránsito)", _v_neutralidad_final),
    ],
    notas="Racionales + Calvo ⇒ el dinero trabaja. El paper de Calvo (1983) está en la biblioteca, esperando verificación.",
)
