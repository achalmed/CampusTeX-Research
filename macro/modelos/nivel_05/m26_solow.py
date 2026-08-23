# m26_solow.py — modelo de Solow: el diagrama fundamental (nivel 5).
#
#   y = A·k^α ;  inversión = s·A·k^α ;  reposición = (n+δ)·k
#   k* donde s·f(k) = (n+δ)·k  →  k* = (sA/(n+δ))^{1/(1−α)}
# El diagrama de dos curvas responde la pregunta que el nivel 1 dejó abierta:
# a largo plazo, ahorrar más SÍ eleva el ingreso (contra la paradoja m05)…
# pero solo su NIVEL, no su crecimiento (rendimientos decrecientes).
#
# Procedencia: Solow (1956, "A Contribution to the Theory of Economic
# Growth", mención) en la versión de manual — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _ngd(p):
    return p["n"] + p["delta"]


def _curvas(p):
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], _ngd(p))
    k = np.linspace(0.01, max(12.0, 1.6 * ks), 300)
    inv = p["s"] * _solow.f(k, p["A"], p["alpha"])
    rep = _ngd(p) * k
    return {"lineas": {"inversión $s\\,A\\,k^{\\alpha}$": (k, inv, config.AZUL2),
                       "reposición $(n+\\delta)\\,k$": (k, rep, config.ROJO),
                       "producto $y = A\\,k^{\\alpha}$": (k, _solow.f(k, p["A"], p["alpha"]), config.GRIS)},
            "equilibrio": (ks, p["s"] * _solow.f(ks, p["A"], p["alpha"])),
            "anotacion": (f"$k^* = (sA/(n{{+}}\\delta))^{{1/(1-\\alpha)}} = {ks:.2f}$\n"
                          f"$y^* = {_solow.f(ks, p['A'], p['alpha']):.2f}$,  "
                          f"$c^* = {(1 - p['s']) * _solow.f(ks, p['A'], p['alpha']):.2f}$")}


def _resultados(p):
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], _ngd(p))
    ys = _solow.f(ks, p["A"], p["alpha"])
    return {"k* (capital por trabajador)": ks,
            "y* (ingreso por trabajador)": ys,
            "c* (consumo por trabajador)": (1 - p["s"]) * ys,
            "inversión de equilibrio s·y*": p["s"] * ys,
            "crecimiento de y* en EE (%)": 0.0,
            "velocidad de convergencia λ": _solow.velocidad(p["alpha"], _ngd(p))}


def _ecuaciones_calibradas(p):
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], _ngd(p))
    return [f"$y = {p['A']:.2f}\\,k^{{{p['alpha']:.2f}}}$",
            f"$k^* = ({p['s']:.2f} \\times {p['A']:.2f} / {_ngd(p):.3f})^{{1/{1 - p['alpha']:.2f}}} = {ks:.2f}$",
            f"$y^* = {_solow.f(ks, p['A'], p['alpha']):.2f}, \\quad c^* = {(1 - p['s']) * _solow.f(ks, p['A'], p['alpha']):.2f}$"]


_P0 = {"s": 0.20, "A": 1.0, "alpha": 0.33, "n": 0.01, "delta": 0.05}


def _v_estado_estacionario():
    ks = _solow.k_estrella(_P0["s"], _P0["A"], _P0["alpha"], _ngd(_P0))
    dk = _P0["s"] * _solow.f(ks, _P0["A"], _P0["alpha"]) - _ngd(_P0) * ks
    return abs(dk) < 1e-12, f"en k*={ks:.3f} la inversión repone EXACTAMENTE el capital (Δk=0)"


def _v_convergencia_global():
    ngd = _ngd(_P0)
    ks = _solow.k_estrella(_P0["s"], _P0["A"], _P0["alpha"], ngd)
    k_abajo = _solow.trayectoria(0.5 * ks, _P0["s"], _P0["A"], _P0["alpha"], ngd, 2000)
    k_arriba = _solow.trayectoria(2.0 * ks, _P0["s"], _P0["A"], _P0["alpha"], ngd, 2000)
    ok = abs(k_abajo[-1] - ks) < 1e-6 and abs(k_arriba[-1] - ks) < 1e-6
    return ok, "desde arriba y desde abajo, k_t converge al MISMO k*: estabilidad global"


def _v_ahorro_nivel_no_crecimiento():
    ngd = _ngd(_P0)
    y1 = _solow.f(_solow.k_estrella(0.2, _P0["A"], _P0["alpha"], ngd), _P0["A"], _P0["alpha"])
    y2 = _solow.f(_solow.k_estrella(0.3, _P0["A"], _P0["alpha"], ngd), _P0["A"], _P0["alpha"])
    k2 = _solow.trayectoria(_solow.k_estrella(0.3, _P0["A"], _P0["alpha"], ngd),
                            0.3, _P0["A"], _P0["alpha"], ngd, 50)
    g_final = k2[-1] / k2[-2] - 1
    ok = y2 > y1 and abs(g_final) < 1e-9
    return ok, (f"s: 0.2→0.3 sube y* ({y1:.2f}→{y2:.2f}) pero el crecimiento en EE vuelve a 0: "
                "el ahorro compra NIVEL, no crecimiento")


