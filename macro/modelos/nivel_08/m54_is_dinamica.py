# m54_is_dinamica.py — la curva IS dinámica (ecuación de Euler) — nivel 8.
#
# La demanda con hogares racionales que miran al futuro:
#   x_t = x_{t+1} − σ·(r_t − r_n)      (brecha hoy = brecha mañana − tasa real)
# Iterando hacia adelante (con x_{T+1}=0):
#   x_t = −σ · Σ_{j≥t} (r_j − r_n)
# La brecha de HOY es la suma de TODAS las tasas reales futuras: la demanda
# se vuelve un precio de activo. Corolario que cambió a los bancos centrales:
# ANUNCIAR tasas futuras mueve el presente — forward guidance.
#
# Procedencia: ecuación de Euler del consumo log-linealizada (tradición
# Ramsey; formulación NK: Woodford, Galí — menciones) — conocimiento general.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _sendas(p, T=None):
    T = int(round(T if T is not None else p["T"]))
    t = np.arange(T + 1)
    ini, K = int(round(p["t_ini"])), int(round(p["K"]))
    r_gap = np.where((t >= ini) & (t < ini + K), p["dr"], 0.0)
    x = np.zeros(T + 2)
    for j in range(T, -1, -1):                      # iteración hacia atrás
        x[j] = x[j + 1] - p["sigma"] * r_gap[j]
    return t, r_gap, x[:-1]


def _curvas(p):
    t, r_gap, x = _sendas(p)
    return {"lineas": {"brecha $x_t$ (demanda)": (t, x, config.AZUL2),
                       "apretón anunciado $r_t - r_n$": (t, r_gap, config.ROJO),
                       "cero": (t, np.zeros_like(x), config.GRIS)},
            "anotacion": (f"apretón de {p['dr']:.1f} pp × {int(p['K'])} períodos, "
                          f"anunciado para $t={int(p['t_ini'])}$\n"
                          f"impacto HOY: $x_0 = -\\sigma K\\,dr = "
                          f"{-p['sigma'] * p['K'] * p['dr']:.1f}$\n"
                          "el presente descuenta TODO el futuro anunciado")}


def _resultados(p):
    t, r_gap, x = _sendas(p)
    ini, K = int(round(p["t_ini"])), int(round(p["K"]))
    return {"x hoy (t=0)": float(x[0]),
            "teórico −σ·K·dr": -p["sigma"] * p["K"] * p["dr"],
            "x al iniciar el apretón": float(x[ini]) if ini < len(x) else 0.0,
            "x al terminar el apretón": float(x[min(ini + K, len(x) - 1)]),
            "suma de tasas futuras (t=0)": float(np.sum(r_gap))}


def _ecuaciones_calibradas(p):
    return [f"$x_t = x_{{t+1}} - {p['sigma']:.1f}\\,(r_t - r_n)$",
            f"$x_0 = -{p['sigma']:.1f} \\times {int(p['K'])} \\times {p['dr']:.1f} "
            f"= {-p['sigma'] * p['K'] * p['dr']:.1f}$"]


_P0 = {"sigma": 1.0, "dr": 1.0, "K": 4.0, "t_ini": 3.0, "T": 14.0, "r_n": 2.0}


def _v_suma_de_futuras():
    _, r_gap, x = _sendas(_P0)
    teo = -_P0["sigma"] * np.sum(r_gap)
    return abs(float(x[0]) - teo) < 1e-12, \
        (f"x_0 = −σ·Σ(tasas futuras) = {teo:.1f} exacto: la demanda de hoy es la "
         "suma descontada del apretón entero")


def _v_forward_guidance():
    x1 = _sendas(_P0)[2][0]
    x2 = _sendas(dict(_P0, K=8.0))[2][0]
    return abs(x2 / x1 - 2.0) < 1e-12, \
        ("duplicar la DURACIÓN anunciada duplica el efecto HOY (sin tocar la tasa "
         "presente): el forward guidance como teorema")


