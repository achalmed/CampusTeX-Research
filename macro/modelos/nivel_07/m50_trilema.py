"""simuladores/macro/modelos/nivel_07/m50_trilema.py — el trilema macroeconómico (nivel 7, cierre).

De los tres deseos — tipo de cambio FIJO, libre MOVILIDAD de capitales y
política monetaria AUTÓNOMA (i propia) — solo se pueden tener DOS. El
tercero se cobra en reservas: si el país fija E, abre la cuenta de
capitales Y mantiene i ≠ i*, el arbitraje de m48 drena las RIN a razón
  fuga por período = κ · movilidad · (i − i*)     [si i > i*: salida]
  T* = RIN0 / fuga    — la paridad tiene fecha de caducidad exacta.
Los tres vértices históricos: patrón oro (fijo+movilidad, sin autonomía),
Bretton Woods (fijo+autonomía, con controles), flotación con metas
(autonomía+movilidad — la esquina peruana moderna). Menciones.

Procedencia: trilema de Mundell-Fleming; formulación histórica moderna:
Obstfeld-Taylor (mención) — conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _fuga(p):
    if p["fijo"] < 0.5:
        return 0.0
    return p["kappa"] * p["movilidad"] * (p["i"] - p["i_star"])


def _rin(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    return t, np.maximum(0.0, p["RIN0"] - _fuga(p) * t)


def _vertices(p):
    eleccion = []
    eleccion.append("fijo" if p["fijo"] >= 0.5 else "FLOTA")
    eleccion.append("movilidad" if p["movilidad"] > 0.5 else "CONTROLES")
    eleccion.append("autonomía" if abs(p["i"] - p["i_star"]) > 1e-9 else "i = i*")
    return " + ".join(eleccion)


def _curvas(p):
    t, rin = _rin(p)
    f = _fuga(p)
    ts = (p["RIN0"] / f) if f > 1e-12 else float("inf")
    return {"lineas": {"reservas internacionales $RIN_t$": (t, rin, config.AZUL2),
                       "sin reservas (colapso de la paridad)": (t, np.zeros_like(rin), config.ROJO)},
            "anotacion": (f"elección: {_vertices(p)}\n"
                          f"fuga por período = $\\kappa \\cdot mov \\cdot (i-i^*)$ = {f:,.1f}\n"
                          + (f"colapso en $T^* = {ts:,.1f}$ períodos" if np.isfinite(ts)
                             else "sin fuga: la elección es consistente"))}


def _resultados(p):
    f = _fuga(p)
    t, rin = _rin(p)
    ts = (p["RIN0"] / f) if f > 1e-12 else float("inf")
    return {"fuga de reservas por período": f,
            "T* (períodos hasta el colapso)": ts if np.isfinite(ts) else 9999.0,
            f"RIN en t={int(p['T'])}": float(rin[-1]),
            "autonomía ejercida i−i* (pp)": p["i"] - p["i_star"],
            "vértices (1 = trío imposible)":
                1.0 if (p["fijo"] >= 0.5 and p["movilidad"] > 0.5
                        and abs(p["i"] - p["i_star"]) > 1e-9) else 0.0}


def _ecuaciones_calibradas(p):
    f = _fuga(p)
    return [f"$fuga = {p['kappa']:.0f} \\times {p['movilidad']:.2f} \\times "
            f"({p['i']:.1f}-{p['i_star']:.1f}) = {f:,.1f}$",
            (f"$T^* = {p['RIN0']:.0f}/{f:,.1f} = {p['RIN0'] / f:,.1f}$" if f > 1e-12
             else "$T^* = \\infty$")]


_P0 = {"i": 5.0, "i_star": 3.0, "fijo": 1.0, "movilidad": 1.0,
       "kappa": 25.0, "RIN0": 200.0, "T": 12.0}


def _v_reloj_exacto():
    f = _fuga(_P0)
    ts_teo = _P0["RIN0"] / f
    t, rin = _rin(_P0, T=40)
    ts_sim = float(t[int(np.argmax(rin <= 0))])
    return abs(ts_sim - np.ceil(ts_teo)) < 1e-9, \
        (f"las RIN llegan a cero exactamente en ⌈T*⌉ = {ts_sim:.0f} períodos "
         f"(T* = RIN0/fuga = {ts_teo:.1f}): la paridad insostenible tiene reloj")


def _v_flotar_libera():
    p = dict(_P0, fijo=0.0)
    _, rin = _rin(p, T=40)
    return bool(np.all(np.abs(rin - _P0["RIN0"]) < 1e-12)), \
        ("al flotar, las RIN quedan intactas con i propia y movilidad plena: "
         "se sacrifica el fijo y se conservan los otros dos vértices (la esquina peruana)")


def _v_controles_compran_tiempo():
    ts0 = _P0["RIN0"] / _fuga(_P0)
    ts1 = _P0["RIN0"] / _fuga(dict(_P0, movilidad=0.1))
    return abs(ts1 / ts0 - 10.0) < 1e-9, \
        (f"con controles (movilidad 1.0→0.1) el colapso se aleja exactamente ×10 "
         f"({ts0:.0f} → {ts1:.0f} períodos): Bretton Woods compraba tiempo con controles")


def _v_renunciar_autonomia():
    f = _fuga(dict(_P0, i=_P0["i_star"]))
    return abs(f) < 1e-12, ("con i = i* la fuga es cero y el fijo es sostenible: "
                            "renunciar a la autonomía (patrón oro / caja de convertibilidad)")


MODELO = Modelo(
    id="m50", nivel=7,
    nombre="Trilema macroeconómico",
    xlabel="Período $t$", ylabel="Reservas internacionales ($RIN$)",
    parametros=[
        Parametro("fijo", _P0["fijo"], 0, 1, 1, "¿Tipo de cambio fijo? (1 sí, 0 flota)",
                  grupo="elección", definicion="el primer vértice"),
        Parametro("movilidad", _P0["movilidad"], 0.0, 1.0, 0.05, "Movilidad de capitales",
                  grupo="elección", definicion="1 = cuenta abierta; <1 = controles"),
        Parametro("i", _P0["i"], 1, 9, 0.25, "Tasa propia i (%)", grupo="elección",
                  definicion="autonomía: i ≠ i* es querer política propia"),
        Parametro("i_star", _P0["i_star"], 1, 7, 0.25, "Tasa mundial i* (%)", grupo="mundo"),
        Parametro("RIN0", _P0["RIN0"], 50, 500, 25, "Reservas iniciales RIN0", grupo="municiones"),
        Parametro("kappa", _P0["kappa"], 5, 60, 5, "Velocidad del arbitraje κ", grupo="mundo",
                  definicion="cuánto capital se mueve por punto de diferencial"),
        Parametro("T", _P0["T"], 6, 30, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Fijo, movilidad y tasa propia: ¿por qué solo se pueden tener dos — y cuál descartó cada época?",
        variables=[("RIN_t", "las reservas — el combustible del vértice de más"),
                   ("fijo, movilidad, i", "los tres deseos — elige dos"),
                   ("T*", "el reloj — cuándo la incoherencia pasa la factura")],
        derivacion=["m48: \\;i \\ne i^*\\;con\\;E\\;fijo\\;y\\;movilidad \\Rightarrow arbitraje",
                    "fuga = \\kappa \\cdot mov \\cdot (i - i^*)",
                    "T^* = \\frac{RIN_0}{fuga} \\;\\;(la\\;paridad\\;tiene\\;fecha)"],
        contexto=("Es el corolario más citado del Mundell-Fleming: la trinidad "
                  "imposible. La historia monetaria del siglo XX se deja leer como "
                  "un paseo por sus vértices (Obstfeld-Taylor, mención): el patrón "
                  "oro fijó y abrió la cuenta — renunciando a política propia; "
                  "Bretton Woods quiso fijo Y autonomía — a punta de controles de "
                  "capital; la era moderna abrió los capitales y flotó — la esquina "
                  "del Perú con metas de inflación y flotación administrada "
                  "(mención). Cada crisis cambiaria (m74) es, en el fondo, un país "
                  "intentando el trío completo."),
        autores=("Corolario de Mundell (años 60); lectura histórica: Obstfeld y "
                 "Taylor (mención); versión 'dilema' con ciclos financieros "
                 "globales: Rey (mención)."),
        supuestos=[
            "El arbitraje de m48 opera a velocidad κ finita: la fuga es flujo por período, no salto instantáneo (didáctico).",
            "El BC defiende la paridad vendiendo RIN sin subir i (si sube i, renuncia a la autonomía: otro vértice).",
            "Las RIN no se piden prestadas ni hay rescates (FMI como mención): el reloj corre solo.",
        ],
        ecuaciones=[
            Ecuacion("fuga = \\kappa \\cdot mov \\cdot (i - i^*)", "el costo del tercer deseo",
                     "cada punto de tasa propia, con cuenta abierta y E fijo, es capital que sale "
                     "— y reservas que el BC quema para sostener la paridad."),
            Ecuacion("T^* = RIN_0 / fuga", "el reloj de la paridad",
                     "aritmética de primera generación (Krugman 1979, mención): el mercado VE "
                     "este reloj — y en m74 lo adelantará con un ataque especulativo."),
        ],
        intuicion=("El trilema es una ley de conservación institucional: la "
                   "incoherencia no se prohíbe, se FINANCIA — con reservas, y por "
                   "tiempo T* calculable. De ahí las tres salidas honestas: flotar "
                   "(que el precio absorba, m49-flexible), cerrar la cuenta "
                   "(que el capital no arbitre, con sus costos), o alinear la tasa "
                   "(que no haya nada que arbitrar). Todo lo demás es elegir la "
                   "fecha del colapso."),
        equilibrio=("Consistente en cualquier PAR de vértices (fuga = 0, verificado "
                    "en flotación y en i=i*); inconsistente con los tres (RIN→0 en "
                    "T* exacto, verificado). No hay equilibrio con trío: hay cuenta "
                    "regresiva."),
        limitaciones=[
            "Lineal y determinista: el mercado real ANTICIPA T* y ataca antes (m74, primera generación) — este reloj es la cota optimista.",
            "El 'dilema' de Rey (mención): con ciclos financieros globales, ni flotar da autonomía plena — la movilidad manda más de lo que el trilema clásico admite.",
            "Controles de capital sin costos: en la práctica filtran, distorsionan y envejecen mal (mención).",
        ],
        evolucion=("Cierra el nivel 7 condensando m43-m49 en una sola restricción "
                   "institucional. El nivel 10 lo dramatiza: la crisis cambiaria "
                   "(m74) es este reloj con expectativas (el ataque llega ANTES de "
                   "T*), y el sudden stop (m75) es la movilidad cambiando de signo. "
                   "El Perú moderno — flotación administrada, metas, RIN altas — es "
                   "la esquina autonomía+movilidad con colchón (m110-m111)."),
    ),
    escenarios=[
        Escenario("trio_imposible", "fijo + cuenta abierta + tasa propia (i=5 vs i*=3)",
                  {"fijo": 1.0, "movilidad": 1.0, "i": 5.0},
                  "las RIN caen 50 por período y la paridad muere en T*=4: el trío "
                  "completo no es una opción — es una cuenta regresiva.",
                  cadena=["i > i* con E fijo y cuenta abierta", "arbitraje de m48",
                          "salida de capital sostenida", "el BC vende RIN para defender Ē",
                          "RIN → 0 en T* = RIN0/fuga", "colapso o ajuste (m74)"]),
        Escenario("controles_de_capital", "Bretton Woods: movilidad recortada a 0.1",
                  {"movilidad": 0.1},
                  "el colapso se aleja de 4 a 40 períodos: los controles COMPRAN "
                  "tiempo para tener fijo + autonomía — el mundo de 1950-1971.",
                  cadena=["controles a la cuenta de capitales", "el arbitraje se estrangula",
                          "fuga ×0.1", "T* ×10", "fijo y autonomía conviven… mientras los controles aguanten"]),
        Escenario("flotar", "la esquina moderna: se suelta la paridad",
                  {"fijo": 0.0},
                  "RIN intactas con tasa propia y cuenta abierta: E absorbe el "
                  "diferencial (m49-flexible) — la elección peruana con metas (m40).",
                  cadena=["se abandona el fijo", "E flota y absorbe el arbitraje",
                          "las RIN dejan de sangrar", "la tasa queda libre para m38",
                          "autonomía + movilidad: la esquina del BCRP"]),
        Escenario("renunciar_a_la_tasa", "patrón oro: i se alinea con i*",
                  {"i": 3.0},
                  "fuga cero con fijo y cuenta abierta: la paridad es eterna… al "
                  "precio de importar la política monetaria del mundo.",
                  cadena=["i = i*", "no hay diferencial que arbitrar", "fuga = 0",
                          "el fijo se sostiene solo", "la política monetaria es la del ancla (m86 en fijo)"]),
    ],
    verificaciones=[
        Verificacion("el reloj: RIN=0 exactamente en ⌈T*⌉", _v_reloj_exacto),
        Verificacion("flotar libera: RIN constantes", _v_flotar_libera),
        Verificacion("controles escalan T* linealmente (×10)", _v_controles_compran_tiempo),
        Verificacion("i = i* ⇒ fuga cero (paridad sostenible)", _v_renunciar_autonomia),
    ],
    notas="La trinidad imposible: la incoherencia no se prohíbe — se financia, y por T* períodos exactos.",
)
