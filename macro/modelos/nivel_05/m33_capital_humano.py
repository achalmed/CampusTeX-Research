"""simuladores/macro/modelos/nivel_05/m33_capital_humano.py — capital humano y crecimiento (Solow aumentado) — nivel 5.

Mankiw-Romer-Weil (1992, mención): dos capitales que se acumulan,
  y = k^α·h^β ;  Δk = s_k·y − (n+g+δ)k ;  Δh = s_h·y − (n+g+δ)h
Estados estacionarios (por trabajador efectivo):
  k* = (s_k^{1−β} s_h^{β} / (n+g+δ))^{1/(1−α−β)} ;  h* análogo.
Con α+β ≈ 2/3 el capital "amplio" pesa mucho pero AÚN decrece: hay
convergencia, pero lenta (λ = (1−α−β)(n+g+δ) ≈ 2-3%) — la que se observa.

Procedencia: Mankiw, Romer y Weil (1992, "A Contribution to the Empirics
of Economic Growth", mención) — conocimiento general; educación →
productividad como canal (Lucas 1988, mención).
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _ngd(p):
    return p["n"] + p["g"] + p["delta"]


def _ee(p):
    ngd = _ngd(p)
    expo = 1 / (1 - p["alpha"] - p["beta"])
    k = (p["s_k"] ** (1 - p["beta"]) * p["s_h"] ** p["beta"] / ngd) ** expo
    h = (p["s_k"] ** p["alpha"] * p["s_h"] ** (1 - p["alpha"]) / ngd) ** expo
    return k, h, k ** p["alpha"] * h ** p["beta"]


def _tray(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    ngd = _ngd(p)
    k = np.empty(T + 1); h = np.empty(T + 1)
    k[0], h[0] = p["k0"], p["h0"]
    for t in range(T):
        y = k[t] ** p["alpha"] * h[t] ** p["beta"]
        k[t + 1] = k[t] + p["s_k"] * y - ngd * k[t]
        h[t + 1] = h[t] + p["s_h"] * y - ngd * h[t]
    return np.arange(T + 1), k, h, k ** p["alpha"] * h ** p["beta"]


def _curvas(p):
    t, k, h, y = _tray(p)
    ks, hs, ys = _ee(p)
    return {"lineas": {"ingreso $y_t = k^{\\alpha}h^{\\beta}$": (t, y, config.AZUL2),
                       "capital físico $k_t$": (t, k, config.GRIS),
                       "capital humano $h_t$": (t, h, config.VERDE),
                       "$y^*$": (t, np.full(len(t), ys), config.DORADO)},
            "anotacion": (f"$k^*={ks:.2f}$, $h^*={hs:.2f}$, $y^*={ys:.2f}$\n"
                          f"$\\lambda = (1-\\alpha-\\beta)(n{{+}}g{{+}}\\delta) = "
                          f"{(1 - p['alpha'] - p['beta']) * _ngd(p):.3f}$: convergencia LENTA")}


def _resultados(p):
    ks, hs, ys = _ee(p)
    t, k, h, y = _tray(p)
    return {"k* (físico)": ks, "h* (humano)": hs, "y*": ys,
            "y actual (fin de simulación)": float(y[-1]),
            "λ de convergencia": (1 - p["alpha"] - p["beta"]) * _ngd(p),
            "razón h*/k*": hs / ks,
            "y* si s_h fuera 0.05": _ee(dict(p, s_h=0.05))[2]}


def _ecuaciones_calibradas(p):
    ks, hs, ys = _ee(p)
    return [f"$y = k^{{{p['alpha']:.2f}}}\\,h^{{{p['beta']:.2f}}}$",
            f"$s_k = {p['s_k']:.2f}, \\quad s_h = {p['s_h']:.2f}$",
            f"$k^* = {ks:.2f}, \\quad h^* = {hs:.2f}, \\quad y^* = {ys:.2f}$"]


_P0 = {"s_k": 0.20, "s_h": 0.10, "alpha": 0.33, "beta": 0.33,
       "n": 0.01, "g": 0.02, "delta": 0.05, "k0": 1.0, "h0": 1.0, "T": 120.0}


def _v_punto_fijo():
    ks, hs, ys = _ee(_P0)
    _, k, h, y = _tray(_P0, T=5000)
    ok = abs(k[-1] - ks) < 1e-6 and abs(h[-1] - hs) < 1e-6
    return ok, (f"la iteración 2D converge exactamente a las fórmulas cerradas "
                f"(k*={ks:.3f}, h*={hs:.3f}): el sistema de dos capitales es estable")


def _v_educacion_paga():
    y1 = _ee(_P0)[2]
    y2 = _ee(dict(_P0, s_h=0.20))[2]
    return y2 > 1.8 * y1, (f"duplicar la inversión educativa (s_h: 0.10→0.20) casi duplica y* "
                           f"({y1:.2f}→{y2:.2f}): con β=1/3 la educación es tan motor como las máquinas")


def _v_convergencia_lenta():
    lam = (1 - _P0["alpha"] - _P0["beta"]) * _ngd(_P0)
    lam_solow = (1 - _P0["alpha"]) * _ngd(_P0)
    ok = lam < lam_solow and 0.02 < lam < 0.04
    return ok, (f"λ={lam:.3f} (vs {lam_solow:.3f} sin capital humano): la convergencia al "
                "~2-3% anual que los datos muestran — la anomalía de m27, resuelta")


def _v_complementariedad():
    # invertir solo en máquinas sin educación rinde menos que balancear
    y_solo_k = _ee(dict(_P0, s_k=0.25, s_h=0.05))[2]
    y_balance = _ee(dict(_P0, s_k=0.15, s_h=0.15))[2]
    return y_balance > y_solo_k, (f"mismo esfuerzo total (0.30): balanceado y*={y_balance:.2f} > "
                                  f"solo-máquinas y*={y_solo_k:.2f} — k y h son complementarios")


MODELO = Modelo(
    id="m33", nivel=5,
    nombre="Capital humano y crecimiento (Solow aumentado)",
    xlabel="Período $t$", ylabel="Por trabajador efectivo",
    parametros=[
        Parametro("s_h", _P0["s_h"], 0.02, 0.35, 0.01, "Inversión educativa s_h", grupo="conducta",
                  definicion="fracción del ingreso invertida en capital humano"),
        Parametro("s_k", _P0["s_k"], 0.05, 0.4, 0.01, "Inversión física s_k", grupo="conducta",
                  definicion="fracción invertida en máquinas e infraestructura"),
        Parametro("beta", _P0["beta"], 0.2, 0.45, 0.01, "Participación del capital humano β", grupo="tecnología"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.45, 0.01, "Participación del capital físico α", grupo="tecnología"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="filtraciones"),
        Parametro("g", _P0["g"], 0.0, 0.04, 0.005, "Progreso técnico g", grupo="filtraciones"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="filtraciones"),
        Parametro("k0", _P0["k0"], 0.2, 8.0, 0.2, "Capital físico inicial", grupo="historia"),
        Parametro("h0", _P0["h0"], 0.2, 8.0, 0.2, "Capital humano inicial", grupo="historia"),
        Parametro("T", _P0["T"], 40, 250, 10, "Períodos simulados", grupo="historia"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto del ingreso de las naciones explican la educación y las máquinas juntas — sin apelar a milagros?",
        variables=[("k, h", "capital físico y humano — endógenas (dos acumulaciones)"),
                   ("y", "ingreso por trabajador efectivo — endógena"),
                   ("s_k, s_h", "las DOS decisiones de inversión de una sociedad"),
                   ("α+β", "peso del capital amplio — decide la velocidad de todo")],
        derivacion=["y = k^{\\alpha}\\,h^{\\beta}",
                    "\\Delta k = s_k\\,y - (n+g+\\delta)k \\;;\\; \\Delta h = s_h\\,y - (n+g+\\delta)h",
                    "k^* = \\Big(\\frac{s_k^{1-\\beta} s_h^{\\beta}}{n+g+\\delta}\\Big)^{\\frac{1}{1-\\alpha-\\beta}}"],
        contexto=("En 1992, cuando el crecimiento endógeno (m32) parecía enterrar a "
                  "Solow, Mankiw, Romer y Weil hicieron la pregunta contraria: ¿y si "
                  "a Solow solo le faltaba UN factor? Añadiendo capital humano — "
                  "educación acumulable como las máquinas — el viejo modelo explica "
                  "~80% de las diferencias de ingreso entre países y predice la "
                  "convergencia lenta (~2%) que los datos muestran. La defensa más "
                  "elegante de Solow… con la escuela como tercera protagonista."),
        autores=("Mankiw, Romer y Weil (1992, mención); el capital humano como motor "
                 "viene de Schultz y Becker (menciones) y su versión dinámica de "
                 "Lucas (1988, mención)."),
        supuestos=[
            "El capital humano se ACUMULA como el físico (invirtiendo ingreso: años de escuela, salud) y se deprecia igual.",
            "α+β < 1: el capital amplio pesa mucho (≈2/3) pero AÚN decrece — ni Solow puro ni AK.",
            "Misma tecnología g exógena para todos (la parte de m29 que sigue sin teoría).",
        ],
        ecuaciones=[
            Ecuacion("y = k^{\\alpha}\\,h^{\\beta}", "producción con dos capitales",
                     "máquinas y educación son factores SEPARADOS y complementarios: cada uno "
                     "con rendimientos decrecientes propios, potentes en conjunto."),
            Ecuacion("\\lambda = (1-\\alpha-\\beta)\\,(n+g+\\delta)", "la velocidad reconciliada",
                     "con α+β=2/3, λ≈2.7%: la convergencia lenta que m27 no podía explicar con "
                     "α=1/3 — el capital amplio hace largos los largos plazos."),
        ],
        intuicion=("Entre Solow (α=1/3, converge rápido, el capital explica poco) y AK "
                   "(α=1, no converge nunca, el capital lo es todo), MRW encuentra el "
                   "punto empíricamente dulce: α+β≈2/3. Las máquinas sin escuelas se "
                   "desperdician y las escuelas sin máquinas también (complementariedad "
                   "verificada): la política de crecimiento es una CARTERA, no una "
                   "bala de plata."),
        equilibrio=("Sistema 2D con punto fijo (k*, h*) globalmente estable (iteración "
                    "= fórmulas, verificado): la lógica de Solow sobrevive con dos "
                    "capitales — mientras α+β<1."),
        limitaciones=[
            "Mide educación en cantidad (años/inversión), no CALIDAD — la crítica empírica más dura (Hanushek, mención).",
            "Causalidad disputada: ¿la educación enriquece o los ricos se educan? MRW es contabilidad, no identificación.",
            "h como 'stock' individual ignora externalidades del conocimiento (Lucas 1988): si existen, el mundo se acerca a m32.",
            "g sigue exógeno: el modelo explica NIVELES y transiciones, no la frontera tecnológica.",
        ],
        evolucion=("Cierra el nivel 5 reconciliando teoría y datos: la agenda que "
                   "sigue es endogeneizar g (ideas: Romer 1990, nivel 8+) y medir "
                   "esto con datos reales — para el Perú, educación → productividad → "
                   "crecimiento es exactamente el eje de m106/m112 (nivel 12) y del "
                   "proyecto de reportes educativos de datafw."),
    ),
    escenarios=[
        Escenario("apuesta_educativa", "duplicar la inversión en educación (s_h: 0.10→0.20)",
                  {"s_h": 0.20},
                  "y* casi se duplica (+96%): con β=1/3 la educación rinde tanto como "
                  "las máquinas — pero tarda décadas en madurar (λ≈2.7%).",
                  cadena=["↑s_h", "h se acumula (lento: escolarizar toma décadas)",
                          "y sube con h", "más ingreso financia también más k",
                          "y* casi el doble — a una generación de plazo"]),
        Escenario("solo_maquinas", "todo a lo físico: s_k=0.25, s_h=0.05",
                  {"s_k": 0.25, "s_h": 0.05},
                  "máquinas sin operarios calificados: y* menor que con cartera "
                  "balanceada del MISMO esfuerzo total — la complementariedad castiga.",
                  cadena=["↑s_k con ↓s_h", "k abundante, h escaso",
                          "rendimiento de k cae (falta h complementario)", "y* menor que balanceado"]),
        Escenario("cartera_balanceada", "mismo esfuerzo total, repartido: s_k=s_h=0.15",
                  {"s_k": 0.15, "s_h": 0.15},
                  "con α=β, el reparto simétrico maximiza y* para un esfuerzo dado: "
                  "la política de crecimiento como problema de cartera.",
                  cadena=["s_k = s_h", "k y h crecen a la par", "ningún factor estrangula al otro",
                          "y* máximo para el esfuerzo total dado"]),
    ],
    verificaciones=[
        Verificacion("punto fijo 2D: iteración = fórmulas cerradas", _v_punto_fijo),
        Verificacion("la educación paga: ↑s_h casi duplica y*", _v_educacion_paga),
        Verificacion("λ ≈ 2-3%: la convergencia lenta observada", _v_convergencia_lenta),
        Verificacion("complementariedad: balancear > solo máquinas", _v_complementariedad),
    ],
    notas="Solow defendido con la escuela: α+β≈2/3 reconcilia teoría y datos. Cierra el nivel 5.",
)
