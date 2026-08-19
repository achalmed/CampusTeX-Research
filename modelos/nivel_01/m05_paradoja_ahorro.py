# m05_paradoja_ahorro.py — paradoja del ahorro en la cruz keynesiana (nivel 1).
#
# Cruz keynesiana:  DA = C0 + c(Y−T) + I + G ;  equilibrio DA = Y
#   → Y* = (C0 − cT + I + G) / (1−c)
# Experimento: los hogares desean ahorrar más (C0 baja en dC0).
# Resultado (con I, G, T fijos): Y* cae en k·dC0 y el ahorro agregado de
# equilibrio NO cambia — S* = I + (G−T) siempre. Esa es la paradoja.
#
# Procedencia: Keynes (1936) y manuales keynesianos — conocimiento general;
# antecedente retórico: Mandeville, La fábula de las abejas (1714).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _equilibrio(C0, p):
    return (C0 - p["c"] * p["T"] + p["I"] + p["G"]) / (1 - p["c"])


def _curvas(p):
    C0a, C0d = p["C0"], p["C0"] - p["dC0"]
    Ya, Yd_ = _equilibrio(C0a, p), _equilibrio(C0d, p)
    Y = np.linspace(0, max(Ya, Yd_) * 1.25, 300)
    da = lambda C0: C0 + p["c"] * (Y - p["T"]) + p["I"] + p["G"]
    return {"lineas": {"DA antes": (Y, da(C0a), config.AZUL2),
                       "DA después (↑ahorro deseado)": (Y, da(C0d), config.ROJO),
                       "recta de 45° (DA = Y)": (Y, Y, config.GRIS)},
            "puntos": [(Ya, Ya, f"antes: Y*={Ya:,.0f}"),
                       (Yd_, Yd_, f"después: Y*={Yd_:,.0f}")],
            "anotacion": (f"ΔY = {Yd_ - Ya:,.1f} = −k·ΔC0\n"
                          f"ahorro de equilibrio: S* = I + G − T = "
                          f"{p['I'] + p['G'] - p['T']:,.1f} (no cambia)")}


def _resultados(p):
    Ya = _equilibrio(p["C0"], p)
    Yd_ = _equilibrio(p["C0"] - p["dC0"], p)
    Ca = p["C0"] + p["c"] * (Ya - p["T"])
    Cd = (p["C0"] - p["dC0"]) + p["c"] * (Yd_ - p["T"])
    return {"Y* antes": Ya, "Y* después": Yd_, "ΔY": Yd_ - Ya,
            "consumo antes": Ca, "consumo después": Cd,
            "ahorro privado antes": Ya - p["T"] - Ca,
            "ahorro privado después": Yd_ - p["T"] - Cd,
            "Δ ahorro (la paradoja)": (Yd_ - p["T"] - Cd) - (Ya - p["T"] - Ca)}


_P0 = {"C0": 150.0, "dC0": 50.0, "c": 0.8, "I": 200.0, "G": 150.0, "T": 100.0}


def _v_paradoja():
    r = _resultados(_P0)
    return abs(r["Δ ahorro (la paradoja)"]) < 1e-9, ("querer ahorrar más NO aumenta el ahorro "
                                                     "agregado: ΔS* = 0 (con I, G, T fijos)")


def _v_ahorro_igual_inversion():
    r = _resultados(_P0)
    objetivo = _P0["I"] + _P0["G"] - _P0["T"]
    ok = (abs(r["ahorro privado antes"] - objetivo) < 1e-9
          and abs(r["ahorro privado después"] - objetivo) < 1e-9)
    return ok, f"en ambos equilibrios S* = I + (G−T) = {objetivo:,.1f}: el ahorro lo fija la inversión"


def _v_caida():
    r = _resultados(_P0)
    k = 1 / (1 - _P0["c"])
    return abs(r["ΔY"] + k * _P0["dC0"]) < 1e-9, f"la renta cae exactamente k·ΔC0 = {k * _P0['dC0']:,.1f}"


