# m28_regla_oro.py — la regla de oro del capital (nivel 5).
#
# ¿Cuánto ahorro es DEMASIADO? El consumo de estado estacionario
#   c*(s) = (1−s)·A·k*(s)^α = A·k*^α − (n+δ)·k*
# se maximiza donde f'(k) = n+δ  →  en Cobb-Douglas:  s_oro = α.
# Ahorrar MÁS que α es ineficiencia dinámica: toda la senda de consumo puede
# mejorarse ahorrando menos (comer capital gratis).
#
# Procedencia: Phelps (1961, "The Golden Rule of Accumulation", mención) —
# conocimiento general; s_oro=α en Cobb-Douglas: resultado estándar.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _ngd(p):
    return p["n"] + p["delta"]


def _c_ee(s, p):
    ks = _solow.k_estrella(s, p["A"], p["alpha"], _ngd(p))
    return (1 - s) * _solow.f(ks, p["A"], p["alpha"])


def _curvas(p):
    s_grid = np.linspace(0.02, 0.85, 300)
    c = np.array([_c_ee(s, p) for s in s_grid])
    s_oro = p["alpha"]
    return {"lineas": {"$c^*(s)$: consumo de estado estacionario": (s_grid, c, config.AZUL2)},
            "equilibrio": (s_oro, _c_ee(s_oro, p)),
            "puntos": [(p["s"], _c_ee(p["s"], p), f"tu economía ($s={p['s']:.2f}$)")],
            "anotacion": (f"$s_{{oro}} = \\alpha = {p['alpha']:.2f}$\n"
                          f"$c^*_{{oro}} = {_c_ee(s_oro, p):.3f}$\n"
                          f"a la derecha de $s_{{oro}}$: ineficiencia dinámica")}


def _resultados(p):
    s_oro = p["alpha"]
    ks = _solow.k_estrella(p["s"], p["A"], p["alpha"], _ngd(p))
    return {"c* con tu s": _c_ee(p["s"], p),
            "s de la regla de oro (= α)": s_oro,
            "c* en la regla de oro": _c_ee(s_oro, p),
            "consumo sacrificado (%)": 100 * (1 - _c_ee(p["s"], p) / _c_ee(s_oro, p)),
            "f'(k*) − (n+δ) (signo del lado)": p["alpha"] * p["A"] * ks ** (p["alpha"] - 1) - _ngd(p)}


def _ecuaciones_calibradas(p):
    return [f"$c^*(s) = (1-s)\\,A\\,k^*(s)^{{\\alpha}}$",
            f"$s_{{oro}} = \\alpha = {p['alpha']:.2f}$",
            f"$c^*({p['s']:.2f}) = {_c_ee(p['s'], p):.3f} \\;\\; vs \\;\\; "
            f"c^*_{{oro}} = {_c_ee(p['alpha'], p):.3f}$"]


_P0 = {"s": 0.20, "A": 1.0, "alpha": 0.33, "n": 0.01, "delta": 0.05}


def _v_argmax():
    s_grid = np.linspace(0.02, 0.9, 4001)
    c = np.array([_c_ee(s, _P0) for s in s_grid])
    s_max = float(s_grid[int(np.argmax(c))])
    return abs(s_max - _P0["alpha"]) < 2e-3, (f"el máximo numérico de c*(s) cae en s={s_max:.3f} "
                                              f"= α: la regla de oro es s_oro = α (Cobb-Douglas)")


def _v_condicion_marginal():
    ks_oro = _solow.k_estrella(_P0["alpha"], _P0["A"], _P0["alpha"], _ngd(_P0))
    fp = _P0["alpha"] * _P0["A"] * ks_oro ** (_P0["alpha"] - 1)
    return abs(fp - _ngd(_P0)) < 1e-12, f"en k_oro: f'(k) = n+δ exacto ({fp:.4f}): PMg del capital = costo de sostenerlo"


