"""simuladores/macro/modelos/nivel_02/m11_efecto_expulsion.py — efecto expulsión (crowding out) — nivel 2.

Descompone qué pasa con un impulso fiscal ΔG dentro del IS-LM (m10):
  ΔY_simple = k·ΔG                 (nivel 1: sin respuesta de r)
  ΔY_ISLM   = ΔG / A,  A = (1−c1) + b·k/h
  Δr = k·ΔY/h  →  ΔI = −b·Δr      (inversión expulsada)
Identidad de cierre (verificable):  ΔY_ISLM = k_simple · (ΔG + ΔI)
Grado de expulsión = −ΔI/ΔG ∈ [0,1]; sus límites son teoría pura:
  h→∞ (LM plana):  Δr=0, expulsión nula, ΔY→k·ΔG (mundo keynesiano extremo)
  h→0 (LM vertical): ΔY→0, ΔI→−ΔG (expulsión total: mundo "clásico")

Procedencia: análisis estándar del IS-LM (manuales) y debate
keynesianos-monetaristas — conocimiento general, no verificado contra edición.
"""

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _efectos(p):
    k_simple = 1 / (1 - p["c1"])
    A = (1 - p["c1"]) + p["b"] * p["k"] / p["h"]
    dY = (p["dG"] + p["b"] * p["dMP"] / p["h"]) / A
    dr = (p["k"] * dY - p["dMP"]) / p["h"]
    dI = -p["b"] * dr
    return {"k_simple": k_simple, "dY_simple": k_simple * p["dG"],
            "dY": dY, "dr": dr, "dI": dI,
            "grado": -dI / p["dG"] if p["dG"] else 0.0}


def _curvas(p):
    e = _efectos(p)
    cats = ["$k\\,\\Delta G$\n(nivel 1)", "$\\Delta Y$ efectivo\n(IS-LM)", "$\\Delta I$\n(expulsada)"]
    vals = [e["dY_simple"], e["dY"], e["dI"]]
    cols = [config.GRIS, config.AZUL2, config.ROJO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$\\Delta r = {e['dr']:+.2f}$ pp\n"
                          f"grado de expulsión $= {100 * e['grado']:.0f}\\%$\n"
                          f"identidad: $\\Delta Y = k(\\Delta G+\\Delta I) = "
                          f"{e['k_simple'] * (p['dG'] + e['dI']):,.1f}$")}


def _resultados(p):
    e = _efectos(p)
    return {"ΔY sin respuesta de r (k·ΔG)": e["dY_simple"],
            "ΔY efectivo (IS-LM)": e["dY"],
            "Δr (puntos)": e["dr"],
            "ΔI (inversión expulsada)": e["dI"],
            "grado de expulsión −ΔI/ΔG (%)": 100 * e["grado"],
            "identidad k·(ΔG+ΔI)": e["k_simple"] * (p["dG"] + e["dI"])}


_P0 = {"dG": 100.0, "dMP": 0.0, "c1": 0.6, "b": 20.0, "k": 0.5, "h": 10.0}


def _v_identidad():
    e = _efectos(_P0)
    lhs, rhs = e["dY"], e["k_simple"] * (_P0["dG"] + e["dI"])
    return abs(lhs - rhs) < 1e-9, ("ΔY = k_simple·(ΔG + ΔI): el impulso neto (gasto público "
                                   "menos inversión expulsada) se multiplica como en m04")


def _v_limite_keynesiano():
    e = _efectos(dict(_P0, h=1e9))
    return abs(e["dY"] - e["dY_simple"]) < 1e-3, ("con LM plana (h→∞): Δr≈0 y ΔY→k·ΔG — "
                                                  "el multiplicador pleno del nivel 1")


def _v_limite_clasico():
    e = _efectos(dict(_P0, h=1e-9))
    ok = abs(e["dY"]) < 1e-3 and abs(e["dI"] + _P0["dG"]) < 1e-3
    return ok, "con LM vertical (h→0): ΔY→0 y ΔI→−ΔG — expulsión total, el gasto solo desplaza"


def _v_acomodo():
    e = _efectos(dict(_P0, dMP=125.0))
    ok = abs(e["dr"]) < 1e-9 and abs(e["dY"] - e["dY_simple"]) < 1e-9
    return ok, ("con acomodo monetario dMP=k·k_simple·ΔG·…=125: Δr=0 exacto y ΔY=k·ΔG — "
                "financiar el impulso evita la expulsión (a costa de emitir)")


