# m74_crisis_cambiaria.py — crisis cambiaria: las tres generaciones (nivel 10).
#
# El reloj del trilema (m50) con EXPECTATIVAS: el ataque especulativo no
# espera a que se agoten las reservas — llega antes.
# Primera generación (Krugman 1979): con fuga constante f, las reservas
# durarían T = RIN/f; pero los especuladores atacan cuando el tipo sombra
# (el que habría con flotación) alcanza la paridad — en  T_ataque = T − h,
# donde h = ganancia_esperada. El colapso es ANTICIPADO y sin previo aviso.
# Segunda generación (Obstfeld): equilibrios MÚLTIPLES — si el mercado cree
# que el gobierno abandonará la paridad (por su costo), ataca y lo fuerza;
# si cree que resistirá, no ataca — profecía autocumplida (como m73).
#
# Procedencia: Krugman (1979, primera generación) y Obstfeld (1994, segunda
# generación) — menciones; conocimiento general. Calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    reservas = np.maximum(0.0, p["RIN"] - p["fuga"] * t)
    t_agota = p["RIN"] / p["fuga"] if p["fuga"] > 0 else float("inf")
    t_ataque = max(0.0, t_agota - p["h"])            # el ataque anticipa por h
    return t, reservas, t_agota, t_ataque


def _curvas(p):
    t, reservas, t_agota, t_ataque = _sendas(p)
    # las reservas caen en picada (salto) en el ataque:
    reservas_reales = reservas.copy()
    if np.isfinite(t_ataque):
        ia = int(np.ceil(t_ataque))
        if ia <= len(reservas_reales) - 1:
            reservas_reales[ia:] = 0.0                # el ataque las agota de golpe
    return {"lineas": {"reservas observadas (con ataque)": (t, reservas_reales, config.AZUL2),
                       "reservas sin ataque (agotamiento lento)": (t, reservas, config.GRIS)},
            "puntos": ([(t_ataque, float(np.interp(t_ataque, t, reservas)),
                         f"ATAQUE en $t={t_ataque:.1f}$")] if np.isfinite(t_ataque) else []),
            "anotacion": (f"agotamiento natural: $T = RIN/fuga = {t_agota:.1f}$\n"
                          f"ataque especulativo: $T - h = {t_ataque:.1f}$\n"
                          "el colapso ADELANTA: nadie espera al último dólar")}


def _resultados(p):
    t, reservas, t_agota, t_ataque = _sendas(p)
    return {"agotamiento natural T = RIN/fuga": t_agota if np.isfinite(t_agota) else 9999.0,
            "momento del ataque (T − h)": t_ataque,
            "anticipación del ataque (h)": p["h"],
            "reservas en el ataque": float(np.interp(t_ataque, t, reservas)) if np.isfinite(t_ataque) else 0.0,
            "reservas perdidas de golpe": float(np.interp(t_ataque, t, reservas)) if np.isfinite(t_ataque) else 0.0}


def _ecuaciones_calibradas(p):
    t_agota = p["RIN"] / p["fuga"] if p["fuga"] > 0 else float("inf")
    return [f"$T = {p['RIN']:.0f}/{p['fuga']:.0f} = {t_agota:.1f}$ (agotamiento lento)",
            f"$T_{{ataque}} = {t_agota:.1f} - {p['h']:.0f} = {max(0.0, t_agota - p['h']):.1f}$"]


_P0 = {"RIN": 200.0, "fuga": 20.0, "h": 3.0, "T": 12.0}


def _v_ataque_anticipa():
    t, reservas, t_agota, t_ataque = _sendas(_P0)
    return t_ataque < t_agota, \
        (f"el ataque (t={t_ataque:.1f}) llega ANTES del agotamiento natural (t={t_agota:.1f}): "
         "los especuladores no esperan al último dólar — la lección de Krugman 1979")


def _v_reservas_al_atacar():
    t, reservas, t_agota, t_ataque = _sendas(_P0)
    r_ataque = float(np.interp(t_ataque, t, reservas))
    return r_ataque > 0, \
        (f"en el ataque QUEDAN {r_ataque:.0f} de reservas: la paridad no cae por falta de "
         "reservas sino por la EXPECTATIVA de que faltarán — se las llevan de golpe")


