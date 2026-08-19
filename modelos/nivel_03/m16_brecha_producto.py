# m16_brecha_producto.py — brecha del producto (output gap) — nivel 3.
#
#   brecha_t = (Y_t − Y*_t)/Y*_t ,  con Y*_t creciendo a g* constante.
# Simulación: una recesión abre una brecha de tamaño `shock` en t_shock y se
# cierra geométricamente a velocidad λ:  brecha_{t+1} = (1−λ)·brecha_t.
# Métricas: semivida de la brecha y PIB-años perdidos (el costo acumulado).
#
# Procedencia: concepto operativo estándar de bancos centrales y reglas
# fiscales — conocimiento general; dinámica de cierre geométrico: decisión de
# diseño didáctica (la medición real usa filtros/función de producción).

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _simular(p):
    T, t0 = int(round(p["T"])), int(round(p["t_shock"]))
    t = np.arange(T + 1)
    Ypot = p["Y0"] * (1 + p["g_pot"] / 100) ** t
    brecha = np.zeros(T + 1)
    for i in range(t0, T + 1):
        brecha[i] = p["shock"] * (1 - p["lam"]) ** (i - t0)
    Y = Ypot * (1 + brecha / 100)
    return t, Ypot, Y, brecha


def _curvas(p):
    t, Ypot, Y, brecha = _simular(p)
    i_max = int(np.argmax(np.abs(brecha)))
    return {"lineas": {"PIB potencial $Y^*$": (t, Ypot, config.GRIS),
                       "PIB observado $Y$": (t, Y, config.AZUL2)},
            "puntos": [(float(t[i_max]), float(Y[i_max]),
                        f"brecha ${brecha[i_max]:+.1f}\\%$")],
            "anotacion": (f"shock de ${p['shock']:+.1f}\\%$ en $t={int(p['t_shock'])}$\n"
                          f"velocidad de cierre $\\lambda = {p['lam']:.2f}$\n"
                          f"PIB-años perdidos $= {np.sum(brecha):+.1f}$ puntos de $Y^*$")}


def _resultados(p):
    t, Ypot, Y, brecha = _simular(p)
    semivida = np.log(0.5) / np.log(1 - p["lam"])
    abiertos = np.where(np.abs(brecha) >= 0.5)[0]
    return {"brecha máxima (%)": float(brecha[int(round(p['t_shock']))]),
            "semivida de la brecha (períodos)": semivida,
            "períodos con |brecha| ≥ 0.5%": float(len(abiertos)),
            "PIB-años perdidos (Σ brechas, %)": float(np.sum(brecha)),
            "Y potencial final": float(Ypot[-1]), "Y observado final": float(Y[-1])}


_P0 = {"g_pot": 3.0, "shock": -6.0, "t_shock": 5.0, "lam": 0.3, "T": 20.0, "Y0": 100.0}


def _v_geometrico():
    _, _, _, brecha = _simular(_P0)
    t0 = int(_P0["t_shock"])
    razones = brecha[t0 + 1:t0 + 6] / brecha[t0:t0 + 5]
    return bool(np.all(np.abs(razones - (1 - _P0["lam"])) < 1e-12)), \
        f"la brecha decae geométricamente a razón (1−λ) = {1 - _P0['lam']:.2f}"


def _v_identidad():
    _, Ypot, Y, brecha = _simular(_P0)
    return bool(np.all(np.abs(Y - Ypot * (1 + brecha / 100)) < 1e-9)), \
        "identidad Y = Y*·(1+brecha) en toda la trayectoria"


def _v_semivida():
    _, _, _, brecha = _simular(dict(_P0, T=60))
    t0 = int(_P0["t_shock"])
    semivida = np.log(0.5) / np.log(1 - _P0["lam"])
    idx = t0 + int(np.ceil(semivida))
    ok = abs(brecha[idx]) <= abs(_P0["shock"]) / 2 + 1e-9
    return ok, f"a los {semivida:.1f} períodos la brecha ya cayó a la mitad (fórmula = simulación)"


