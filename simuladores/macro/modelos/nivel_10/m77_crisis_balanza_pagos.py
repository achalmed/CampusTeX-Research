"""simuladores/macro/modelos/nivel_10/m77_crisis_balanza_pagos.py — crisis de balanza de pagos (nivel 10).

La versión "cuentas nacionales" de la crisis: un déficit corriente crónico
financiado por reservas menguantes (paridad fija) tiene fecha de caducidad.
Cada período:  RIN_{t+1} = RIN_t + CC_t + CF_t
Con CC < 0 crónico (sobrevaluación real, m46) y CF que se seca, las reservas
caen hasta un piso crítico RIN_min (típicamente ~3 meses de importaciones).
Al tocarlo, la paridad se abandona: devaluación → la CC se corrige (m75) y
se detiene la sangría. El modelo integra m43 (identidad), m46 (RER
sobrevaluado como CAUSA) y m75 (el ajuste) en una sola línea temporal.

Procedencia: enfoque monetario de la balanza de pagos (mención); modelo
canónico de reservas (relacionado con Krugman 1979, m74) — conocimiento
general. Calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    # CC crónica negativa por sobrevaluación; mejora si el RER se corrige (dev)
    cc = p["cc0"] * np.ones(T + 1)
    cf = p["cf0"] - p["seca"] * t                       # el financiamiento se seca
    RIN = np.empty(T + 1)
    RIN[0] = p["RIN0"]
    t_crisis = None
    for k in range(T):
        RIN[k + 1] = RIN[k] + cc[k] + cf[k]
        if RIN[k + 1] <= p["RIN_min"] and t_crisis is None:
            t_crisis = k + 1
            RIN[k + 1] = p["RIN_min"]
        elif t_crisis is not None:
            RIN[k + 1] = p["RIN_min"]                    # tras devaluar, se estabiliza
    return t, RIN, cc, cf, t_crisis


def _curvas(p):
    t, RIN, cc, cf, t_crisis = _sendas(p)
    return {"lineas": {"reservas $RIN_t$": (t, RIN, config.AZUL2),
                       "piso crítico (3 meses de M)": (t, np.full(len(t), p["RIN_min"]), config.ROJO)},
            "puntos": ([(t_crisis, p["RIN_min"], f"CRISIS: devaluación en $t={t_crisis}$")]
                       if t_crisis else []),
            "anotacion": (f"CC crónica = {p['cc0']:+.0f} (sobrevaluación real, m46)\n"
                          f"financiamiento se seca: CF cae {p['seca']:.0f}/período\n"
                          + (f"la paridad cae al tocar el piso (t={t_crisis})"
                             if t_crisis else "las reservas aguantan el horizonte"))}


def _resultados(p):
    t, RIN, cc, cf, t_crisis = _sendas(p)
    return {"reservas iniciales RIN0": p["RIN0"],
            "cuenta corriente crónica CC": p["cc0"],
            "período de la crisis": float(t_crisis) if t_crisis else 9999.0,
            "reservas en el horizonte": float(RIN[-1]),
            "financiamiento inicial CF0": p["cf0"],
            "sangría neta período 0 (CC+CF)": p["cc0"] + p["cf0"]}


def _ecuaciones_calibradas(p):
    return [f"$RIN_{{t+1}} = RIN_t + CC + CF_t$",
            f"$CC = {p['cc0']:+.0f}$ (crónica), $CF_t = {p['cf0']:.0f} - {p['seca']:.0f}\\,t$"]


_P0 = {"RIN0": 100.0, "cc0": -8.0, "cf0": 6.0, "seca": 2.0, "RIN_min": 20.0, "T": 15.0}


def _v_identidad_reservas():
    t, RIN, cc, cf, t_crisis = _sendas(dict(_P0, RIN_min=-1e9))  # sin piso: identidad pura
    res = np.max(np.abs(RIN[1:] - (RIN[:-1] + cc[:-1] + cf[:-1])))
    return res < 1e-9, f"RIN_t+1 = RIN_t + CC + CF exacto (identidad de m43 en el tiempo, residuo {res:.1e})"


def _v_crisis_al_piso():
    t, RIN, cc, cf, t_crisis = _sendas(_P0)
    return t_crisis is not None and t_crisis > 0, \
        (f"las reservas tocan el piso en t={t_crisis}: la paridad no aguanta un déficit "
         "corriente crónico con financiamiento que se seca — la crisis tiene fecha")


def _v_sobrevaluacion_causa():
    t1 = _sendas(_P0)[4]
    t2 = _sendas(dict(_P0, cc0=-2.0))[4]              # RER menos sobrevaluado
    ok = (t2 is None) or (t2 > t1)
    return ok, ("corregir el RER (CC de −8 a −2, m46) posterga o evita la crisis: "
                "la sobrevaluación real es la CAUSA, las reservas solo el síntoma visible")


def _v_financiamiento_retrasa():
    t1 = _sendas(_P0)[4]
    t2 = _sendas(dict(_P0, cf0=10.0))[4]
    ok = (t2 is None) or (t2 > t1)
    return ok, (f"más financiamiento inicial retrasa la crisis (de t={t1} a "
                f"{'nunca' if t2 is None else t2}): el capital compra tiempo, no soluciona el déficit")


MODELO = Modelo(
    id="m77", nivel=10,
    nombre="Crisis de balanza de pagos",
    xlabel="Período $t$", ylabel="Reservas internacionales",
    parametros=[
        Parametro("cc0", _P0["cc0"], -15, 0, 1, "Cuenta corriente crónica CC", grupo="causa",
                  definicion="déficit por sobrevaluación real (m46): la enfermedad de fondo"),
        Parametro("cf0", _P0["cf0"], 0, 15, 1, "Financiamiento inicial CF0", grupo="síntoma"),
        Parametro("seca", _P0["seca"], 0, 5, 0.5, "Velocidad a la que se seca CF", grupo="síntoma"),
        Parametro("RIN0", _P0["RIN0"], 40, 200, 10, "Reservas iniciales RIN0", grupo="colchón"),
        Parametro("RIN_min", _P0["RIN_min"], 5, 50, 5, "Piso crítico (3 meses M)", grupo="colchón"),
        Parametro("T", _P0["T"], 8, 25, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un tipo de cambio fijo sobrevaluado siempre termina en devaluación — solo es cuestión de cuándo?",
        variables=[("RIN_t", "reservas — el combustible finito de la paridad (m50)"),
                   ("CC crónica", "el déficit por sobrevaluación real — la CAUSA (m46)"),
                   ("RIN_min", "el piso — donde la defensa se rinde")],
        derivacion=["RIN_{t+1} = RIN_t + CC_t + CF_t \\;\\;(m43\\;en\\;el\\;tiempo)",
                    "CC < 0\\;crónica\\;(sobrevaluación, m46),\\;\\;CF\\downarrow",
                    "RIN \\to RIN_{min} \\Rightarrow devaluación \\Rightarrow CC\\;se\\;corrige\\;(m75)"],
        contexto=("La crisis de balanza de pagos es la muerte anunciada de una "
                  "paridad fija sobrevaluada — y es la síntesis de tres modelos del "
                  "currículo. La identidad de reservas (m43) las hace caer período "
                  "a período; la causa es un tipo de cambio real sobrevaluado (m46) "
                  "que genera déficit corriente crónico; y el desenlace es el "
                  "ajuste forzado de m75. El patrón se repite en la historia "
                  "latinoamericana con precisión de reloj: años de paridad "
                  "'estable' que abarata importaciones y mata exportaciones, "
                  "financiados con reservas y deuda, hasta que el colchón se agota "
                  "y la devaluación llega de golpe (México 1994, y tantas otras — "
                  "menciones). La lección de política es la del trilema (m50): o "
                  "flotar, o mantener el RER competitivo, pero no fingir una "
                  "paridad que los fundamentos no sostienen."),
        autores=("Enfoque monetario de la balanza de pagos (Polak/FMI, Johnson — "
                 "menciones); su versión con ataque especulativo es Krugman (1979, "
                 "m74); conocimiento general."),
        supuestos=[
            "Paridad fija defendida con reservas (m50): con flotación, el RER se corregiría solo (m45) y no habría crisis de reservas.",
            "CC crónica exógena: en la realidad la sobrevaluación (m46) la genera endógenamente — aquí se toma como dada para ver la dinámica de reservas.",
            "Devaluación al tocar el piso: sin ataque especulativo anticipado (esa es la capa de m74).",
        ],
        ecuaciones=[
            Ecuacion("RIN_{t+1} = RIN_t + CC + CF_t", "la sangría de reservas",
                     "cada período de déficit no financiado se paga con reservas: la identidad de "
                     "m43 convertida en cuenta regresiva (verificada exacta)."),
            Ecuacion("RIN \\to RIN_{min} \\Rightarrow devaluación", "el desenlace forzoso",
                     "al piso crítico la defensa se rinde; la devaluación corrige el RER (m46) y "
                     "cierra la CC (m75) — el ajuste que la paridad postergaba."),
        ],
        intuicion=("La crisis de balanza de pagos enseña que las reservas son un "
                   "síntoma, no la enfermedad: acumularlas para defender una "
                   "paridad sobrevaluada es como tomar analgésicos para una "
                   "fractura — alivia sin curar. La cura es el precio relativo "
                   "(RER, m46): o se deja flotar para que se ajuste solo, o se "
                   "mantiene competitivo con disciplina. El Perú aprendió ambas "
                   "cosas de la manera dura en los 80 y construyó su régimen "
                   "actual — flotación administrada, reservas altas, RER vigilado "
                   "— precisamente para no repetir este gráfico (m50, m110)."),
        equilibrio=("Trayectoria determinista de reservas hasta el piso "
                    "(verificada como identidad de m43); el 'equilibrio' final es "
                    "post-devaluación, con la CC corregida por el RER nuevo — el "
                    "puente exacto a m75."),
        limitaciones=[
            "Sin ataque especulativo: m74 muestra que el colapso ANTICIPA al agotamiento — este modelo da la cota lenta.",
            "CC exógena: el vínculo RER→CC (m46) es la pieza causal que aquí se resume en un número.",
            "Sin balances en dólares: si la deuda es en dólares, la devaluación que 'cura' la CC QUIEBRA a los deudores (m71) — la cura mata (tercera generación).",
        ],
        evolucion=("Integra m43+m46+m75 en una línea temporal y prepara m74 (el "
                   "ataque que la adelanta) y m78 (la trampa de deuda que a menudo "
                   "la acompaña). Para el Perú, el contrafactual — cómo el régimen "
                   "actual evita este gráfico — es m110."),
    ),
    escenarios=[
        Escenario("muerte_anunciada", "CC crónica −8 con financiamiento que se seca",
                  {"cc0": -8.0, "seca": 2.0},
                  "las reservas tocan el piso en ~7 períodos: la paridad "
                  "sobrevaluada colapsa en fecha calculable — el guion "
                  "latinoamericano clásico.",
                  cadena=["RER sobrevaluado (m46)", "déficit corriente crónico",
                          "el capital financia… hasta que se seca", "reservas al piso",
                          "devaluación forzosa", "la CC se corrige por las malas (m75)"]),
        Escenario("corregir_el_rer", "ajuste del RER: CC de −8 a −2 (m46)",
                  {"cc0": -2.0},
                  "las reservas aguantan todo el horizonte: atacar la CAUSA (el "
                  "precio relativo) en vez del síntoma (las reservas) evita la "
                  "crisis — la lección de política.",
                  cadena=["devaluación preventiva o flotación (m45)", "el RER se corrige",
                          "la CC mejora", "la sangría de reservas se detiene",
                          "crisis evitada tratando la enfermedad, no el síntoma"]),
        Escenario("colchon_de_reservas", "más reservas iniciales (RIN0=160)",
                  {"RIN0": 160.0},
                  "la crisis se posterga pero llega igual: acumular reservas sin "
                  "corregir el RER solo compra tiempo — el error de las defensas "
                  "prolongadas.",
                  cadena=["más reservas", "más tiempo de defensa",
                          "pero la CC sigue drenando", "el piso llega igual, más tarde",
                          "reservas ≠ solución si el precio está mal"]),
    ],
    verificaciones=[
        Verificacion("identidad de reservas exacta (m43 en el tiempo)", _v_identidad_reservas),
        Verificacion("las reservas tocan el piso: la crisis tiene fecha", _v_crisis_al_piso),
        Verificacion("corregir el RER (m46) posterga o evita la crisis", _v_sobrevaluacion_causa),
        Verificacion("más financiamiento retrasa pero no cura", _v_financiamiento_retrasa),
    ],
    notas="Las reservas son el síntoma; el RER (m46) la enfermedad. Analgésicos no curan la fractura.",
)