def _v_mas_reservas_retrasan():
    t1 = _sendas(_P0)[3]
    t2 = _sendas(dict(_P0, RIN=300.0))[3]
    return t2 > t1, \
        (f"más reservas retrasan el ataque (t: {t1:.1f}→{t2:.1f}) pero NO lo evitan: "
         "el colchón compra tiempo, no inmunidad (contra fundamentos malos)")


def _v_fuga_acelera():
    t1 = _sendas(_P0)[3]
    t2 = _sendas(dict(_P0, fuga=40.0))[3]
    return t2 < t1, \
        (f"más fuga adelanta el colapso (t: {t1:.1f}→{t2:.1f}): el déficit fiscal "
         "monetizado (m36/m62) que alimenta la fuga es la raíz de primera generación")


MODELO = Modelo(
    id="m74", nivel=10,
    nombre="Crisis cambiaria (tres generaciones)",
    xlabel="Período $t$", ylabel="Reservas internacionales",
    parametros=[
        Parametro("h", _P0["h"], 0, 8, 0.5, "Anticipación del ataque h", grupo="expectativas",
                  definicion="cuánto adelantan los especuladores al agotamiento"),
        Parametro("fuga", _P0["fuga"], 5, 50, 5, "Fuga de reservas por período", grupo="fundamentos",
                  definicion="alimentada por el déficit monetizado (m36, m62)"),
        Parametro("RIN", _P0["RIN"], 50, 400, 25, "Reservas iniciales RIN", grupo="fundamentos"),
        Parametro("T", _P0["T"], 6, 20, 1, "Períodos simulados", grupo="experimento"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué las paridades caen de golpe y sin aviso, con reservas todavía en el banco central?",
        variables=[("T = RIN/fuga", "el reloj del trilema (m50): agotamiento lento"),
                   ("T − h", "el ataque real: los especuladores anticipan"),
                   ("h", "la expectativa — lo que convierte un goteo en avalancha")],
        derivacion=["m50: \\;fuga\\;constante \\Rightarrow T = RIN/fuga",
                    "tipo\\;sombra\\;alcanza\\;la\\;paridad\\;antes: \\;T_{ataque} = T - h",
                    "ataque \\Rightarrow reservas\\;a\\;cero\\;de\\;GOLPE"],
        contexto=("El trilema (m50) daba un reloj lento: las reservas duran "
                  "T=RIN/fuga. Krugman (1979) mostró que el mercado no es tan "
                  "paciente: los especuladores calculan el 'tipo sombra' — el que "
                  "regiría con flotación — y atacan en el instante EXACTO en que "
                  "cruzaría la paridad, adelantándose al agotamiento. El resultado "
                  "es la firma de las crisis cambiarias: colapso súbito, sin previo "
                  "aviso, con reservas todavía en la bóveda. La primera generación "
                  "(Krugman) culpa a los fundamentos (déficit monetizado, m36); la "
                  "segunda (Obstfeld 1994) añade equilibrios múltiples — el ataque "
                  "puede ser autocumplido, como la corrida de m73; la tercera "
                  "(post-Asia 1997) suma balances en dólares (m71) y sudden stops "
                  "(m75)."),
        autores=("Krugman (1979, primera generación); Flood-Garber (formalización); "
                 "Obstfeld (1994, segunda generación, equilibrios múltiples); "
                 "tercera generación post-1997: Krugman, Chang-Velasco — menciones."),
        supuestos=[
            "Primera generación: fuga por fundamentos (déficit) y ataque racional que anticipa — determinista.",
            "El gobierno defiende hasta agotar reservas y luego flota (no sube la tasa a lo Defensa, m48 — esa es otra rama).",
            "h resume la anticipación: en la segunda generación h es ENDÓGENO a la creencia (por eso hay equilibrios múltiples).",
        ],
        ecuaciones=[
            Ecuacion("T_{ataque} = \\frac{RIN}{fuga} - h", "el colapso anticipado",
                     "el ataque adelanta al agotamiento por h: cuanto más creen los especuladores "
                     "en el colapso, antes ocurre — la profecía se acerca a sí misma."),
            Ecuacion("primera: \\;fundamentos \\;;\\; segunda: \\;equilibrios\\;múltiples",
                     "las dos raíces",
                     "Krugman: la paridad es insostenible y el mercado solo apura lo inevitable. "
                     "Obstfeld: la paridad era viable, pero la creencia la mató (como m73)."),
        ],
        intuicion=("La crisis cambiaria es el trilema (m50) leído por un mercado "
                   "que sabe contar: si todos ven que las reservas se agotarán, "
                   "nadie quiere ser el último con moneda local — y el 'último "
                   "día' se adelanta hasta volverse HOY. En primera generación el "
                   "gobierno se lo buscó (déficit monetizado); en segunda, la mala "
                   "suerte de coordinación basta. Para un emergente como el Perú "
                   "de los 80, ambos mecanismos operaban; el Perú de hoy — "
                   "reservas altas, flotación, metas (m40, m50) — compró inmunidad "
                   "cara y deliberada."),
        equilibrio=("Primera generación: momento del ataque ÚNICO y determinista "
                    "(T−h, verificado). Segunda generación: equilibrios MÚLTIPLES — "
                    "ataque o no según la creencia, sin cambio de fundamentos "
                    "(el mismo mecanismo de m73)."),
        limitaciones=[
            "h exógeno aquí: la riqueza de la segunda generación es que h depende de la creencia sobre la resolución del gobierno (endógeno, múltiple).",
            "Sin defensa por tasa: subir la tasa para retener capital (m48) es la otra estrategia — con su propio costo recesivo.",
            "Sin balances en dólares: la tercera generación (Asia 1997) muestra que la depreciación QUIEBRA a los endeudados en dólares — el lazo con m71/m75.",
        ],
        evolucion=("Es la profecía autocumplida de m73 aplicada a la paridad, y "
                   "el trilema de m50 con dientes. m75 (sudden stop) añade el corte "
                   "de financiamiento externo, m76 la lleva a la deuda soberana, y "
                   "m84/m87 (nivel 11) la vuelven episodios. El contrafactual "
                   "peruano — por qué el sol no colapsa — es m50 aplicado (m110)."),
    ),
    escenarios=[
        Escenario("ataque_de_krugman", "fundamentos malos: fuga 20, anticipación 3",
                  {"fuga": 20.0, "h": 3.0},
                  "las reservas 'durarían' 10 períodos pero el ataque llega en el 7: "
                  "colapso súbito con reservas todavía en la bóveda — la firma de "
                  "primera generación.",
                  cadena=["déficit monetizado alimenta la fuga", "el mercado calcula el tipo sombra",
                          "ataca cuando cruzaría la paridad", "reservas a cero de golpe en T−h",
                          "devaluación súbita sin aviso"]),
        Escenario("mas_reservas", "el mismo país con RIN=300 (colchón mayor)",
                  {"RIN": 300.0},
                  "el ataque se retrasa del 7 al 12 pero NO se evita: con "
                  "fundamentos malos, las reservas compran tiempo, no inmunidad — "
                  "la lección de las defensas fallidas.",
                  cadena=["más reservas", "el agotamiento natural se aleja",
                          "el ataque también se retrasa", "pero llega igual",
                          "acumular sin corregir el déficit solo posterga"]),
        Escenario("expectativas_de_panico", "alta anticipación: h=6 (segunda generación)",
                  {"h": 6.0},
                  "el ataque salta al período 4: cuando el mercado DUDA de la "
                  "voluntad de defender, la crisis se autocumple mucho antes — "
                  "Obstfeld y las profecías cambiarias.",
                  cadena=["duda sobre la resolución del gobierno", "↑h (todos anticipan)",
                          "el ataque se adelanta", "fuerza el abandono que temían",
                          "profecía autocumplida (como m73)"]),
    ],
    verificaciones=[
        Verificacion("el ataque anticipa al agotamiento (Krugman)", _v_ataque_anticipa),
        Verificacion("quedan reservas al atacar (no es falta, es expectativa)", _v_reservas_al_atacar),
        Verificacion("más reservas retrasan pero no evitan", _v_mas_reservas_retrasan),
        Verificacion("más fuga adelanta el colapso", _v_fuga_acelera),
    ],
    notas="El trilema (m50) leído por un mercado que sabe contar: el último día se adelanta hasta ser hoy.",
)
