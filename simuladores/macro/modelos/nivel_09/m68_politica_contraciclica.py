"""simuladores/macro/modelos/nivel_09/m68_politica_contraciclica.py — política fiscal contracíclica (nivel 9).

Un ciclo determinista (brecha = A·sen(2πt/per)) y una regla fiscal
  f_t = φ·(−brecha_t)      [gastar en recesión, ahorrar en el boom]
con posible ASIMETRÍA (el vicio universal): en los booms solo se ahorra la
fracción (1−asim) de lo que la regla manda.
  brecha estabilizada = brecha·(1−mult·φ)      [exacto]
  deuda acumulada = Σ f_t: CERO si la regla es simétrica; ESCALERA si no
La prociclicidad histórica latinoamericana (φ<0 en la práctica: gastar el
boom, ajustar la recesión — Gavin-Perotti, Talvi-Végh, menciones) es el
contraejemplo que las reglas fiscales y los fondos de estabilización
(Perú incluido, mención) intentan corregir.

Procedencia: mecánica didáctica sobre m16/m60 (decisión de diseño);
evidencia de prociclicidad: menciones.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T)
    brecha = p["A"] * np.sin(2 * np.pi * t / p["per"])
    f = p["phi"] * (-brecha)
    f = np.where(brecha > 0, f * (1 - p["asim"]), f)       # el boom no se ahorra entero
    estabilizada = brecha + p["mult"] * f
    deuda = np.cumsum(f)
    return t, brecha, estabilizada, f, deuda


def _curvas(p):
    t, brecha, estab, f, deuda = _sendas(p)
    return {"lineas": {"brecha sin política": (t, brecha, config.GRIS),
                       "brecha estabilizada": (t, estab, config.AZUL2),
                       "deuda fiscal acumulada": (t, deuda, config.ROJO)},
            "anotacion": (f"regla: $f = {p['phi']:.2f}\\times(-brecha)$, "
                          f"asimetría = {p['asim']:.1f}\n"
                          f"volatilidad: ×{abs(1 - p['mult'] * p['phi']):.2f} "
                          f"(exacto con asimetría 0)\n"
                          f"deuda tras {int(p['T'])} períodos: {float(deuda[-1]):+.1f}")}


def _resultados(p):
    t, brecha, estab, f, deuda = _sendas(p)
    return {"razón de volatilidades (estab/original)": float(np.std(estab) / np.std(brecha)),
            "razón teórica |1−mult·φ| (si asim=0)": abs(1 - p["mult"] * p["phi"]),
            "deuda acumulada al final": float(deuda[-1]),
            "gasto en recesiones (Σf⁻)": float(np.sum(f[brecha < 0])),
            "ahorro en booms (Σf⁺)": float(-np.sum(f[brecha > 0]))}


def _ecuaciones_calibradas(p):
    return [f"$f_t = {p['phi']:.2f}\\,(-brecha_t)$",
            f"$brecha^{{estab}} = brecha\\,(1 - {p['mult']:.2f}\\times{p['phi']:.2f}) "
            f"= {1 - p['mult'] * p['phi']:.2f}\\,brecha$"]


_P0 = {"A": 3.0, "per": 8.0, "phi": 0.4, "mult": 0.7, "asim": 0.0, "T": 24.0}


def _v_estabilizacion_exacta():
    t, brecha, estab, f, deuda = _sendas(_P0)
    razon = float(np.std(estab) / np.std(brecha))
    teo = abs(1 - _P0["mult"] * _P0["phi"])
    return abs(razon - teo) < 1e-12, \
        (f"la volatilidad se reduce EXACTAMENTE a |1−mult·φ| = {teo:.2f}: la regla "
         "simétrica es un atenuador lineal del ciclo")


def _v_simetria_gratis():
    t, brecha, estab, f, deuda = _sendas(_P0)
    return abs(float(deuda[-1])) < 1e-9, \
        ("con regla SIMÉTRICA y ciclos completos, la deuda acumulada es CERO exacto: "
         "la contracíclica bien hecha es un seguro, no un gasto")


def _v_ratchet():
    t, brecha, estab, f, deuda = _sendas(dict(_P0, asim=0.6))
    d1 = float(deuda[int(_P0["per"]) - 1])
    d2 = float(deuda[2 * int(_P0["per"]) - 1])
    d3 = float(deuda[3 * int(_P0["per"]) - 1])
    ok = d1 > 1e-9 and abs((d2 - d1) - d1) < 1e-9 and abs((d3 - d2) - d1) < 1e-9
    return ok, (f"con asimetría (no ahorrar el boom), la deuda sube en ESCALERA exacta "
                f"(+{d1:.1f} por ciclo): el vicio fiscal universal, cuantificado")


def _v_prociclico_amplifica():
    t, brecha, estab, f, deuda = _sendas(dict(_P0, phi=-0.3))
    razon = float(np.std(estab) / np.std(brecha))
    return razon > 1, (f"con φ<0 (gastar el boom, ajustar la recesión) la volatilidad se "
                       f"AMPLIFICA ×{razon:.2f}: la prociclicidad histórica latinoamericana")


MODELO = Modelo(
    id="m68", nivel=9,
    nombre="Política fiscal contracíclica",
    xlabel="Período $t$", ylabel="Brecha (%) · deuda (u.m.)",
    parametros=[
        Parametro("phi", _P0["phi"], -0.5, 1.0, 0.05, "Regla fiscal φ", grupo="regla",
                  definicion=">0 contracíclica; <0 el pecado procíclico"),
        Parametro("asim", _P0["asim"], 0.0, 1.0, 0.1, "Asimetría (no ahorrar el boom)", grupo="regla",
                  definicion="el ratchet: gastar en las malas sin guardar en las buenas"),
        Parametro("mult", _P0["mult"], 0.2, 1.5, 0.05, "Multiplicador fiscal (m60)", grupo="estructura"),
        Parametro("A", _P0["A"], 1, 6, 0.5, "Amplitud del ciclo A", grupo="ciclo"),
        Parametro("per", _P0["per"], 4, 12, 1, "Período del ciclo", grupo="ciclo"),
        Parametro("T", _P0["T"], 8, 48, 4, "Horizonte (múltiplo del período)", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Puede el fisco suavizar el ciclo sin arruinarse — y por qué casi todos terminan haciéndolo al revés?",
        variables=[("φ", "la regla — signo y tamaño de la respuesta al ciclo"),
                   ("asim", "el ratchet — la mitad de la regla que la política no cumple"),
                   ("deuda acumulada", "el veredicto — cero si simétrica, escalera si no")],
        derivacion=["f_t = \\phi\\,(-brecha_t)",
                    "brecha^{estab} = brecha\\,(1 - mult\\cdot\\phi)",
                    "sim\\acute{e}trica \\Rightarrow \\sum f_t = 0 \\;(ciclos\\;completos)"],
        contexto=("La teoría es limpia: gastar en la recesión, guardar en el boom, "
                  "y el ciclo se atenúa con deuda promedio CERO — un seguro, no un "
                  "gasto. La práctica histórica fue lo contrario: en América "
                  "Latina la política fiscal AMPLIFICÓ el ciclo por décadas "
                  "(procíclica: Gavin-Perotti 1997, Talvi-Végh — menciones), "
                  "porque el boom afloja la restricción de crédito y la política "
                  "gasta lo transitorio (m66: el espejismo). Las reglas fiscales y "
                  "los fondos de estabilización — el peruano entre ellos, mención "
                  "— son ingeniería institucional contra ese vicio: obligan a "
                  "cumplir la mitad impopular de la regla."),
        autores=("Estabilizadores y política discrecional: tradición keynesiana "
                 "(m04); evidencia de prociclicidad: Gavin y Perotti (1997), Talvi "
                 "y Végh (2005), Frankel-Végh-Vuletin sobre la 'graduación' "
                 "(menciones)."),
        supuestos=[
            "Ciclo determinista y regla lineal: el laboratorio limpio para ver las TRES aritméticas (contra, pro, ratchet).",
            "El multiplicador es el de m60 y es constante: en la realidad es mayor en recesión (m70) — lo que REFUERZA el caso contracíclico.",
            "Espacio fiscal disponible: la regla presupone el margen de m65 (sin colchón no hay contracíclica que valga).",
        ],
        ecuaciones=[
            Ecuacion("brecha^{estab} = (1 - mult\\,\\phi)\\,brecha", "el atenuador",
                     "la regla multiplica el ciclo por un factor menor que uno (verificado "
                     "exacto): φ=0.4 con mult=0.7 recorta el 28% de la volatilidad."),
            Ecuacion("\\sum_{ciclo} f_t = 0 \\;\\;vs\\;\\; \\sum_{ciclo} f_t = \\phi\\,asim\\,\\Sigma^{boom}",
                     "seguro vs escalera",
                     "la simetría hace gratis el seguro; el ratchet convierte cada ciclo en un "
                     "peldaño de deuda — verificado como escalera EXACTA."),
        ],
        intuicion=("La contracíclica es un seguro de auto: las primas (ahorrar el "
                   "boom) duelen justo cuando nadie ve el riesgo, y el siniestro "
                   "(la recesión) llega cuando ya no hay tiempo de asegurarse. El "
                   "ratchet es conducir sin pagar primas: funciona hasta el primer "
                   "choque, y la escalera de deuda del gráfico es la factura del "
                   "'seguro' impago. La lección institucional peruana: el fondo de "
                   "estabilización es un cobrador de primas automático (mención)."),
        equilibrio=("Con regla simétrica: ciclo atenuado exacto y deuda de ciclo "
                    "completo CERO (ambos verificados). Con asimetría: deuda en "
                    "escalera aritmética — el estado estacionario fiscal no existe "
                    "y m64 espera al final de la escalera."),
        limitaciones=[
            "Rezagos de implementación: la discrecional suele llegar tarde (el ciclo ya giró) — los estabilizadores automáticos (m66) no tienen ese problema.",
            "La brecha se mide con niebla (m16): reglas sobre brechas mal medidas pueden ser procíclicas sin querer.",
            "El multiplicador constante subestima el caso contracíclico: m70 muestra que es mayor exactamente cuando la regla manda gastar.",
        ],
        evolucion=("Define la política fiscal BIEN hecha para que m69 examine la "
                   "mal hecha (ajustar en la recesión) y m70 aporte el juicio "
                   "empírico. La versión peruana — regla, fondo, y el multiplicador "
                   "local — es m107-m108 con datos del MEF."),
    ),
    escenarios=[
        Escenario("seguro_bien_pagado", "regla simétrica: φ=0.4, asimetría 0",
                  {"phi": 0.4, "asim": 0.0},
                  "el ciclo se atenúa 28% y la deuda vuelve a CERO en cada ciclo "
                  "completo: la contracíclica es gratis si se cumple entera.",
                  cadena=["recesión: la regla gasta", "boom: la regla AHORRA lo mismo",
                          "el ciclo se atenúa ×(1−mult·φ)", "Σf = 0 por ciclo",
                          "seguro sin prima neta"]),
        Escenario("pecado_prociclico", "φ = −0.3: gastar el boom, ajustar la recesión",
                  {"phi": -0.3},
                  "la volatilidad se AMPLIFICA ×1.21: la política fiscal como "
                  "amplificador del ciclo — la historia latinoamericana que las "
                  "reglas vinieron a enterrar.",
                  cadena=["boom: entra plata y se gasta (m66: espejismo)",
                          "recesión: se corta el crédito y se ajusta",
                          "la política empuja EN la dirección del ciclo",
                          "volatilidad amplificada", "y la deuda igual crece"]),
        Escenario("ratchet", "gastar en las malas sin guardar en las buenas (asim=0.6)",
                  {"asim": 0.6},
                  "el ciclo se atenúa… y la deuda sube +2 por ciclo en escalera "
                  "perfecta: el 'seguro' impago que termina en m64.",
                  cadena=["recesión: la regla gasta completa",
                          "boom: solo se ahorra el 40% de lo debido",
                          "Σf > 0 cada ciclo", "escalera de deuda exacta",
                          "el colchón de m65 se erosiona ciclo a ciclo"]),
    ],
    verificaciones=[
        Verificacion("atenuación exacta |1−mult·φ|", _v_estabilizacion_exacta),
        Verificacion("regla simétrica ⇒ deuda de ciclo CERO", _v_simetria_gratis),
        Verificacion("ratchet ⇒ escalera de deuda exacta", _v_ratchet),
        Verificacion("procíclica ⇒ amplifica el ciclo", _v_prociclico_amplifica),
    ],
    notas="El seguro fiscal: gratis si simétrico, escalera si no. La prociclicidad fue el vicio; la regla, la vacuna.",
)
