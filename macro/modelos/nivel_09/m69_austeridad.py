# m69_austeridad.py — austeridad: la aritmética del denominador (nivel 9).
#
# Un ajuste primario dA (% del PIB) busca bajar la deuda/PIB… pero el ajuste
# CONTRAE el denominador vía el multiplicador (m60/m70):
#   b₁ = (b₀ − dA) / (1 − mult·dA/100)
# El numerador baja dA; el denominador baja mult·dA%. ¿Quién gana?
#   multiplicador crítico:  mult* = 100/b₀   (exacto, independiente de dA)
#   mult < mult*: la austeridad FUNCIONA (b cae)
#   mult > mult*: la PARADOJA — ajustar SUBE el ratio (autodestructiva)
# Con b₀=120% basta mult>0.83 (el de una recesión, m70) para la paradoja;
# con b₀=40% haría falta mult>2.5 (casi imposible). El debate post-2010
# (Alesina vs Blanchard-Leigh, menciones) fue exactamente esta ecuación.
#
# Procedencia: aritmética del ratio (decisión de diseño sobre m64/m60);
# debate: Alesina-Ardagna vs Blanchard y Leigh (2013) — menciones.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _b1(p, mult=None):
    mult = p["mult"] if mult is None else mult
    return (p["b0"] - p["dA"]) / (1 - mult * p["dA"] / 100)


def _mult_critico(p):
    return 100 / p["b0"]


def _curvas(p):
    m = np.linspace(0, 2.5, 200)
    b1 = (p["b0"] - p["dA"]) / (1 - m * p["dA"] / 100)
    mc = _mult_critico(p)
    return {"lineas": {"deuda tras el ajuste $b_1(mult)$": (m, b1, config.AZUL2),
                       "deuda inicial $b_0$": (m, np.full_like(m, p["b0"]), config.GRIS)},
            "equilibrio": (p["mult"], float(_b1(p))),
            "puntos": [(mc, p["b0"], f"crítico: $mult^* = 100/b_0 = {mc:.2f}$")],
            "anotacion": (f"ajuste dA = {p['dA']:.1f}% del PIB con mult = {p['mult']:.2f}\n"
                          f"$b_1 = ({p['b0']:.0f}-{p['dA']:.1f})/(1-{p['mult'] * p['dA'] / 100:.3f}) "
                          f"= {float(_b1(p)):.1f}\\%$\n"
                          + ("la austeridad FUNCIONA (mult < mult*)" if p["mult"] < mc
                             else "PARADOJA: el ajuste SUBIÓ el ratio"))}


def _resultados(p):
    return {"deuda/PIB tras el ajuste b1 (%)": float(_b1(p)),
            "cambio del ratio (pp)": float(_b1(p)) - p["b0"],
            "multiplicador crítico 100/b0": _mult_critico(p),
            "caída del PIB (%)": p["mult"] * p["dA"],
            "ahorro fiscal directo (pp de b)": p["dA"]}


def _ecuaciones_calibradas(p):
    return [f"$b_1 = \\frac{{{p['b0']:.0f} - {p['dA']:.1f}}}{{1 - {p['mult']:.2f}\\times"
            f"{p['dA']:.1f}/100}} = {float(_b1(p)):.1f}$",
            f"$mult^* = 100/{p['b0']:.0f} = {_mult_critico(p):.2f}$"]


_P0 = {"b0": 120.0, "dA": 2.0, "mult": 1.2}


def _v_critico_exacto():
    mc = _mult_critico(_P0)
    return abs(float(_b1(_P0, mult=mc)) - _P0["b0"]) < 1e-9, \
        (f"en mult* = 100/b0 = {mc:.3f}, el ajuste deja b EXACTAMENTE donde estaba: "
         "numerador y denominador se anulan — y mult* no depende del tamaño del ajuste")


def _v_paradoja():
    b1 = float(_b1(_P0))
    return b1 > _P0["b0"], \
        (f"con b0=120% y mult=1.2 (recesión), ajustar 2% del PIB SUBE el ratio a "
         f"{b1:.1f}%: la austeridad autodestructiva — el denominador perdió más que el numerador")