def _v_paradoja_resuelta():
    # m05 (corto plazo): más ahorro ↓Y. Solow (largo plazo): más ahorro ↑y*.
    ngd = _ngd(_P0)
    y_frugal = _solow.f(_solow.k_estrella(0.3, _P0["A"], _P0["alpha"], ngd), _P0["A"], _P0["alpha"])
    y_base = _solow.f(_solow.k_estrella(0.2, _P0["A"], _P0["alpha"], ngd), _P0["A"], _P0["alpha"])
    return y_frugal > y_base, ("la paradoja del ahorro (m05) se INVIERTE a largo plazo: "
                               "con la inversión absorbiendo el ahorro, la frugalidad enriquece")


MODELO = Modelo(
    id="m26", nivel=5,
    nombre="Modelo de Solow",
    xlabel="Capital por trabajador ($k$)", ylabel="Flujos por trabajador",
    parametros=[
        Parametro("s", _P0["s"], 0.05, 0.6, 0.01, "Tasa de ahorro s", grupo="conducta",
                  definicion="fracción del ingreso que se invierte"),
        Parametro("A", _P0["A"], 0.5, 2.0, 0.05, "Productividad A", grupo="tecnología",
                  definicion="eficiencia con que k produce y"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α", grupo="tecnología",
                  definicion="curvatura de f(k): rendimientos decrecientes"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="filtraciones",
                  definicion="nuevos trabajadores que diluyen el capital"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="filtraciones",
                  definicion="capital que se desgasta cada período"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta=("¿Puede una economía crecer para siempre acumulando capital — y por "
                  "qué ahorrar más eleva el ingreso pero no su crecimiento?"),
        variables=[("k", "capital por trabajador — endógena (se acumula)"),
                   ("y, c", "ingreso y consumo por trabajador — endógenas"),
                   ("s, n, δ", "conducta y demografía — exógenas"),
                   ("A, α", "tecnología — exógena (el gran supuesto)")],
        derivacion=["\\dot{K} = s\\,Y - \\delta K \\;;\\; k = K/L,\\; L_{t+1}=(1+n)L_t",
                    "\\Delta k = s\\,A\\,k^{\\alpha} - (n+\\delta)\\,k",
                    "\\Delta k = 0 \\;\\Rightarrow\\; k^* = \\Big(\\frac{sA}{n+\\delta}\\Big)^{1/(1-\\alpha)}"],
        contexto=("En 1956 la teoría dominante (Harrod-Domar, mención) predecía "
                  "economías al filo de la navaja: cualquier desvío entre ahorro y "
                  "requerimientos de capital llevaba al colapso o al desempleo "
                  "explosivo — pero las economías reales crecían estables. Robert "
                  "Solow mostró que bastaba dejar que el capital tuviera rendimientos "
                  "decrecientes y precios flexibles: la acumulación se autorregula y "
                  "el sistema converge a una senda estable. Nació la teoría moderna "
                  "del crecimiento — y con ella una sorpresa: el capital NO puede "
                  "explicar el crecimiento sostenido."),
        autores=("Solow (1956; Nobel 1987) y Swan (1956, independiente — mención). "
                 "La contabilidad del crecimiento (Solow 1957, mención) reveló el "
                 "'residuo': la mayor parte del crecimiento no viene del capital."),
        supuestos=[
            "Rendimientos DECRECIENTES del capital (α<1): cada máquina adicional aporta menos — el supuesto que gobierna todo.",
            "Tasa de ahorro s constante y exógena (nadie optimiza; Ramsey lo endogeneiza — mención).",
            "Pleno empleo y precios flexibles: el largo plazo puro (la LRAS de m22 por dentro).",
            "Sin progreso técnico por ahora: A fija (m29 lo enciende).",
            "Economía cerrada: el ahorro nacional financia la inversión nacional.",
        ],
        ecuaciones=[
            Ecuacion("y = A\\,k^{\\alpha}", "producción por trabajador",
                     "la Cobb-Douglas de m22 en términos per cápita: α≈1/3 según la participación "
                     "del capital en el ingreso."),
            Ecuacion("\\Delta k = s\\,A\\,k^{\\alpha} - (n+\\delta)\\,k", "acumulación",
                     "el capital por trabajador sube con la inversión (s·y) y se diluye con la "
                     "depreciación (δ) y los nuevos trabajadores (n)."),
            Ecuacion("k^* = \\Big(\\frac{s\\,A}{n+\\delta}\\Big)^{\\frac{1}{1-\\alpha}}",
                     "estado estacionario",
                     "donde la inversión repone exactamente lo que se pierde: allí k, y, c por "
                     "trabajador quedan CONSTANTES — el crecimiento per cápita se apaga."),
        ],
        intuicion=("La curva de inversión s·f(k) es cóncava (rendimientos decrecientes) "
                   "y la de reposición (n+δ)k es una recta: tarde o temprano se cruzan, "
                   "y en ese cruce el crecimiento por acumulación muere. Ahorrar más "
                   "desplaza el cruce a la derecha — más ingreso de equilibrio — pero "
                   "no puede impedir el cruce: por eso el ahorro compra NIVEL y solo la "
                   "tecnología (m29) compra CRECIMIENTO. La paradoja de m05 queda "
                   "resuelta por horizonte: frugalidad empobrece en recesión keynesiana "
                   "y enriquece en el largo plazo clásico."),
        equilibrio=("k* único y GLOBALMENTE estable (verificado desde arriba y desde "
                    "abajo): con k<k* la inversión supera a la reposición y k crece; "
                    "con k>k*, al revés. La estabilidad que Harrod-Domar no tenía."),
        limitaciones=[
            "Sin progreso técnico no explica el crecimiento sostenido observado — su propia conclusión central (el 'residuo de Solow' es el elefante).",
            "s exógena: nadie decide ahorrar; la versión con optimización es Ramsey-Cass-Koopmans (mención, nivel 8).",
            "Predice convergencia más rápida y brechas de ingreso menores que las reales (m30, m33 la matizan con capital humano).",
            "Un solo bien, sin dinero ni corto plazo: es exactamente el interior de la LRAS (m22), no un modelo de ciclo.",
        ],
        evolucion=("m27 disecciona el estado estacionario y su velocidad; m28 pregunta "
                   "cuánto ahorro es DEMASIADO (regla de oro); m29 enciende el progreso "
                   "técnico y recupera el crecimiento sostenido; m30-m31 llevan el "
                   "aparato a la pregunta de por qué unos países alcanzan y otros no; "
                   "m32-m33 (AK, capital humano) disputan la exogeneidad de A."),
    ),
    escenarios=[
        Escenario("mas_ahorro", "la tasa de ahorro sube de 0.20 a 0.30",
                  {"s": 0.30},
                  "k* y y* suben (+34% el ingreso), pero el crecimiento de EE vuelve a "
                  "cero: el ahorro compra nivel, no crecimiento — y m28 preguntará si "
                  "tanto ahorro conviene.",
                  cadena=["↑s", "inversión > reposición al k* viejo", "k se acumula",
                          "rendimientos decrecientes frenan", "nuevo k* mayor",
                          "y* mayor, crecimiento otra vez 0"]),
        Escenario("explosion_demografica", "la población acelera (n: 0.01→0.03)",
                  {"n": 0.03},
                  "más trabajadores diluyen el capital: k* e y* caen — el mecanismo "
                  "malthusiano dentro de Solow.",
                  cadena=["↑n", "la recta (n+δ)k gira hacia arriba", "reposición > inversión",
                          "k por trabajador se diluye", "k* e y* menores"]),
        Escenario("salto_tecnologico", "la productividad sube 20% (A: 1.0→1.2)",
                  {"A": 1.2},
                  "y* sube MÁS que 20% (el capital se acumula encima del salto): la "
                  "tecnología es el único motor que no se agota — m29 la hace crecer "
                  "continuamente.",
                  cadena=["↑A", "f(k) e inversión suben a cada k", "nuevo cruce a la derecha",
                          "k* mayor por acumulación inducida", "y* sube más que el propio salto de A"]),
        Escenario("pais_que_no_ahorra", "economía con s = 0.08",
                  {"s": 0.08},
                  "k* = 1.2: la pobreza de equilibrio de una economía que consume casi "
                  "todo — anticipo de la trampa de pobreza (m31).",
                  cadena=["↓s", "poca inversión a cada k", "cruce muy a la izquierda",
                          "k* e y* bajos", "pobreza DE EQUILIBRIO (no transitoria)"]),
    ],
    verificaciones=[
        Verificacion("Δk = 0 exacto en k* (fórmula = punto fijo)", _v_estado_estacionario),
        Verificacion("estabilidad global (converge desde ambos lados)", _v_convergencia_global),
        Verificacion("el ahorro compra nivel, no crecimiento", _v_ahorro_nivel_no_crecimiento),
        Verificacion("la paradoja de m05 se invierte a largo plazo", _v_paradoja_resuelta),
    ],
    notas="El diagrama fundamental del crecimiento: dos curvas que se cruzan y una promesa que se apaga.",
)
