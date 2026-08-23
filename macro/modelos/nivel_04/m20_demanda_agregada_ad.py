# m20_demanda_agregada_ad.py — curva AD derivada del IS-LM (nivel 4).
#
# La promesa pendiente de m18: la AD no se postula, se DERIVA. Con M nominal
# fija, un P mayor reduce los saldos reales M/P, desplaza la LM a la izquierda,
# sube r y deprime la inversión y el producto (efecto Keynes):
#   Y(P) = [F + (b/h)·(M/P)] / Ac ,  F = c0−c1·T+I0+G ,  Ac = (1−c1)+b·k/h
# Cada punto de la AD es un equilibrio IS-LM completo (verificable contra m10).
#
# Procedencia: derivación estándar de manuales de macro intermedia —
# conocimiento macroeconómico general, no verificado contra edición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_04 import _adas
import config


def _y_de_p(P, p, dG=None, dM=None):
    F, bh, Ac = _adas.estructura(p)
    F += p["dG"] if dG is None else dG
    M = p["M"] + (p["dM"] if dM is None else dM)
    return (F + bh * M / P) / Ac


def _curvas(p):
    P = np.linspace(1.0, 4.0, 200)
    base = _y_de_p(P, p, dG=0.0, dM=0.0)
    alt = _y_de_p(P, p)
    return {"lineas": {"AD base (de IS-LM)": (base, P, config.AZUL2),
                       "AD con shock ($dG,\\,dM$)": (alt, P, config.ROJO)},
            "anotacion": (f"$Y(P) = [F + (b/h)\\,M/P]\\,/\\,A_c$\n"
                          f"$Y$ en $P=2$: base $= {_y_de_p(2.0, p, 0.0, 0.0):,.1f}$, "
                          f"con shock $= {_y_de_p(2.0, p):,.1f}$\n"
                          "cada punto es un equilibrio IS-LM completo")}


def _resultados(p):
    F, bh, Ac = _adas.estructura(p)
    y2 = _y_de_p(2.0, p, 0.0, 0.0)
    return {"Y sobre la AD en P=1.5": _y_de_p(1.5, p, 0.0, 0.0),
            "Y sobre la AD en P=2": y2,
            "Y sobre la AD en P=3": _y_de_p(3.0, p, 0.0, 0.0),
            "dY/dP en P=2 (pendiente)": -bh * p["M"] / (Ac * 4.0),
            "desplazamiento fiscal dY|P (dG/Ac)": p["dG"] / Ac,
            "desplazamiento monetario dY|P=2": bh * p["dM"] / (Ac * 2.0),
            "r implícita en P=2 (del LM)": (p["k"] * y2 - p["M"] / 2.0) / p["h"]}


_P0 = {"dG": 50.0, "dM": 0.0, "c0": 100.0, "c1": 0.6, "I0": 150.0, "b": 20.0,
       "G": 200.0, "T": 100.0, "k": 0.5, "h": 10.0, "M": 600.0}


def _v_es_islm():
    # el punto de la AD en P=2 debe SER el equilibrio IS-LM de m10 con M/P=300
    y_ad = _y_de_p(2.0, _P0, 0.0, 0.0)
    p = _P0
    A = (1 - p["c1"]) + p["b"] * p["k"] / p["h"]
    B = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"] + p["b"] * (p["M"] / 2.0) / p["h"]
    return abs(y_ad - B / A) < 1e-9, ("el punto de la AD en P=2 es exactamente el equilibrio "
                                      f"IS-LM de m10 con M/P=300 (Y={y_ad:,.1f})")


def _v_pendiente_negativa():
    y_bajo, y_alto = _y_de_p(1.5, _P0, 0.0, 0.0), _y_de_p(3.0, _P0, 0.0, 0.0)
    return y_bajo > y_alto, (f"P↑ ⇒ M/P↓ ⇒ r↑ ⇒ Y↓ (efecto Keynes): "
                             f"Y({1.5})={y_bajo:,.0f} > Y(3)={y_alto:,.0f}")