MODELO = Modelo(
    id="m16", nivel=3,
    nombre="Brecha del producto (output gap)",
    xlabel="Período $t$", ylabel="PIB (índice, $Y_0=100$)",
    parametros=[
        Parametro("shock", _P0["shock"], -12.0, 6.0, 0.5, "Tamaño del shock (% de Y*)"),
        Parametro("lam", _P0["lam"], 0.05, 0.8, 0.05, "Velocidad de cierre λ"),
        Parametro("g_pot", _P0["g_pot"], 0.0, 6.0, 0.25, "Crecimiento potencial g* (%)"),
        Parametro("t_shock", _P0["t_shock"], 1, 10, 1, "Período del shock"),
        Parametro("T", _P0["T"], 10, 40, 1, "Horizonte simulado"),
        Parametro("Y0", _P0["Y0"], 50, 200, 10, "PIB inicial (índice)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        contexto=("Si el PIB potencial es lo que la economía PUEDE producir sin "
                  "tensionar precios, la brecha mide cuán lejos está de lograrlo. Es el "
                  "termómetro operativo de la macro de corto plazo: los bancos "
                  "centrales la usan para calibrar la tasa (regla de Taylor, m38), los "
                  "ministerios para separar déficit estructural de cíclico (m66), y los "
                  "analistas para fechar recesiones."),
        autores=("Concepto ligado a Okun (potential GNP, 1962) y a la práctica de "
                 "bancos centrales y organismos (FMI, OCDE); la medición moderna usa "
                 "filtros estadísticos (Hodrick-Prescott, mención) o funciones de "
                 "producción."),
        supuestos=[
            "Y* observable y creciendo a tasa constante g* (en la realidad: estimado y revisado).",
            "El cierre de la brecha es geométrico a velocidad λ (resumen didáctico de todos los mecanismos de ajuste).",
            "El shock no daña a Y*: la recesión es puramente cíclica (la histéresis viola esto — ver limitaciones).",
        ],
        ecuaciones=[
            Ecuacion("\\text{brecha}_t = \\frac{Y_t - Y^*_t}{Y^*_t}", "definición",
                     "negativa en recesión (capacidad ociosa, presión desinflacionaria), positiva "
                     "en sobrecalentamiento (presión inflacionaria)."),
            Ecuacion("\\text{brecha}_{t+1} = (1-\\lambda)\\,\\text{brecha}_t", "cierre",
                     "λ resume la eficacia de todos los estabilizadores: mercados que ajustan, "
                     "política contracíclica, expectativas. Semivida = ln(0.5)/ln(1−λ)."),
        ],
        intuicion=("Dos números resumen una recesión: cuán honda (brecha máxima) y cuán "
                   "larga (λ). El costo social es el ÁREA entre las dos curvas — los "
                   "PIB-años perdidos — y depende más de λ que del golpe inicial: una "
                   "recesión moderada pero lenta de cerrar puede costar más que un "
                   "desplome con rebote rápido."),
        equilibrio=("El 'equilibrio' es la propia senda potencial (brecha 0); es "
                    "globalmente estable por construcción con 0<λ<1. Toda la discusión "
                    "económica seria está en qué determina λ — que aquí es un parámetro "
                    "y en los niveles 4 y 8 será un resultado."),
        limitaciones=[
            "Y* NO es observable: se estima con filtros o funciones de producción y se revisa fuerte (tras 2008 muchas brechas 'positivas' se re-estimaron como sobrecalentamiento).",
            "El cierre geométrico es una caja negra: no dice POR QUÉ se cierra (precios, políticas, expectativas — eso es AD-AS, m20-m25).",
            "Ignora la histéresis: recesiones largas pueden destruir capacidad y BAJAR Y* (el shock deja de ser puramente cíclico).",
        ],
        evolucion=("Da el insumo que faltaba para operacionalizar el nivel 3: la brecha "
                   "alimenta la Phillips moderna y la regla de Taylor (m38). m17 la hace "
                   "estocástica (ciclos como shocks repetidos) y m98 la estimará con el "
                   "PBI peruano real del BCRP."),
    ),
    escenarios=[
        Escenario("recesion_profunda", "desplome de −10% (estilo crisis mayor)",
                  {"shock": -10.0},
                  "la brecha máxima casi duplica el caso base y los PIB-años perdidos "
                  "crecen más que proporcionalmente."),
        Escenario("recuperacion_lenta", "cierre lento λ = 0.1 (semivida ~6.6 períodos)",
                  {"lam": 0.1},
                  "el mismo golpe cuesta el triple en PIB-años: la velocidad de cierre "
                  "importa más que la profundidad — el argumento de la política contracíclica."),
        Escenario("sobrecalentamiento", "brecha POSITIVA de +4%",
                  {"shock": 4.0},
                  "producir sobre el potencial no es gratis: es la antesala de la "
                  "inflación (m18) — la brecha positiva es el caso que Taylor castiga (m38)."),
    ],
    verificaciones=[
        Verificacion("decaimiento geométrico exacto (1−λ)", _v_geometrico),
        Verificacion("identidad Y = Y*(1+brecha)", _v_identidad),
        Verificacion("semivida teórica = simulada", _v_semivida),
    ],
    notas="El costo de una recesión es el área entre curvas: profundidad × persistencia.",
)