def _v_sobreahorro_domina():
    # con s=0.5 > α: bajar s a α sube el consumo en el EE nuevo Y en el tránsito
    p_alto = dict(_P0, s=0.5)
    ngd = _ngd(_P0)
    k_inicial = _solow.k_estrella(0.5, _P0["A"], _P0["alpha"], ngd)
    k_tray = _solow.trayectoria(k_inicial, _P0["alpha"], _P0["A"], _P0["alpha"], ngd, 300)
    c_tray = (1 - _P0["alpha"]) * _solow.f(k_tray, _P0["A"], _P0["alpha"])
    c_viejo = _c_ee(0.5, _P0)
    ok = bool(np.all(c_tray > c_viejo - 1e-12))
    return ok, ("con s=0.5>α, bajar s a α sube el consumo HOY y en TODO el futuro: "
                "el sobreahorro es ineficiencia dinámica (almuerzo gratis)")


def _v_subahorro_no_domina():
    # con s=0.2 < α: subir s sacrifica consumo presente (no hay almuerzo gratis)
    ngd = _ngd(_P0)
    k_inicial = _solow.k_estrella(0.2, _P0["A"], _P0["alpha"], ngd)
    k_tray = _solow.trayectoria(k_inicial, _P0["alpha"], _P0["A"], _P0["alpha"], ngd, 300)
    c_tray = (1 - _P0["alpha"]) * _solow.f(k_tray, _P0["A"], _P0["alpha"])
    c_viejo = _c_ee(0.2, _P0)
    return bool(c_tray[1] < c_viejo), ("con s<α, subir el ahorro CUESTA consumo presente: "
                                       "llegar al oro exige sacrificio (decisión intergeneracional)")