def _v_desplazamiento_fiscal():
    F, bh, Ac = _adas.estructura(_P0)
    obs = _y_de_p(2.0, _P0, 50.0, 0.0) - _y_de_p(2.0, _P0, 0.0, 0.0)
    return abs(obs - 50.0 / Ac) < 1e-9, (f"a P fijo, dG=50 corre la AD {50 / Ac:,.1f} a la derecha "
                                         "(el multiplicador del IS-LM, m10)")


def _v_desplazamiento_monetario():
    F, bh, Ac = _adas.estructura(_P0)
    obs = _y_de_p(2.0, _P0, 0.0, 100.0) - _y_de_p(2.0, _P0, 0.0, 0.0)
    teo = bh * 100.0 / (Ac * 2.0)
    return abs(obs - teo) < 1e-9, f"a P=2, dM=100 corre la AD {teo:,.1f}: el dinero también desplaza AD"


MODELO = Modelo(
    id="m20", nivel=4,
    nombre="Demanda agregada (AD) derivada del IS-LM",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dG", _P0["dG"], -150, 150, 10, "Shock fiscal dG (desplaza AD)"),
        Parametro("dM", _P0["dM"], -200, 200, 10, "Shock monetario dM (desplaza AD)"),
        Parametro("M", _P0["M"], 300, 900, 10, "Dinero nominal M"),
        Parametro("G", _P0["G"], 0, 500, 10, "Gasto público G"),
        Parametro("T", _P0["T"], 0, 400, 10, "Impuestos T"),
        Parametro("c1", _P0["c1"], 0.1, 0.9, 0.05, "Propensión a consumir c1"),
        Parametro("b", _P0["b"], 5, 50, 1, "Sensibilidad de I a r (b)"),
        Parametro("k", _P0["k"], 0.1, 1.0, 0.05, "Demanda de dinero por Y (k)"),
        Parametro("h", _P0["h"], 2, 30, 1, "Demanda de dinero por r (h)"),
        Parametro("c0", _P0["c0"], 0, 300, 10, "Consumo autónomo c0"),
        Parametro("I0", _P0["I0"], 0, 400, 10, "Inversión autónoma I0"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta=("¿Por qué la demanda agregada cae cuando sube el nivel de precios, "
                  "si no es la demanda de un bien?"),
        contexto=("m18 usó una AD 'porque sí'; este modelo la construye. La pregunta "
                  "incómoda era: ¿por qué una demanda AGREGADA caería con el nivel de "
                  "precios, si no es la demanda de un bien? La síntesis respondió con "
                  "el efecto Keynes: P alto encoge el poder de compra del dinero, "
                  "encarece el crédito vía el mercado monetario y deprime la inversión. "
                  "La AD es el IS-LM barrido sobre P."),
        autores=("Síntesis neoclásica (sobre Hicks 1937); el canal de saldos reales es "
                 "el 'efecto Keynes'; el efecto riqueza directo del dinero es el "
                 "'efecto Pigou' (mención, no modelado aquí)."),
        supuestos=[
            "Todos los del IS-LM (m10), con M NOMINAL exógena y P ahora variable.",
            "El único canal P→Y es el de saldos reales (sin efecto riqueza Pigou ni canal de tipo de cambio).",
            "Expectativas de precios ausentes: P afecta por su NIVEL, no por su tasa de cambio (la inflación esperada llega en m52).",
        ],
        ecuaciones=[
            Ecuacion("Y(P) = \\frac{F + \\frac{b}{h}\\,\\frac{M}{P}}{A_c}, \\quad F = c_0 - c_1 T + I_0 + G",
                     "curva AD",
                     "el numerador es el gasto autónomo más el empuje monetario real; Ac=(1−c1)+bk/h "
                     "es el denominador del IS-LM (m10): la AD hereda TODA la estructura de los niveles 1-2."),
            Ecuacion("\\frac{dY}{dP} = -\\frac{b\\,M}{h\\,A_c\\,P^2} < 0", "pendiente (efecto Keynes)",
                     "P↑ → M/P↓ → LM a la izquierda → r↑ → I↓ → Y↓. No es la ley de demanda de un "
                     "bien: es política monetaria implícita hecha por los precios."),
            Ecuacion("\\Delta Y\\big|_P = \\frac{dG}{A_c} \\;;\\; \\frac{b}{h}\\,\\frac{dM}{P\\,A_c}",
                     "desplazamientos",
                     "lo fiscal y lo monetario mueven la MISMA curva: sobre el plano (Y,P) ambas son "
                     "políticas 'de demanda' — la distinción reaparecerá en sus efectos sobre r."),
        ],
        intuicion=("Leer la AD como un resumen: detrás de cada punto hay un mercado de "
                   "bienes y uno de dinero equilibrándose (verificado contra m10). Por "
                   "eso 'moverse sobre la AD' significa dejar que P haga política "
                   "monetaria contractiva, y 'desplazar la AD' significa hacerla por "
                   "decisión (dG, dM)."),
        equilibrio=("La AD sola no fija nada (¿cuál P?): necesita la oferta agregada. "
                    "m21-m22 construyen las dos ofertas y m23 cierra el sistema."),
        limitaciones=[
            "Con deflación el efecto Keynes puede fallar: expectativas deflacionarias suben la tasa real (la crítica de la deuda-deflación de Fisher, m94).",
            "En el piso r=0 la AD se vuelve vertical/perversa (la trampa m12 reaparece en el plano (Y,P) — literatura ZLB, nivel 8).",
            "M exógena: con bancos centrales que fijan r, la 'AD moderna' se deriva de IS-MP (m51).",
        ],
        evolucion=("Con la AD derivada, m21 (SRAS) y m22 (LRAS) completan las piezas y "
                   "m23 arma el modelo AD-AS completo — el aparato gráfico dominante "
                   "de la macro de manual hasta hoy."),
    ),
    escenarios=[
        Escenario("expansion_fiscal", "dG = +100 (desplaza AD a la derecha)",
                  {"dG": 100.0, "dM": 0.0},
                  "a cada nivel de precios, el equilibrio IS-LM subyacente tiene más "
                  "producto: la AD entera se corre dG/Ac = 71.",
                  cadena=["↑dG", "a cada P, el IS-LM subyacente rinde más Y",
                          "AD → derecha en dG/Ac", "cuánto va a P lo dirá la oferta (m23)"]),
        Escenario("expansion_monetaria", "dM = +100 con dG = 0",
                  {"dG": 0.0, "dM": 100.0},
                  "más dinero nominal sostiene más saldos reales a cada P: la AD se "
                  "corre a la derecha — más en los P bajos (el shift depende de 1/P).",
                  cadena=["↑dM", "↑M/P a cada nivel de precios", "↓r ⇒ ↑I (IS-LM subyacente)",
                          "AD → derecha en (b/h)dM/(P·Ac)"]),
        Escenario("dinero_escaso", "contracción monetaria dM = −150",
                  {"dG": 0.0, "dM": -150.0},
                  "la AD a la izquierda: el mismo P sostiene menos actividad — la "
                  "receta desinflacionaria que m23 evaluará contra la SRAS.",
                  cadena=["↓dM", "↓M/P a cada P", "↑r ⇒ ↓I", "AD → izquierda"]),
    ],
    verificaciones=[
        Verificacion("cada punto de la AD es un IS-LM (P=2 ≡ m10)", _v_es_islm),
        Verificacion("pendiente negativa (efecto Keynes)", _v_pendiente_negativa),
        Verificacion("desplazamiento fiscal = dG/Ac", _v_desplazamiento_fiscal),
        Verificacion("desplazamiento monetario = (b/h)dM/(P·Ac)", _v_desplazamiento_monetario),
    ],
    notas="La AD que m18 postuló, ahora derivada: detrás de cada punto vive un IS-LM completo.",
)
