# m12_trampa_liquidez.py — trampa de liquidez / límite inferior cero (nivel 2).
#
# IS-LM con un piso en la tasa: r no puede bajar de 0 (nadie presta a tasa
# negativa pudiendo guardar efectivo). LM efectiva = max(0, (kY − M/P)/h).
# Si la demanda es tan débil que la IS corta en el tramo plano:
#   - la política monetaria pierde tracción: ↑M/P no mueve Y (el dinero se atesora);
#   - la política fiscal recupera el multiplicador PLENO del nivel 1 (Δr = 0).
# Calibración base: demanda deliberadamente débil (c0=60, I0=80) para nacer
# dentro de la trampa.
#
# Procedencia: Keynes (1936, mención) y Hicks (1937, tramo plano de LM);
# relectura moderna: Krugman (1998, Japón) y la literatura del ZLB post-2008 —
# conocimiento macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _equilibrio(p):
    """Resuelve IS-LM con piso r ≥ 0. Si la solución no restringida da r<0,
    el equilibrio cae en el tramo plano: r=0 e Y sale de la IS sola."""
    A = (1 - p["c1"]) + p["b"] * p["k"] / p["h"]
    B = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"] + p["b"] * p["MP"] / p["h"]
    Y_u = B / A
    r_u = (p["k"] * Y_u - p["MP"]) / p["h"]
    if r_u >= 0:
        return Y_u, r_u, False
    autonomo = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"]
    return autonomo / (1 - p["c1"]), 0.0, True