MODELO = Modelo(
    id="m28", nivel=5,
    nombre="Regla de oro del capital",
    xlabel="Tasa de ahorro ($s$)", ylabel="Consumo de estado estacionario ($c^*$)",
    parametros=[
        Parametro("s", _P0["s"], 0.05, 0.8, 0.01, "Tasa de ahorro de tu economía"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α (= s_oro)"),
        Parametro("A", _P0["A"], 0.5, 2.0, 0.05, "Productividad A"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto ahorro es demasiado — existe un nivel de capital que empobrece?",
        variables=[("c*(s)", "consumo de EE como función del ahorro — el objeto a maximizar"),
                   ("s_oro", "la tasa que lo maximiza — resultado: α"),
                   ("k_oro", "capital de la regla de oro — donde f'(k)=n+δ")],
        derivacion=["c^* = A\\,k^{*\\alpha} - (n+\\delta)\\,k^*",
                    "\\frac{dc^*}{dk^*} = \\alpha A k^{*\\alpha-1} - (n+\\delta) = 0",
                    "f'(k_{oro}) = n+\\delta \\;\\Rightarrow\\; s_{oro} = \\alpha \\;(Cobb\\!-\\!Douglas)"],
        contexto=("Si m26 mostró que más ahorro da más ingreso, ¿por qué no ahorrar "
                  "80%? Phelps (1961) respondió con una fábula: el reino de Solovia "
                  "busca la acumulación que maximiza el CONSUMO — porque se vive de "
                  "consumir, no de acumular. El resultado incomoda a los fetichistas "
                  "del ahorro: existe un punto más allá del cual el capital solo "
                  "trabaja para mantenerse a sí mismo."),
        autores=("Phelps (1961, mención; Nobel 2006). La condición f'(k)=n+δ es el "
                 "puente hacia la eficiencia dinámica (Diamond 1965, mención)."),
        supuestos=["Los de m26; el criterio es el consumo de ESTADO ESTACIONARIO (no descuenta el tránsito).",
                   "Sin preferencias explícitas: la 'optimalidad' es de largo plazo puro (Ramsey pondría descuento — mención).",
                   "Cobb-Douglas hace s_oro = α exacto: elegancia, no generalidad."],
        ecuaciones=[
            Ecuacion("c^*(s) = (1-s)\\,A\\,k^*(s)^{\\alpha}", "el menú de estados estacionarios",
                     "cada s compra un k* distinto; consumir más HOY (s bajo) o tener más "
                     "capital MAÑANA (s alto): c*(s) es la frontera de esa elección."),
            Ecuacion("f'(k_{oro}) = n + \\delta", "condición de la regla de oro",
                     "acumula mientras el producto marginal del capital supere su costo de "
                     "mantenimiento; detente cuando se igualan."),
        ],
        intuicion=("A la izquierda de s_oro, ahorrar más rinde: el capital extra "
                   "produce más de lo que cuesta reponerlo. A la derecha, el capital es "
                   "tan abundante que su producto marginal ya no paga ni su "
                   "depreciación+dilución: la economía trabaja para alimentar máquinas. "
                   "La asimetría es lo profundo: el sobreahorro se corrige GRATIS "
                   "(bajar s sube el consumo en toda la senda, verificado); el "
                   "subahorro no — subir s cuesta consumo presente, y decidirlo es un "
                   "conflicto entre generaciones que el modelo no puede resolver."),
        equilibrio=("Máximo interior único de c*(s) en s=α (verificado numéricamente); "
                    "s>α define la región dinámicamente INEFICIENTE."),
        limitaciones=[
            "El criterio ignora el tránsito y el descuento temporal: con impaciencia (Ramsey) el s óptimo es MENOR que el de oro (regla de oro modificada — mención).",
            "Economías reales parecen estar DEBAJO del oro (f'(k)>n+δ): la ineficiencia dinámica es rara — el interés del caso es conceptual.",
            "s como elección social única: en realidad la deciden millones de hogares y el sistema financiero (niveles 8-9).",
        ],
        evolucion=("Cierra la estática del ahorro: m26 (nivel), m27 (velocidad), m28 "
                   "(óptimo). Lo que sigue es el motor que falta: m29 enciende el "
                   "progreso técnico y todo este análisis se re-lee 'por trabajador "
                   "efectivo'. La versión con hogares optimizadores (Ramsey) espera en "
                   "el nivel 8."),
    ),
    escenarios=[
        Escenario("subahorro", "economía en s = 0.20 < α",
                  {"s": 0.20},
                  "consume 1.4% menos que en el oro; subir s mejoraría el EE pero "
                  "cuesta consumo presente: no hay almuerzo gratis de este lado.",
                  cadena=["s < α", "f'(k*) > n+δ", "capital escaso rinde de sobra",
                          "subir s mejora el EE", "pero sacrifica consumo HOY",
                          "decisión intergeneracional"]),
        Escenario("sobreahorro", "economía fetichista del capital: s = 0.55",
                  {"s": 0.55},
                  "el capital ya no se paga a sí mismo: bajar s hacia α sube el "
                  "consumo hoy Y siempre — ineficiencia dinámica pura.",
                  cadena=["s > α", "f'(k*) < n+δ", "el capital no paga su mantenimiento",
                          "bajar s libera consumo", "mejora HOY y SIEMPRE",
                          "almuerzo gratis (ineficiencia dinámica)"]),
        Escenario("en_el_oro", "la economía justo en s = α = 0.33",
                  {"s": 0.33},
                  "el punto de Phelps: máximo consumo sostenible por siempre.",
                  cadena=["s = α", "f'(k*) = n+δ exacto", "PMg del capital = costo de sostenerlo",
                          "c* máximo sostenible"]),
    ],
    verificaciones=[
        Verificacion("argmax numérico de c*(s) = α", _v_argmax),
        Verificacion("condición marginal f'(k_oro) = n+δ exacta", _v_condicion_marginal),
        Verificacion("sobreahorro: bajar s domina en TODA la senda", _v_sobreahorro_domina),
        Verificacion("subahorro: subir s cuesta consumo presente", _v_subahorro_no_domina),
    ],
    notas="Se vive de consumir, no de acumular: el capital óptimo existe y ahorrar de más es tirar consumo.",
)