def _v_funciona_con_mult_bajo():
    b1 = float(_b1(dict(_P0, mult=0.5)))
    return b1 < _P0["b0"], \
        (f"el MISMO ajuste con mult=0.5 (expansión, BC acomodando) baja b a {b1:.1f}%: "
         "no es la austeridad — es el CUÁNDO")


def _v_deuda_baja_inmune():
    p = dict(_P0, b0=40.0)
    mc = _mult_critico(p)
    b1 = float(_b1(p, mult=1.2))
    return mc > 2 and b1 < p["b0"], \
        (f"con b0=40%, el crítico es {mc:.1f} (inalcanzable) y el mismo ajuste en recesión "
         f"SÍ baja b: la paradoja es un privilegio de los sobre-endeudados")


MODELO = Modelo(
    id="m69", nivel=9,
    nombre="Austeridad (la aritmética del denominador)",
    xlabel="Multiplicador fiscal vigente", ylabel="Deuda/PIB tras el ajuste (%)",
    parametros=[
        Parametro("mult", _P0["mult"], 0.1, 2.5, 0.05, "Multiplicador vigente (m60/m70)", grupo="régimen",
                  definicion="alto en recesión/ZLB, bajo en expansión: el CUÁNDO"),
        Parametro("b0", _P0["b0"], 20, 180, 5, "Deuda/PIB inicial b0 (%)", grupo="posición",
                  definicion="fija el crítico: mult* = 100/b0"),
        Parametro("dA", _P0["dA"], 0.5, 5, 0.25, "Ajuste primario dA (% del PIB)", grupo="decisión"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Puede el ajuste fiscal SUBIR la deuda/PIB — y qué decide si la austeridad sana o se muerde la cola?",
        variables=[("b1", "el ratio tras el ajuste — numerador Y denominador se mueven"),
                   ("mult", "el multiplicador VIGENTE — el régimen de m60/m70"),
                   ("mult* = 100/b0", "la frontera — elegante, exacta e independiente de dA")],
        derivacion=["numerador: \\;B/Y_0 \\to (b_0 - dA)",
                    "denominador: \\;Y_0 \\to Y_0\\,(1 - mult\\cdot dA/100)",
                    "b_1 = \\frac{b_0 - dA}{1 - mult\\,dA/100}; \\quad b_1 = b_0 \\iff mult^* = \\frac{100}{b_0}"],
        contexto=("Tras 2010, Europa ajustó en plena recesión con la promesa de la "
                  "'austeridad expansiva' (Alesina-Ardagna, mención). Blanchard y "
                  "Leigh (2013, mención) midieron el error: los multiplicadores "
                  "vigentes eran mucho mayores que los supuestos (ZLB, m70), y en "
                  "varios países el ratio deuda/PIB SUBIÓ tras el ajuste — Grecia "
                  "como caso extremo (mención). La ecuación de este modelo es ese "
                  "debate entero: no discute SI ajustar sino CUÁNDO, porque el "
                  "multiplicador — que depende del régimen (m60) y del momento "
                  "(m70) — decide de qué lado de mult*=100/b0 se cae."),
        autores=("Debate: Alesina y Ardagna (austeridad expansiva) vs Blanchard y "
                 "Leigh (2013, el error de pronóstico de los multiplicadores) — "
                 "menciones; la aritmética del ratio es álgebra de m64."),
        supuestos=[
            "Efecto de una vez sobre el PIB (mult·dA) sin dinámica posterior: la versión completa añade la persistencia de m61 y la reacción de r (m65).",
            "El multiplicador es EXÓGENO al ajuste: en realidad depende del estado que el propio ajuste empeora — la paradoja puede autoalimentarse.",
            "Sin efecto confianza: el canal 'austeridad baja la prima r' (el argumento de Alesina) actuaría vía m65 — aquí se aísla el denominador.",
        ],
        ecuaciones=[
            Ecuacion("b_1 = \\frac{b_0 - dA}{1 - mult\\,dA/100}", "la doble contracción",
                     "el ajuste resta arriba (menos deuda) y resta abajo (menos PIB): el ratio — "
                     "que es lo que los mercados miran (m65) — puede ir en cualquier dirección."),
            Ecuacion("mult^* = \\frac{100}{b_0}", "la frontera de la paradoja",
                     "exacta e independiente del tamaño del ajuste: con deuda de 120%, cualquier "
                     "multiplicador sobre 0.83 vuelve el ajuste contraproducente."),
        ],
        intuicion=("La austeridad es una dieta medida en un espejo que se encoge: "
                   "si el cuerpo (PIB) se contrae más rápido que el peso (deuda), "
                   "la báscula relativa EMPEORA. La frontera 100/b0 da la regla "
                   "práctica: los países poco endeudados casi no pueden fallar "
                   "(mult*>2.5); los sobre-endeudados casi no pueden acertar en "
                   "recesión (mult*<1 y el multiplicador recesivo es ≥1, m70). "
                   "Corolario de m68: el momento de ajustar era el boom — la "
                   "austeridad de recesión es el castigo por la prociclicidad."),
        equilibrio=("Estática comparativa exacta: mult* verificado como cruce; los "
                    "cuatro cuadrantes (deuda alta/baja × mult alto/bajo) quedan "
                    "cubiertos por las verificaciones."),
        limitaciones=[
            "Un período: los efectos de mediano plazo (histéresis del PIB, caída de la prima) pueden revertir el veredicto en ambas direcciones (menciones).",
            "La composición importa y aquí no está: recortar inversión vs gasto corriente vs subir impuestos tienen multiplicadores distintos (m70).",
            "El canal confianza→prima (m65) puede rescatar ajustes 'paradójicos' si el default estaba cerca: Grecia y el contrafactual imposible (mención).",
        ],
        evolucion=("Es el m68 leído al revés: quien no ahorró el boom termina "
                   "ajustando en la recesión, del lado malo de mult*. El juicio "
                   "empírico sobre los multiplicadores por estado — la pieza que "
                   "cierra el argumento — es m70."),
    ),
    escenarios=[
        Escenario("paradoja_griega", "b0=160%, ajuste en recesión (mult=1.4)",
                  {"b0": 160.0, "mult": 1.4},
                  "el crítico es 0.63 y el multiplicador 1.4: cada punto de ajuste "
                  "SUBE el ratio — la espiral 2010-2013 en una fracción (mención).",
                  cadena=["deuda altísima ⇒ mult* bajo", "recesión ⇒ mult alto",
                          "mult ≫ mult*", "el PIB cae más que la deuda",
                          "b sube: más ajuste pedido — la espiral"]),
        Escenario("austeridad_que_funciona", "b0=40% con mult=0.7",
                  {"b0": 40.0, "mult": 0.7},
                  "crítico 2.5, multiplicador 0.7: el ajuste baja b sin drama — la "
                  "deuda baja compra inmunidad a la paradoja.",
                  cadena=["deuda baja ⇒ mult* altísimo", "el denominador apenas se resiente",
                          "b cae casi uno a uno con dA", "consolidar barato: el premio del colchón (m65)"]),
        Escenario("el_mismo_pais_dos_momentos", "b0=120%: mult 0.5 (boom) vs 1.2 (recesión)",
                  {"mult": 0.5},
                  "con mult=0.5 el ajuste funciona; con 1.2 se muerde la cola: "
                  "idéntico país, idéntico ajuste — solo cambió el CUÁNDO (m68).",
                  cadena=["mismo b0, mismo dA", "el régimen fija el mult (m60/m70)",
                          "boom: mult<mult* ⇒ funciona", "recesión: mult>mult* ⇒ paradoja",
                          "la austeridad es una pregunta de calendario"]),
    ],
    verificaciones=[
        Verificacion("mult* = 100/b0 exacto (e independiente de dA)", _v_critico_exacto),
        Verificacion("la paradoja: ajustar sube el ratio (b0 alto, mult alto)", _v_paradoja),
        Verificacion("el mismo ajuste funciona con mult bajo (el CUÁNDO)", _v_funciona_con_mult_bajo),
        Verificacion("la deuda baja es inmune a la paradoja", _v_deuda_baja_inmune),
    ],
    notas="La dieta en un espejo que se encoge: mult* = 100/b0 decide si la báscula relativa mejora.",
)
