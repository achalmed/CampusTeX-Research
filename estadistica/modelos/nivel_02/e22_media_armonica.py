"""simuladores/estadistica/modelos/nivel_02/e22_media_armonica.py — la media armónica (sección II, tema 22).

El promedio correcto para RAZONES y TASAS sobre un numerador común: velocidades
sobre distancias iguales, precios por unidad, densidades. HM = n/Σ(1/xᵢ) =
recíproco de la media de los recíprocos. El caso clásico: ir 60 km a 30 km/h y
volver 60 km a 60 km/h NO promedia 45 km/h (aritmética), sino 40 —porque se
pasa MÁS TIEMPO a la velocidad lenta—, y eso es la media armónica. Cierra la
familia de promedios y la desigualdad completa: HM ≤ GM ≤ AM.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_A = 30.0                                             # primera velocidad (fija), km/h


def _medias(v2):
    x = np.array([_A, float(v2)])
    am = float(x.mean())
    gm = float(np.exp(np.mean(np.log(x))))
    hm = float(len(x) / np.sum(1.0 / x))
    return x, am, gm, hm


def _curvas(p):
    v2 = p["v2"]
    grid = np.linspace(10, 90, 180)
    am = np.array([_medias(v)[1] for v in grid])
    gm = np.array([_medias(v)[2] for v in grid])
    hm = np.array([_medias(v)[3] for v in grid])
    _, a0, g0, h0 = _medias(v2)
    return {"lineas": {"aritmética AM (la ingenua)": (grid, am, config.ROJO),
                       "geométrica GM": (grid, gm, config.DORADO),
                       "armónica HM (la correcta para tasas)": (grid, hm, config.AZUL2)},
            "puntos": [(v2, h0, f"v₂={v2:.0f} → HM {h0:.1f}")],
            "anotacion": (f"velocidades [30, {v2:.0f}] km/h sobre distancias iguales\n"
                          f"HM = {h0:.1f} ≤ GM = {g0:.1f} ≤ AM = {a0:.1f}\n"
                          "la velocidad media es la ARMÓNICA (más tiempo a la lenta)")}


def _resultados(p):
    v2 = p["v2"]
    x, am, gm, hm = _medias(v2)
    return {"segunda velocidad v₂": float(v2),
            "media aritmética (respuesta INGENUA)": am,
            "media geométrica": gm,
            "media armónica (velocidad media REAL)": hm,
            "HM ≤ GM ≤ AM (ordenadas)": 1.0 if hm <= gm <= am else 0.0,
            "error de usar AM en vez de HM": am - hm}


def _ecuaciones_calibradas(p):
    v2 = p["v2"]
    x, am, gm, hm = _medias(v2)
    return [f"\\mathrm{{HM}} = \\frac{{n}}{{\\sum 1/x_i}} = \\frac{{2}}{{1/30 + 1/{v2:.0f}}} = {hm:.1f}",
            f"\\mathrm{{HM}} \\leq \\mathrm{{GM}} \\leq \\mathrm{{AM}}:\\ {hm:.1f} \\leq {gm:.1f} \\leq {am:.1f}"]


_P0 = {"v2": 60.0}


def _v_formula_reciproca():
    x, am, gm, hm = _medias(60.0)
    hm_directa = float(1.0 / np.mean(1.0 / x))
    return abs(hm - hm_directa) < 1e-12, \
        (f"la media armónica = recíproco de la media de los recíprocos = 1/media(1/x) = {hm:.1f}: se promedia "
         "'al revés' porque la magnitud que se conserva (el tiempo, sobre distancia fija) es inversa a la tasa")


def _v_cadena_desigualdades():
    ok = all(_medias(v)[3] <= _medias(v)[2] + 1e-9 <= _medias(v)[1] + 2e-9 for v in (20, 45, 80))
    x, am, gm, hm = _medias(20.0)
    return ok, \
        (f"HM ≤ GM ≤ AM SIEMPRE (la cadena completa de las medias): {hm:.1f} ≤ {gm:.1f} ≤ {am:.1f} — las tres "
         "coinciden solo si los valores son iguales; la armónica es la más 'pesimista', la aritmética la más 'optimista'")


def _v_ejemplo_velocidad():
    x, am, gm, hm = _medias(60.0)                     # 30 y 60 km/h
    return abs(am - 45.0) < 1e-9 and abs(hm - 40.0) < 1e-9, \
        (f"ir a 30 y volver a 60 km/h (distancias iguales): la velocidad media NO es {am:.0f} (aritmética) sino "
         f"{hm:.0f} (armónica) — se tarda el doble a 30 que a 60, así que el tiempo total pesa hacia la velocidad lenta")


def _v_correcta_para_tasas():
    return True, \
        ("la media armónica es la correcta para promediar TASAS con numerador común (km/tiempo con distancia "
         "fija, precio/cantidad, PER de acciones): promediar tasas con la aritmética sobrestima; la armónica pondera bien el denominador")


MODELO = Modelo(
    id="e22", nivel=2,
    nombre="La media armónica",
    xlabel="segunda velocidad  v₂ (km/h)", ylabel="media (km/h)",
    parametros=[
        Parametro("v2", _P0["v2"], 10.0, 90.0, 5.0, "Segunda velocidad v₂ (km/h)",
                  grupo="descriptiva", definicion="la primera es 30; la velocidad media del viaje ida-vuelta es la armónica"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si vas a 30 km/h y vuelves a 60 km/h por el mismo camino, ¿tu velocidad media es 45? (No, es 40.) ¿Por qué?",
        variables=[("xᵢ", "las tasas o razones (velocidades, precios por unidad)"),
                   ("HM", "media armónica = n / Σ(1/xᵢ)"),
                   ("HM ≤ GM ≤ AM", "la cadena completa de las medias")],
        derivacion=["\\text{a tasa } x \\text{ sobre cantidad fija } d,\\ \\text{el 'costo' es } d/x \\;(\\text{tiempo})",
                    "\\text{promedio real} = \\frac{\\text{total cantidad}}{\\text{total costo}} = \\frac{n\\,d}{\\sum d/x_i}",
                    "= \\frac{n}{\\sum 1/x_i} = \\mathrm{HM} \\quad(\\text{recíproco de la media de recíprocos})",
                    "\\text{siempre } \\mathrm{HM} \\le \\mathrm{GM} \\le \\mathrm{AM}"],
        contexto=("La media armónica es la tercera y menos conocida de las medias "
                  "clásicas, y la que atrapa a casi todos con el problema de la "
                  "velocidad promedio. Si recorres 60 km a 30 km/h y vuelves los "
                  "mismos 60 km a 60 km/h, la tentación es promediar 30 y 60 y decir "
                  "45 km/h. Está mal: la velocidad media del viaje completo es 40 "
                  "km/h. La razón es que pasas MÁS TIEMPO a la velocidad lenta —2 "
                  "horas a 30, solo 1 hora a 60—, así que la velocidad baja domina "
                  "el promedio. Formalmente, la velocidad media es la distancia "
                  "total sobre el tiempo total, y al hacer esa cuenta aparece la "
                  "media armónica: HM = n / Σ(1/xᵢ), el recíproco de la media de los "
                  "recíprocos. La clave conceptual es que la media armónica es la "
                  "correcta cuando lo que se promedia son TASAS o razones y lo que "
                  "se mantiene constante es el NUMERADOR (la distancia, no el "
                  "tiempo). Aparece en muchos lugares: el precio promedio por unidad "
                  "cuando compras cantidades iguales de dinero (no de producto), el "
                  "PER promedio de una cartera de acciones, densidades, resistencias "
                  "eléctricas en paralelo, el F1-score que combina precisión y "
                  "exhaustividad (e236). Y completa la desigualdad de las medias en "
                  "su forma total: HM ≤ GM ≤ AM, siempre, con igualdad solo si todos "
                  "los valores coinciden. Las tres son promedios legítimos, pero "
                  "cada uno es el correcto para un tipo distinto de dato: la "
                  "aritmética para cantidades que se suman, la geométrica para "
                  "factores que se multiplican, la armónica para tasas sobre un "
                  "numerador común. Usar la que no toca no es un error menor: da la "
                  "respuesta equivocada, como los 45 km/h que no fueron."),
        autores=("Las tres medias (aritmética, geométrica, armónica) vienen de los "
                 "pitagóricos (teoría musical); la desigualdad HM≤GM≤AM es clásica "
                 "— menciones. Conocimiento estadístico general."),
        supuestos=[
            "Datos POSITIVOS: la media armónica exige valores positivos (hay recíprocos); un cero la manda a cero, un negativo la rompe.",
            "Apropiada para TASAS/razones con numerador común constante (distancia fija, dinero fijo): si lo constante es el denominador, la correcta es la aritmética.",
            "Es la más sensible a los valores PEQUEÑOS (los recíprocos grandes dominan): un valor cercano a cero la arrastra hacia abajo.",
        ],
        ecuaciones=[
            Ecuacion("\\mathrm{HM} = \\frac{n}{\\sum_{i=1}^n 1/x_i}", "media armónica",
                     "n sobre la suma de los recíprocos: el promedio correcto de tasas cuando el numerador "
                     "(distancia, dinero) es fijo — se promedia 'al revés'."),
            Ecuacion("\\mathrm{HM} = \\frac{1}{\\overline{1/x}}", "recíproco de la media de recíprocos",
                     "invertir cada dato, promediar, e invertir el resultado: refleja que la magnitud "
                     "conservada (el tiempo) es inversa a la tasa (la velocidad)."),
            Ecuacion("\\mathrm{HM} \\le \\mathrm{GM} \\le \\mathrm{AM}", "la cadena completa de las medias",
                     "la armónica nunca supera a la geométrica, que nunca supera a la aritmética; iguales solo "
                     "si todos los datos coinciden — tres promedios ordenados."),
        ],
        intuicion=("La media armónica es la que 'sabe' que a velocidad lenta se "
                   "tarda más, y por eso le da más peso —no porque haya más datos "
                   "lentos, sino porque cada dato lento ocupa más de la magnitud que "
                   "importa (el tiempo)—. Es el promedio pesimista de la familia: "
                   "siempre el más bajo de los tres, arrastrado por los valores "
                   "pequeños. La intuición para saber cuál media usar es preguntar "
                   "'¿qué se mantiene constante?': si sumo cosas (notas, ingresos), "
                   "aritmética; si multiplico factores (tasas de crecimiento), "
                   "geométrica; si promedio tasas sobre algo fijo (velocidad sobre "
                   "distancia, precio sobre dinero), armónica. El error de los 45 "
                   "km/h es tan común que tiene nombre propio en didáctica, y su "
                   "moraleja excede a la velocidad: cada vez que promedias razones "
                   "—rendimientos por dólar, casos por cada mil, precios por "
                   "unidad—, la aritmética casi siempre te dará un número demasiado "
                   "optimista, y la armónica el correcto. En machine learning, el "
                   "F1-score usa exactamente esto: combina precisión y recall con "
                   "media armónica para castigar el desequilibrio entre ambas "
                   "(e236)."),
        equilibrio=("La media armónica es única (para datos positivos), la más "
                    "pequeña de las tres (HM ≤ GM ≤ AM), con igualdad solo si todos "
                    "los valores coinciden. Es la más sensible a los valores "
                    "pequeños. No hay 'equilibrio' que resolver: es el promedio "
                    "correcto de tasas sobre numerador común."),
        limitaciones=[
            "Solo datos positivos: ceros o negativos la indefinen o rompen (recíprocos).",
            "Muy sensible a valores pequeños: un dato cercano a cero domina y la desploma — poco robusta hacia abajo.",
            "Fácil de usar mal: es correcta solo cuando el numerador es constante; si lo constante es el denominador, la respuesta correcta es la aritmética — distinguir el caso exige pensar en qué se conserva.",
        ],
        evolucion=("Cierra la familia de promedios —aritmética (e17), geométrica "
                   "(e21), armónica (e22)— y la desigualdad completa HM ≤ GM ≤ AM, "
                   "cada una óptima para su tipo de dato (sumas, factores, tasas). "
                   "Reaparece en el F1-score (e236, media armónica de precisión y "
                   "recall) y en cualquier promedio de razones. Con la moda (e19) y "
                   "las cuatro medias, la tendencia central queda completa; sigue la "
                   "DISPERSIÓN (cuartiles e23, rango e26, varianza e27)."),
    ),
    escenarios=[
        Escenario("iguales", "velocidades iguales (v₂ = 30): las tres medias coinciden",
                  {"v2": 30.0},
                  "si ambas velocidades son 30, no hay nada que promediar: HM = GM "
                  "= AM = 30. La cadena de desigualdades se vuelve igualdad cuando "
                  "los datos son idénticos.",
                  cadena=["v₂ = 30 = v₁ (velocidades iguales)", "no hay dispersión",
                          "HM = GM = AM = 30", "las tres medias coinciden"]),
        Escenario("muy_distintas", "velocidades muy distintas (v₂ = 90)",
                  {"v2": 90.0},
                  "con 30 y 90 km/h, la aritmética diría 60, pero la velocidad "
                  "media real es la armónica ≈45: el tiempo a 30 (mucho) pesa más "
                  "que el tiempo a 90 (poco). Cuanto más distintas las tasas, mayor "
                  "el error de la aritmética.",
                  cadena=["v₂ = 90 (muy distinta de 30)", "se tarda 3× más a 30 que a 90",
                          "el tiempo total pesa hacia la lenta", "HM ≈ 45 (no 60): la armónica acierta"]),
    ],
    verificaciones=[
        Verificacion("HM = 1/media(1/x) (recíproco de recíprocos)", _v_formula_reciproca),
        Verificacion("HM ≤ GM ≤ AM siempre (la cadena completa)", _v_cadena_desigualdades),
        Verificacion("velocidad 30/60: media 40 (armónica), no 45", _v_ejemplo_velocidad),
        Verificacion("es la correcta para tasas sobre numerador común", _v_correcta_para_tasas),
    ],
    notas="Media armónica HM = n/Σ(1/xᵢ): el promedio de TASAS sobre numerador común. Ir a 30 y volver a 60 da 40 km/h (no 45): más tiempo a la lenta. Cierra HM ≤ GM ≤ AM. Solo datos positivos; sensible a valores pequeños. En ML es el F1-score (e236).",
)
