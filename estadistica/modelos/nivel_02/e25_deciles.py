"""simuladores/estadistica/modelos/nivel_02/e25_deciles.py — los deciles (sección II, tema 25).

Los deciles parten los datos ordenados en DIEZ grupos iguales: D1..D9 (los
percentiles 10, 20, …, 90), con D5 = la mediana. Son la herramienta estándar
para estudiar la DESIGUALDAD: al ordenar a la población por ingreso y partirla
en diez décimos, la razón entre el decil más alto y el más bajo —el índice
D9/D1— mide cuántas veces gana el 10% más rico respecto al 10% más pobre. El
modelo genera una distribución de ingresos (sesgada, como las reales) y deja
subir la desigualdad para ver el perfil de deciles empinarse y el índice D9/D1
dispararse.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_RNG = np.random.default_rng(2)
_Z = _RNG.standard_normal(4000)                      # ruido fijo → ingresos reproducibles


def _ingresos(sigma):
    return np.exp(7.0 + sigma * _Z) / 100.0          # lognormal: sesgada a la derecha (ingresos)


def _deciles(x):
    return [float(np.percentile(x, 10 * k)) for k in range(1, 10)]


def _curvas(p):
    x = _ingresos(p["sigma"])
    d = _deciles(x)
    ratio = d[8] / d[0]
    return {"lineas": {"ingreso en cada decil (D1…D9)": (np.arange(1, 10), np.array(d), config.AZUL2)},
            "puntos": [(1, d[0], f"D1={d[0]:.0f}"), (5, d[4], f"D5={d[4]:.0f} (mediana)"),
                       (9, d[8], f"D9={d[8]:.0f}")],
            "anotacion": (f"deciles: D1..D9 parten a la población en diez décimos\n"
                          f"D5 = {d[4]:.0f} = mediana; índice de desigualdad D9/D1 = {ratio:.1f}\n"
                          "el 10% más rico gana {:.0f} veces lo del 10% más pobre".format(ratio))}


def _resultados(p):
    x = _ingresos(p["sigma"])
    d = _deciles(x)
    return {"D1 (10% más pobre, umbral)": d[0],
            "D5 (mediana)": d[4],
            "D9 (10% más rico, umbral)": d[8],
            "índice D9/D1 (desigualdad)": d[8] / d[0],
            "índice D9/D5": d[8] / d[4],
            "media (comparación, > mediana por el sesgo)": float(x.mean())}


def _ecuaciones_calibradas(p):
    x = _ingresos(p["sigma"])
    d = _deciles(x)
    return [f"D_k = P_{{10k}}:\\ D_5 = {d[4]:.0f} = \\text{{mediana}};\\ D_1={d[0]:.0f},\\ D_9={d[8]:.0f}",
            f"\\text{{índice }} D_9/D_1 = {d[8]/d[0]:.1f}\\ \\text{{(desigualdad: veces que el 10\\% rico supera al pobre)}}"]


_P0 = {"sigma": 0.6}


def _v_d5_es_mediana():
    x = _ingresos(0.6)
    d = _deciles(x)
    return abs(d[4] - float(np.median(x))) < 1e-6, \
        (f"D5 = {d[4]:.0f} = la mediana: el quinto decil es el corte del 50%, igual que el percentil 50 (e24) "
         "y el segundo cuartil (e23) — todos son el mismo punto central")


def _v_deciles_son_percentiles():
    x = _ingresos(0.6)
    d = _deciles(x)
    ok = all(abs(d[k - 1] - float(np.percentile(x, 10 * k))) < 1e-6 for k in range(1, 10))
    return ok, \
        ("los deciles SON percentiles: Dₖ = percentil 10k (D1=P10, D2=P20, …, D9=P90) — deciles, cuartiles y "
         "mediana son cortes del mismo continuo de percentiles (e24)")


def _v_parten_en_decimos():
    x = _ingresos(0.6)
    d = _deciles(x)
    props = [np.mean(x <= d[k]) for k in range(9)]
    ok = all(abs(props[k] - (k + 1) / 10) < 0.03 for k in range(9))
    return ok, \
        ("los deciles parten en DIEZ décimos iguales: ~10% de la población entre deciles consecutivos — D1 deja "
         "el 10% por debajo, D9 el 90%; cada franja tiene la misma cantidad de gente")


def _v_ratio_mide_desigualdad():
    r_baja = _deciles(_ingresos(0.3))
    r_alta = _deciles(_ingresos(1.0))
    ratio_baja = r_baja[8] / r_baja[0]
    ratio_alta = r_alta[8] / r_alta[0]
    return ratio_alta > ratio_baja * 2, \
        (f"el índice D9/D1 mide desigualdad: sube de {ratio_baja:.1f} (dispersión baja) a {ratio_alta:.1f} "
         "(dispersión alta) — cuanto más se estira la distribución, más veces gana el decil rico respecto al pobre")


MODELO = Modelo(
    id="e25", nivel=2,
    nombre="Los deciles",
    xlabel="decil  (1 = más pobre … 9)", ylabel="ingreso en el umbral del decil",
    parametros=[
        Parametro("sigma", _P0["sigma"], 0.2, 1.2, 0.05, "Dispersión de ingresos (desigualdad)",
                  grupo="descriptiva", definicion="estira la distribución; a más dispersión, mayor el índice D9/D1"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si ordenamos a un país por ingreso y lo partimos en diez, ¿cuántas veces gana el décimo más rico respecto al más pobre?",
        variables=[("D1…D9", "los nueve deciles: percentiles 10, 20, …, 90"),
                   ("D5", "el quinto decil = la mediana"),
                   ("D9/D1", "índice de desigualdad: razón entre el decil rico y el pobre")],
        derivacion=["\\text{ordenar la población y partir en diez décimos iguales}",
                    "D_k = P_{10k} : \\text{umbral del décimo } k \\;(k=1,\\dots,9)",
                    "D_5 = \\text{mediana}",
                    "\\text{índice } D_9/D_1 : \\text{cuántas veces el decil 9 supera al 1}"],
        contexto=("Los deciles son percentiles de diez en diez —los cortes 10, 20, "
                  "…, 90— y su terreno natural es el estudio de la DESIGUALDAD. La "
                  "idea es simple y poderosa: ordena a toda la población por ingreso "
                  "(o riqueza, o cualquier variable) y pártela en diez grupos del "
                  "mismo tamaño; los deciles son los nueve umbrales que los separan. "
                  "El decil 5 es la mediana. Pero lo interesante son los extremos y "
                  "su razón: el índice D9/D1 —cuántas veces el ingreso del umbral del "
                  "10% más rico supera al del 10% más pobre— es una de las medidas "
                  "de desigualdad más usadas y más intuitivas, porque no depende de "
                  "supuestos: solo compara dos cortes de la distribución real. En "
                  "los países muy desiguales de América Latina, este índice puede "
                  "ser de 20, 30 o más (el umbral del décimo rico gana decenas de "
                  "veces lo del pobre); en los países nórdicos, cercano a 5. Los "
                  "deciles heredan las virtudes de todos los cuantiles: son "
                  "robustos, no suponen ninguna forma de la distribución y describen "
                  "posición. Y como los ingresos son fuertemente ASIMÉTRICOS "
                  "—sesgados a la derecha, con una cola larga de ricos—, los deciles "
                  "revelan algo que la media esconde: el ingreso PROMEDIO de un país "
                  "puede subir aunque el decil mediano no mejore, si toda la ganancia "
                  "se concentra en los deciles altos (la lección de e18: media ≫ "
                  "mediana señala cola derecha). Por eso los organismos serios "
                  "reportan la distribución por deciles, no solo el PIB per cápita "
                  "(un promedio): el crecimiento que no llega a los deciles bajos no "
                  "es desarrollo inclusivo. Los deciles son, en el fondo, la manera "
                  "de convertir 'la distribución' de una abstracción en diez números "
                  "que cuentan quién está dónde."),
        autores=("El análisis por deciles y los índices de desigualdad: economía y "
                 "estadística social (Pareto, Gini, s. XIX-XX) — menciones. "
                 "Conocimiento estadístico general."),
        supuestos=[
            "Datos al menos ordinales y una población que tenga sentido partir en diez (n razonablemente grande); con pocos datos los deciles extremos son inestables.",
            "El índice D9/D1 compara UMBRALES de deciles, no ingresos promedio de cada décimo (esa sería otra medida, más sensible a las colas); ambas se usan.",
            "La desigualdad tiene muchas medidas (D9/D1, Gini, Theil, Palma): los deciles dan una lectura transparente pero parcial (ignoran la forma dentro de cada décimo).",
        ],
        ecuaciones=[
            Ecuacion("D_k = P_{10k} \\quad (k = 1, \\dots, 9)", "los nueve deciles",
                     "los percentiles de diez en diez: parten la población en diez grupos iguales; D5 es la "
                     "mediana."),
            Ecuacion("D_9 / D_1", "índice de desigualdad decílica",
                     "cuántas veces el umbral del decil más rico supera al del más pobre: una medida "
                     "transparente de desigualdad que solo compara la distribución real."),
            Ecuacion("\\text{media} > D_5 \\;(\\text{ingresos sesgados})", "la media engaña",
                     "en distribuciones sesgadas a la derecha (ingresos) la media supera a la mediana (D5): el "
                     "promedio puede crecer aunque el décimo mediano no mejore."),
        ],
        intuicion=("Los deciles convierten la palabra 'distribución' en algo que se "
                   "puede señalar con el dedo: diez grupos, nueve líneas, y una "
                   "razón —D9/D1— que resume de un golpe cuán estirada está la "
                   "sociedad. Su lección más importante es política y estadística a "
                   "la vez: un PROMEDIO puede ocultar una distribución injusta. Un "
                   "país cuyo PIB per cápita crece 5% suena próspero, pero si todo "
                   "ese crecimiento se fue a los deciles 8, 9 y 10, el decil mediano "
                   "—la gente típica— no vio nada, y los deciles lo muestran sin "
                   "piedad. Por eso mirar la distribución por deciles antes de "
                   "celebrar un promedio es una forma de honestidad. La imagen del "
                   "perfil de deciles —una curva que sube suave en los décimos bajos "
                   "y se dispara en los altos— es el retrato de la desigualdad: "
                   "cuanto más se empina al final, más concentrado está el ingreso "
                   "arriba. Y conecta con toda la descriptiva: los deciles son "
                   "percentiles (e24), que generalizan cuartiles (e23) y mediana "
                   "(e18); su asimetría anticipa la ASIMETRÍA formal (e30); y su "
                   "razón D9/D1 es una prima del coeficiente de variación (e29) como "
                   "medida de dispersión relativa."),
        equilibrio=("Los deciles son únicos (dada la interpolación), monótonos "
                    "crecientes, con D5 = mediana. El índice D9/D1 crece con la "
                    "dispersión de la distribución (más desigualdad). En "
                    "distribuciones sesgadas, media > D5. No hay 'equilibrio': es la "
                    "anatomía de la distribución en diez cortes."),
        limitaciones=[
            "Ignoran la forma DENTRO de cada décimo: el índice D9/D1 no ve qué pasa entre los deciles (dos países con igual D9/D1 pueden diferir en el medio) — para eso están Gini, Theil, la curva de Lorenz.",
            "Los umbrales de deciles no son los ingresos PROMEDIO de cada grupo: comparar umbrales vs promedios da números distintos (los promedios de los deciles extremos son más sensibles a las colas).",
            "Deciles extremos inestables con pocos datos: D1 y D9 dependen de las colas, que necesitan muchas observaciones para estimarse bien.",
        ],
        evolucion=("Especializan los percentiles (e24) al análisis de la desigualdad "
                   "(índice D9/D1), cerrando el arco de los cuantiles: mediana (e18) "
                   "→ cuartiles (e23) → percentiles (e24) → deciles (e25). Su "
                   "asimetría anticipa la ASIMETRÍA (e30) y motiva medidas de "
                   "desigualdad más finas (Gini, Lorenz, Palma). En economía, son la "
                   "lente estándar para leer distribuciones de ingreso y evaluar si "
                   "el crecimiento es inclusivo — el complemento distributivo del "
                   "PIB per cápita (un promedio, m97 del macro-lab)."),
    ),
    escenarios=[
        Escenario("igualdad", "baja dispersión (sociedad más igualitaria)",
                  {"sigma": 0.3},
                  "con poca dispersión, los deciles están juntos y el índice D9/D1 "
                  "es bajo (~4): el décimo rico gana pocas veces lo del pobre. El "
                  "perfil de deciles es casi plano — una distribución compacta.",
                  cadena=["baja dispersión de ingresos", "los deciles están cerca unos de otros",
                          "D9/D1 bajo (~4, tipo nórdico)", "sociedad más igualitaria"]),
        Escenario("desigualdad", "alta dispersión (sociedad muy desigual)",
                  {"sigma": 1.0},
                  "con alta dispersión, la cola de ricos se estira: D9 se dispara "
                  "mientras D1 apenas se mueve, y el índice D9/D1 sube a 20+ (tipo "
                  "latinoamericano). El perfil de deciles se empina brutalmente al "
                  "final — el retrato de la concentración.",
                  cadena=["alta dispersión de ingresos", "la cola de ricos se estira (D9 sube)",
                          "D1 apenas cambia (el pobre sigue pobre)", "D9/D1 se dispara (20+): sociedad muy desigual"]),
    ],
    verificaciones=[
        Verificacion("D5 es la mediana", _v_d5_es_mediana),
        Verificacion("los deciles son percentiles (Dₖ = P₁₀ₖ)", _v_deciles_son_percentiles),
        Verificacion("los deciles parten la población en décimos", _v_parten_en_decimos),
        Verificacion("el índice D9/D1 mide desigualdad (crece con la dispersión)", _v_ratio_mide_desigualdad),
    ],
    notas="Deciles D1..D9 = percentiles 10..90 (D5=mediana): diez grupos iguales. El índice D9/D1 mide desigualdad (nórdicos ~5, latinoamericanos 20+). Revelan lo que el PROMEDIO esconde: el crecimiento que no llega a los deciles bajos no es inclusivo.",
)