def _v_presente_responde_al_futuro():
    _, r_gap, x = _sendas(_P0)
    ok = abs(float(r_gap[0])) < 1e-12 and float(x[0]) < -1e-9
    return ok, (f"en t=0 la tasa AÚN no subió (r_0=r_n) pero x_0 = {float(x[0]):.1f}: "
                "la IS estática de m10 jamás podría — aquí el anuncio ES política")


def _v_final_limpio():
    _, _, x = _sendas(_P0)
    fin = int(_P0["t_ini"] + _P0["K"])
    return bool(np.all(np.abs(x[fin:]) < 1e-12)), \
        "terminado el apretón, x vuelve EXACTAMENTE a 0: sin tasas futuras no hay brecha"


MODELO = Modelo(
    id="m54", nivel=8,
    nombre="Curva IS dinámica (Euler)",
    xlabel="Período $t$", ylabel="Desviaciones (pp)",
    parametros=[
        Parametro("dr", _P0["dr"], 0.25, 3, 0.25, "Tamaño del apretón dr (pp)", grupo="anuncio"),
        Parametro("K", _P0["K"], 1, 8, 1, "Duración anunciada K", grupo="anuncio",
                  definicion="el corazón del forward guidance"),
        Parametro("t_ini", _P0["t_ini"], 0, 8, 1, "Inicio anunciado del apretón", grupo="anuncio"),
        Parametro("sigma", _P0["sigma"], 0.5, 2, 0.1, "Sensibilidad intertemporal σ", grupo="estructura",
                  definicion="cuánto posterga consumo el hogar por punto de tasa real"),
        Parametro("T", _P0["T"], 8, 30, 1, "Períodos simulados", grupo="experimento"),
        Parametro("r_n", _P0["r_n"], 0, 4, 0.25, "Tasa natural r_n", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué la demanda de HOY cae cuando el banco central solo ANUNCIA tasas para el año que viene?",
        variables=[("x_t", "brecha del producto — un precio de activo"),
                   ("r_t − r_n", "la senda de tasas reales — lo único que importa, ENTERA"),
                   ("σ", "sustitución intertemporal — la palanca del hogar racional")],
        derivacion=["Euler: \\;c_t = c_{t+1} - \\sigma(r_t - r_n) \\;(log-lineal)",
                    "x_t = x_{t+1} - \\sigma(r_t - r_n)",
                    "iterando: \\;x_t = -\\sigma \\sum_{j\\ge t}(r_j - r_n)"],
        contexto=("La IS del nivel 2 miraba la tasa de HOY; los hogares de Ramsey "
                  "miran la vida entera. Al log-linealizar su ecuación de Euler, la "
                  "brecha se vuelve la suma de todas las tasas reales futuras — y la "
                  "política monetaria cambia de instrumento: ya no solo mueve la "
                  "tasa corta, mueve EXPECTATIVAS de tasas. Cuando el ZLB (m12) ató "
                  "las manos de los bancos centrales en 2008-2015, esta ecuación fue "
                  "su salida: prometer tasas bajas por más tiempo (forward guidance) "
                  "estimula hoy sin bajar nada hoy."),
        autores=("Ecuación de Euler (tradición Ramsey, mención); su papel como IS "
                 "del NK: Woodford (2003), Galí (2008) — menciones."),
        supuestos=[
            "Hogares racionales con previsión perfecta de la senda anunciada (la fe absoluta en el anuncio es el talón de Aquiles).",
            "Sin restricciones de liquidez: todos pueden mover consumo en el tiempo (los hogares 'mano a boca' rompen esto — mención).",
            "Terminal x=0: la economía vuelve al potencial al final (ancla de largo plazo, m22).",
        ],
        ecuaciones=[
            Ecuacion("x_t = x_{t+1} - \\sigma\\,(r_t - r_n)", "la IS de Euler",
                     "hoy consumo menos que mañana solo si la tasa real me paga por esperar: la "
                     "demanda ya no es una curva — es una recursión."),
            Ecuacion("x_0 = -\\sigma \\sum_{j=0}^{\\infty}(r_j - r_n)", "la demanda como precio de activo",
                     "el nivel de HOY descuenta la senda ENTERA: anunciar K períodos de apretón "
                     "equivale a K apretones hoy — el forward guidance es aritmética."),
        ],
        intuicion=("El hogar racional convierte cualquier anuncio en presente: si "
                   "el crédito será caro un año, adelanta el ahorro YA — y la "
                   "demanda cae hoy con la tasa de hoy intacta (verificado: x_0<0 "
                   "con r_0=r_n). El gráfico muestra la anti-intuición completa: la "
                   "brecha es más profunda ANTES del apretón que durante su final, "
                   "porque cada período que pasa quedan menos tasas futuras por "
                   "descontar."),
        equilibrio=("Con la senda anunciada y el ancla terminal, la trayectoria es "
                    "única (recursión hacia atrás, verificada contra la suma "
                    "cerrada). Sin ancla terminal habría múltiples equilibrios — la "
                    "sombra de la indeterminación que m56 controla con Taylor."),
        limitaciones=[
            "El forward guidance puzzle (mención): con esta ecuación pura, promesas MUY lejanas tienen efectos irrealmente grandes — atención limitada y descuento lo curan en la literatura.",
            "Previsión perfecta del anuncio: la credibilidad (m41) decide si el mercado descuenta la senda completa o la mitad.",
            "Sin restricciones de crédito: la potencia real del canal depende de cuántos hogares pueden intertemporalizar.",
        ],
        evolucion=("Es la mitad 'demanda' del modelo canónico: m55 hace lo mismo "
                   "con la oferta (NKPC forward-looking) y m56 cierra el sistema "
                   "con la regla de Taylor — donde esta suma de tasas futuras se "
                   "vuelve endógena a la política."),
    ),
    escenarios=[
        Escenario("apreton_anunciado", "hoy se anuncia: +1pp real por 4 períodos desde t=3",
                  {"t_ini": 3.0, "K": 4.0},
                  "la brecha cae a −4 DESDE t=0, tres períodos antes de que la tasa "
                  "se mueva: el anuncio ya hizo la mitad del trabajo.",
                  cadena=["anuncio creíble", "los hogares descuentan la senda entera",
                          "ahorran desde HOY", "x_0 = −σ·K·dr", "la tasa presente ni se tocó"]),
        Escenario("forward_guidance", "misma tasa, DOBLE duración anunciada (K=8)",
                  {"K": 8.0},
                  "el efecto de hoy se duplica exacto sin mover la tasa presente: "
                  "la herramienta que rescató a los bancos centrales en el ZLB.",
                  cadena=["prometer 'bajo por más tiempo' (o alto)", "más términos en la suma",
                          "x_0 escala con K", "política sin tocar la tasa de hoy"]),
        Escenario("hogares_sensibles", "σ = 2: intertemporalidad potente",
                  {"sigma": 2.0},
                  "el mismo anuncio pega el doble: economías con crédito profundo y "
                  "hogares planificadores amplifican la política de expectativas.",
                  cadena=["↑σ", "cada punto de tasa mueve más consumo",
                          "x_0 = −σKdr escala", "más potencia — y más fragilidad al anuncio"]),
    ],
    verificaciones=[
        Verificacion("x_0 = −σ·Σ(tasas futuras) exacto", _v_suma_de_futuras),
        Verificacion("forward guidance: duplicar K duplica el efecto hoy", _v_forward_guidance),
        Verificacion("el presente responde al futuro (x_0<0 con r_0=r_n)", _v_presente_responde_al_futuro),
        Verificacion("sin tasas futuras, brecha exactamente cero", _v_final_limpio),
    ],
    notas="La demanda como precio de activo: descontar el futuro es la nueva transmisión monetaria.",
)