def _curvas(p):
    Y = np.linspace(200, 900, 400)
    r_is = (p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"] - (1 - p["c1"]) * Y) / p["b"]
    lm0 = np.maximum(0.0, (p["k"] * Y - p["MP"]) / p["h"])
    lm1 = np.maximum(0.0, (p["k"] * Y - (p["MP"] + p["dMP"])) / p["h"])
    Ye, re, trampa = _equilibrio(p)
    return {"lineas": {"IS": (Y, r_is, config.AZUL2),
                       "LM (piso $r=0$)": (Y, lm0, config.ROJO),
                       "LM con más dinero ($dMP$)": (Y, lm1, config.VERDE)},
            "equilibrio": (Ye, re),
            "anotacion": (f"{'EN LA TRAMPA: la IS corta el tramo plano' if trampa else 'fuera de la trampa'}\n"
                          f"$Y^* = {Ye:,.1f}$,  $r^* = {re:.2f}\\%$\n"
                          f"el dinero extra ($dMP={p['dMP']:.0f}$) {'NO mueve Y' if trampa else 'sí opera'}")}


def _resultados(p):
    Ye, re, trampa = _equilibrio(p)
    Y_dinero, _, _ = _equilibrio(dict(p, MP=p["MP"] + 100))
    Y_gasto, _, _ = _equilibrio(dict(p, G=p["G"] + 1))
    return {"Y*": Ye, "r*": re, "en la trampa (1=sí)": 1.0 if trampa else 0.0,
            "efecto de +100 de dinero sobre Y": Y_dinero - Ye,
            "multiplicador fiscal local (dY/dG)": Y_gasto - Ye,
            "multiplicador simple 1/(1−c1)": 1 / (1 - p["c1"])}


def _ecuaciones_calibradas(p):
    Ye, re, trampa = _equilibrio(p)
    k = 1 / (1 - p["c1"])
    F = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"]
    if trampa:
        return [f"$r^* = 0 \\;\\;(piso)$",
                f"$Y^* = k\\,F = {k:.2f} \\times {F:.0f} = {Ye:,.1f}$",
                f"$dY/dG = k = {k:.2f}$"]
    return [f"$Y^* = {Ye:,.1f}, \\quad r^* = {re:.2f} > 0$",
            f"$dY/dG < {k:.2f}$"]


_P0 = {"c0": 60.0, "c1": 0.6, "I0": 80.0, "b": 20.0, "G": 150.0, "T": 100.0,
       "k": 0.5, "h": 10.0, "MP": 300.0, "dMP": 100.0}


def _v_en_trampa():
    Ye, re, trampa = _equilibrio(_P0)
    return trampa and re == 0.0, f"calibración base dentro de la trampa (Y*={Ye:,.1f}, r*=0)"


def _v_dinero_impotente():
    Y0, _, _ = _equilibrio(_P0)
    Y1, _, _ = _equilibrio(dict(_P0, MP=_P0["MP"] + 100))
    return abs(Y1 - Y0) < 1e-9, "en la trampa, +100 de dinero deja Y exactamente igual (se atesora)"


def _v_fiscal_pleno():
    r = _resultados(_P0)
    return abs(r["multiplicador fiscal local (dY/dG)"] - r["multiplicador simple 1/(1−c1)"]) < 1e-9, \
        "en la trampa el multiplicador fiscal es el PLENO del nivel 1 (Δr=0 → sin expulsión)"


def _v_salida_fiscal():
    Ye, re, trampa = _equilibrio(dict(_P0, G=200.0))
    r_local = _resultados(dict(_P0, G=200.0))["multiplicador fiscal local (dY/dG)"]
    ok = (not trampa) and re > 0 and r_local < 1 / (1 - _P0["c1"])
    return ok, (f"con G=200 la IS sale del tramo plano (r*={re:.2f}>0) y el multiplicador "
                f"vuelve a ser el amortiguado del IS-LM ({r_local:.2f})")


MODELO = Modelo(
    id="m12", nivel=2,
    nombre="Trampa de liquidez",
    xlabel="Producto ($Y$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("dMP", _P0["dMP"], 0, 300, 10, "Dinero extra dMP (para ver su impotencia)"),
        Parametro("G", _P0["G"], 50, 350, 10, "Gasto público G"),
        Parametro("I0", _P0["I0"], 20, 200, 10, "Ánimo inversor I0 (bajo = demanda débil)"),
        Parametro("c0", _P0["c0"], 20, 200, 10, "Consumo autónomo c0"),
        Parametro("MP", _P0["MP"], 100, 600, 10, "Oferta real de dinero M/P"),
        Parametro("c1", _P0["c1"], 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 5, 50, 1, "Sensibilidad de I a r (b)"),
        Parametro("k", _P0["k"], 0.1, 1.0, 0.05, "Demanda de dinero por Y (k)"),
        Parametro("h", _P0["h"], 2, 30, 1, "Demanda de dinero por r (h)"),
        Parametro("T", _P0["T"], 0, 300, 10, "Impuestos T"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta=("¿Por qué con tasas en cero el dinero deja de funcionar y el gasto "
                  "público recupera toda su potencia?"),
        variables=[("Y, r", "producto y tasa — endógenas"),
                   ("régimen", "dentro/fuera de la trampa — ENDÓGENO (frontera r=0)"),
                   ("dMP, G", "instrumentos monetario y fiscal — exógenos"),
                   ("c0, I0", "el 'ánimo' de la demanda — deciden si se cae en la trampa")],
        derivacion=["r_u = \\frac{k\\,Y_u - M/P}{h} \\;\\;(solución\\;sin\\;piso)",
                    "r_u < 0 \\;\\Rightarrow\\; r^* = 0 \\;(el\\;piso\\;ata)",
                    "Y^*\\big|_{r=0} = \\frac{c_0 - c_1 T + I_0 + G}{1-c_1}"],
        contexto=("Keynes especuló con una situación en la que la política monetaria "
                  "'empuja una cuerda': con tasas ya en el suelo y expectativas "
                  "deprimidas, el dinero extra se atesora en vez de prestarse. Hicks la "
                  "dibujó como el tramo plano de su LM. Fue curiosidad de manual durante "
                  "décadas — hasta que Japón (años 90) y luego medio mundo (2008-2015, "
                  "tasas de política en cero) la convirtieron en el problema práctico "
                  "número uno; Krugman (1998) la resucitó teóricamente."),
        autores=("Keynes (1936, mención); Hicks (1937); relectura moderna: Krugman "
                 "(1998) y la literatura del zero lower bound post-2008."),
        supuestos=[
            "El efectivo rinde 0: nadie acepta bonos con rendimiento negativo, así que r ≥ 0 (piso nominal).",
            "Demanda agregada débil: la IS corta a la LM en (o bajo) el piso — la trampa es un ESTADO, no un parámetro.",
            "Los del IS-LM en lo demás (precios fijos: la deflación, que agrava la trampa vía tasa real, llega en m94).",
        ],
        ecuaciones=[
            Ecuacion("r_{LM}^{efectiva}(Y) = \\max\\!\\left(0, \\frac{kY - M/P}{h}\\right)", "LM con piso",
                     "el tramo plano en r=0: allí el público absorbe cualquier cantidad de dinero "
                     "sin exigir compensación — dinero y bonos se vuelven sustitutos perfectos."),
            Ecuacion("Y^*\\big|_{trampa} = \\frac{c_0 - c_1 T + I_0 + G}{1-c_1}", "equilibrio en la trampa",
                     "con r clavada en 0, la LM desaparece del problema: manda la IS sola y el "
                     "multiplicador vuelve a ser el simple del nivel 1."),
        ],
        intuicion=("La trampa invierte los veredictos del m11: la política monetaria, "
                   "normalmente potente, se vuelve inocua (el dinero extra se guarda); "
                   "la fiscal, normalmente amortiguada por la expulsión, recupera toda "
                   "su fuerza porque no hay tasa que subir. Por eso la respuesta a 2008 "
                   "combinó estímulo fiscal con políticas monetarias NO convencionales "
                   "(comprar activos largos, prometer tasas bajas futuras)."),
        equilibrio=("Dos regímenes con frontera endógena: si la solución no restringida "
                    "del IS-LM da r≥0, vale m10; si da r<0, el equilibrio efectivo está "
                    "en el tramo plano (r=0, Y de la IS). Los shocks pueden cruzar la "
                    "frontera — salir de la trampa es un cambio de régimen."),
        limitaciones=[
            "Con precios flexibles la deflación SUBE la tasa real aunque la nominal esté en 0 — la trampa moderna es peor que esta versión (m94, nivel 8 con ZLB).",
            "El piso exacto no es 0 (varios bancos centrales probaron tasas levemente negativas), pero existe uno.",
            "No modela las salidas no convencionales (QE, forward guidance): aquí 'dinero' es un solo activo.",
            "Expectativas ausentes: Krugman mostró que la trampa es en el fondo un problema de EXPECTATIVAS de inflación — prometer inflación futura la desarma.",
        ],
        evolucion=("Cierra el nivel 2 mostrando que las pendientes del IS-LM no son "
                   "tecnicismos: deciden qué política funciona. La versión con precios y "
                   "deflación es m94; la versión nuevo keynesiana con ZLB y expectativas "
                   "llega en el nivel 8 — y el episodio aplicado (Japón, 2008-2015) es m95."),
    ),
    escenarios=[
        Escenario("mas_dinero_aun", "duplicar la inyección monetaria (dMP = 200)",
                  {"dMP": 200.0},
                  "la LM verde se corre más a la derecha… y el equilibrio no se mueve un "
                  "milímetro: en la trampa, emitir es empujar la cuerda.",
                  cadena=["↑↑M/P", "r ya está en 0 (piso)", "el dinero se atesora",
                          "el tramo plano se alarga pero no baja", "ΔY = 0"]),
        Escenario("rescate_fiscal", "el gasto sube de 150 a 200",
                  {"G": 200.0},
                  "la IS sale del tramo plano: Y sube con multiplicador pleno mientras "
                  "dura la trampa, y al salir (r*>0) reaparece la expulsión.",
                  cadena=["↑G", "IS → derecha SOBRE el tramo plano", "Δr = 0",
                          "sin expulsión", "multiplicador pleno", "posible salida de la trampa"]),
        Escenario("depresion_profunda", "el ánimo inversor se hunde (I0: 80→60)",
                  {"I0": 60.0},
                  "más adentro de la trampa: la brecha que la política monetaria no puede "
                  "cerrar se agranda — el caso Japón.",
                  cadena=["↓I0 (pesimismo)", "IS → izquierda", "más hondo en el tramo plano",
                          "la brecha que el dinero no puede cerrar crece"]),
    ],
    verificaciones=[
        Verificacion("la calibración base cae en la trampa (r*=0)", _v_en_trampa),
        Verificacion("dinero impotente: +100 de M/P no mueve Y", _v_dinero_impotente),
        Verificacion("multiplicador fiscal pleno dentro de la trampa", _v_fiscal_pleno),
        Verificacion("salida fiscal: con G=200 se abandona la trampa", _v_salida_fiscal),
    ],
    notas="La trampa invierte el m11: monetaria impotente, fiscal a plena potencia.",
)