MODELO = Modelo(
    id="m11", nivel=2,
    nombre="Efecto expulsión (crowding out)",
    xlabel="", ylabel="Variación (unidades monetarias)",
    parametros=[
        Parametro("dG", _P0["dG"], 10, 200, 10, "Impulso fiscal ΔG"),
        Parametro("dMP", _P0["dMP"], 0, 200, 5, "Acomodo monetario dMP (0 = sin acomodo)"),
        Parametro("c1", _P0["c1"], 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 5, 50, 1, "Sensibilidad de I a r (b)"),
        Parametro("k", _P0["k"], 0.1, 1.0, 0.05, "Demanda de dinero por Y (k)"),
        Parametro("h", _P0["h"], 0.5, 30, 0.5, "Demanda de dinero por r (h)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Cuánto del impulso fiscal se pierde porque la tasa de interés "
                  "expulsa inversión privada?"),
        contexto=("¿El gasto público crea demanda o solo desplaza a la privada? La "
                  "'Treasury view' británica de los años 20 sostenía que cada libra "
                  "gastada por el Estado era una libra menos de inversión privada; Keynes "
                  "respondió que con desempleo el gasto crea ingreso nuevo. El IS-LM "
                  "arbitra el debate: ambos tienen razón, en distintos supuestos sobre el "
                  "mercado de dinero — y esa fue exactamente la trinchera del debate "
                  "keynesianos-monetaristas de los años 60-70."),
        autores=("Análisis canónico del IS-LM (síntesis neoclásica); el debate empírico "
                 "clásico: Friedman y los monetaristas (LM empinada) contra los "
                 "keynesianos de la síntesis (LM plana)."),
        supuestos=[
            "Todos los del IS-LM (m10): precios fijos, economía cerrada, M exógena.",
            "El impulso ΔG no se financia con impuestos corrientes (déficit): el canal es solo la tasa de interés.",
            "Sin expectativas: nadie anticipa impuestos futuros (esa crítica es la equivalencia ricardiana, m67).",
        ],
        ecuaciones=[
            Ecuacion("\\Delta Y = \\frac{\\Delta G}{(1-c_1) + b\\,k/h}", "efecto fiscal en IS-LM",
                     "el denominador suma la filtración por ahorro (1−c1) y la filtración NUEVA por "
                     "tasa de interés (bk/h): el ingreso extra demanda dinero, sube r y descarta inversión."),
            Ecuacion("\\Delta I = -b\\,\\Delta r = -b\\,\\frac{k\\,\\Delta Y}{h}", "inversión expulsada",
                     "la cadena completa: ΔG → ΔY → ΔL → Δr → ΔI<0."),
            Ecuacion("\\Delta Y = \\frac{1}{1-c_1}\\,(\\Delta G + \\Delta I)", "identidad de cierre",
                     "el multiplicador simple sigue operando — pero sobre el impulso NETO de la "
                     "expulsión. El nivel 1 no estaba mal: estaba incompleto."),
        ],
        intuicion=("La expulsión no es un 'fracaso' de la política fiscal sino su costo "
                   "de financiamiento implícito: sin dinero nuevo, el ingreso adicional "
                   "compite por la misma liquidez y el crédito se encarece. El grado de "
                   "expulsión lo deciden dos pendientes: cuán sensible es la inversión a "
                   "r (b) y cuán sensible es la demanda de dinero a r (h)."),
        equilibrio=("Estática comparativa entre dos equilibrios IS-LM. Los límites h→∞ "
                    "(expulsión nula) y h→0 (expulsión total) reproducen el mundo "
                    "keynesiano extremo y el mundo clásico como casos particulares del "
                    "mismo aparato."),
        limitaciones=[
            "En recesión profunda (r≈0) la expulsión desaparece — pero eso es la trampa de liquidez (m12), no este modelo.",
            "En economía abierta con cambio flexible la expulsión opera vía apreciación cambiaria, no (solo) vía r (m49).",
            "Con expectativas racionales y hogares previsores, el canal ricardiano (m67) puede expulsar consumo además de inversión.",
            "Empíricamente el grado de expulsión depende del régimen (normal vs ZLB): los multiplicadores medidos varían (m70).",
        ],
        evolucion=("Es la primera 'guerra de pendientes' del currículo: monetaristas y "
                   "keynesianos discutían h y b con este mismo diagrama. El caso límite "
                   "opuesto (LM plana) es m12; la versión en economía abierta es m49; "
                   "la evidencia empírica moderna sobre multiplicadores es m70."),
    ),
    escenarios=[
        Escenario("mundo_monetarista", "demanda de dinero insensible a r (h = 2)",
                  {"h": 2.0},
                  "LM casi vertical: el 93% del impulso se expulsa — el gasto público "
                  "'solo mueve la composición, no el nivel' (posición monetarista).",
                  cadena=["h pequeño ⇒ LM casi vertical", "↑G", "fuerte ↑r", "↓↓I",
                          "expulsión ≈ total"]),
        Escenario("mundo_keynesiano", "dinero muy sensible a r y poca b (h=30, b=5)",
                  {"h": 30.0, "b": 5.0},
                  "LM plana e inversión insensible: expulsión de un dígito — el gasto "
                  "rinde casi el multiplicador pleno (posición keynesiana).",
                  cadena=["h grande, b chico ⇒ LM plana", "↑G", "r casi no sube",
                          "I casi intacta", "expulsión mínima", "k casi pleno"]),
        Escenario("acomodo_monetario", "el banco central emite dMP=125 junto al impulso",
                  {"dMP": 125.0},
                  "Δr = 0 exacto: la 'monetización' del impulso recupera el multiplicador "
                  "del nivel 1 — con la semilla inflacionaria que el nivel 3 cobrará.",
                  cadena=["↑G + emisión calibrada dMP", "la mayor demanda de dinero se abastece",
                          "Δr = 0 exacto", "sin expulsión", "ΔY = k·ΔG (m04)"]),
    ],
    verificaciones=[
        Verificacion("identidad ΔY = k·(ΔG+ΔI)", _v_identidad),
        Verificacion("límite keynesiano (h→∞): expulsión nula", _v_limite_keynesiano),
        Verificacion("límite clásico (h→0): expulsión total", _v_limite_clasico),
        Verificacion("acomodo monetario: Δr=0 y multiplicador pleno", _v_acomodo),
    ],
    notas="El debate keynesianos-monetaristas fue, en buena parte, una discusión sobre h y b.",
)