MODELO = Modelo(
    id="m05", nivel=1,
    nombre="Paradoja del ahorro",
    xlabel="Producto (Y)", ylabel="Demanda agregada (DA)",
    parametros=[
        Parametro("C0", _P0["C0"], 50, 300, 10, "Consumo autónomo inicial C0"),
        Parametro("dC0", _P0["dC0"], 0, 120, 5, "Aumento del ahorro deseado (caída de C0)"),
        Parametro("c", _P0["c"], 0.1, 0.95, 0.05, "Propensión marginal a consumir c"),
        Parametro("I", _P0["I"], 50, 400, 10, "Inversión (exógena y fija)"),
        Parametro("G", _P0["G"], 0, 400, 10, "Gasto público G"),
        Parametro("T", _P0["T"], 0, 400, 10, "Impuestos T"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("Si cada hogar decide ahorrar más, ¿ahorra más la sociedad? La "
                  "respuesta keynesiana en recesión es NO: el menor consumo reduce el "
                  "ingreso de otros, y con él su capacidad de ahorrar. La virtud privada "
                  "puede ser vicio público — intuición que Mandeville escandalizó en 1714 "
                  "y que Keynes convirtió en teoría durante la Depresión, cuando la "
                  "austeridad de todos hundía la demanda de todos."),
        autores=("Keynes (1936) y la tradición keynesiana de manuales; antecedente "
                 "retórico: Mandeville, La fábula de las abejas (1714)."),
        supuestos=[
            "La inversión es EXÓGENA y fija: no responde al mayor ahorro disponible ni a la tasa de interés (supuesto crucial).",
            "Precios fijos y capacidad ociosa: el ajuste es por cantidades (Y), no por precios.",
            "Economía cerrada con G y T fijos.",
            "El mayor deseo de ahorro se modela como caída del consumo autónomo (C0 → C0 − ΔC0).",
        ],
        ecuaciones=[
            Ecuacion("DA = C_0 + c\\,(Y-T) + I + G", "demanda agregada",
                     "consumo keynesiano (m03) más gasto autónomo; la cruz keynesiana "
                     "grafica DA contra Y."),
            Ecuacion("Y^* = \\frac{C_0 - c\\,T + I + G}{1-c}", "equilibrio (DA = Y)",
                     "el gasto autónomo multiplicado por k = 1/(1−c) (m04)."),
            Ecuacion("\\Delta Y^* = -\\frac{\\Delta C_0}{1-c}", "efecto del mayor ahorro deseado",
                     "la caída del consumo autónomo se multiplica igual que cualquier shock de gasto."),
            Ecuacion("S^* = I + (G - T)", "ahorro privado de equilibrio",
                     "de la condición de equilibrio: el ahorro agregado queda determinado por la "
                     "inversión (y el déficit público), NO por el deseo de ahorrar."),
        ],
        intuicion=("El ahorro individual y el agregado obedecen lógicas distintas (falacia "
                   "de composición). Un hogar que consume menos ahorra más PORQUE su "
                   "ingreso no depende de su propio gasto; la sociedad no tiene esa "
                   "suerte: su ingreso ES su gasto. Con inversión fija, el ahorro agregado "
                   "está anclado (S* = I + G − T) y el único ajuste posible ante más "
                   "frugalidad es una renta menor."),
        equilibrio=("Estable: si Y > Y*, la producción excede la demanda, se acumulan "
                    "existencias no deseadas y las empresas recortan producción (y "
                    "viceversa). El desplazamiento de DA mueve el punto de corte con la "
                    "recta de 45°."),
        limitaciones=[
            "Todo descansa en I exógena: si la inversión responde a la tasa de interés o al ahorro disponible, la paradoja se debilita (m06, m10).",
            "Es estrictamente de corto plazo: en el largo plazo más ahorro financia más capital y MÁS producto (Solow, m26) — la paradoja se invierte.",
            "Sin sector externo: en economía abierta parte del ajuste sale por importaciones y cuenta corriente (m43-m49).",
            "Sin precios: en pleno empleo el menor consumo liberaría recursos hacia inversión vía precios/tasas, no hundiría Y.",
        ],
        evolucion=("Es el broche del nivel 1: exhibe a la vez el poder del multiplicador "
                   "y la fragilidad de sus supuestos. El nivel 2 endogeniza la inversión "
                   "con la tasa de interés (IS-LM, m06-m12) y el nivel 5 (Solow, m26) "
                   "reconcilia el corto plazo keynesiano con el largo plazo, donde el "
                   "ahorro vuelve a ser virtud."),
        referencias=["Keynes (1936), Teoría General — mención, no verificado contra edición",
                     "Mandeville (1714), La fábula de las abejas — antecedente histórico (mención)"],
    ),
    escenarios=[
        Escenario("frugalidad_leve", "los hogares recortan el consumo autónomo en 25",
                  {"dC0": 25.0},
                  "Y* cae 125 (= 5×25); el ahorro agregado no se mueve un céntimo."),
        Escenario("frugalidad_fuerte", "recorte severo del consumo autónomo (100)",
                  {"dC0": 100.0},
                  "la renta cae 500 y el ahorro sigue clavado en I+G−T: mientras más "
                  "intentan ahorrar todos, más pobres terminan todos — sin ahorrar más."),
        Escenario("hogares_gastadores", "con PMC alta (c = 0.9) el castigo es mayor",
                  {"c": 0.9},
                  "k = 10: la misma frugalidad hunde el doble la renta — economías de "
                  "alto re-gasto amplifican la paradoja."),
    ],
    verificaciones=[
        Verificacion("ΔS* = 0 (la paradoja, exacta)", _v_paradoja),
        Verificacion("S* = I + (G−T) en ambos equilibrios", _v_ahorro_igual_inversion),
        Verificacion("ΔY = −k·ΔC0 (multiplicador en reversa)", _v_caida),
    ],
    notas="El supuesto que carga toda la paradoja es I exógena — vigilarlo es la puerta al nivel 2.",
)
