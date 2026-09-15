"""simuladores/estadistica/modelos/nivel_02/e18_mediana.py — la mediana (sección II, tema 18).

La contraparte robusta de la media. Si la media (e17) minimiza el error
CUADRÁTICO (Σ(xᵢ−a)²) y es su talón de Aquiles ante outliers, la mediana
minimiza el error ABSOLUTO (Σ|xᵢ−a|) y es inmune a ellos: parte los datos en
dos mitades y no le importa CUÁNTO de lejos está el valor extremo, solo de qué
lado. Punto de ruptura 50% (hay que corromper la mitad de los datos para
moverla). El modelo deja mover un candidato `a` y ver que el error absoluto es
mínimo en la mediana — la "V" que contrasta con la parábola de la media.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_DATOS = np.array([4, 5, 6, 7, 8, 9, 40], float)    # n=7, mediana=7, media≈11.3 (un outlier: 40)
_MEDIANA = float(np.median(_DATOS))
_MEDIA = float(_DATOS.mean())
_N = len(_DATOS)


def _l1(a):
    return float(np.sum(np.abs(_DATOS - a)))


def _curvas(p):
    a = p["a"]
    grid = np.linspace(1, 15, 200)
    l1 = np.array([_l1(x) for x in grid])
    return {"lineas": {"error absoluto total  $\\sum |x_i-a|$": (grid, l1, config.ROJO)},
            "puntos": [(_MEDIANA, _l1(_MEDIANA), f"mínimo en mediana = {_MEDIANA:.0f}"),
                       (a, _l1(a), f"tu a = {a:.1f}")]
                      + [(float(x), 0.0, "") for x in _DATOS if x <= 15],
            "anotacion": (f"datos: {', '.join(str(int(x)) for x in _DATOS)}\n"
                          f"mediana = {_MEDIANA:.0f} parte en dos mitades; media = {_MEDIA:.1f} (arrastrada por el 40)\n"
                          f"la mediana MINIMIZA el error absoluto: |·| en {_MEDIANA:.0f}, no {_MEDIA:.1f}")}


def _resultados(p):
    a = p["a"]
    return {"mediana": _MEDIANA,
            "media (comparación)": _MEDIA,
            "datos por debajo de la mediana": float(np.sum(_DATOS < _MEDIANA)),
            "datos por encima": float(np.sum(_DATOS > _MEDIANA)),
            "error absoluto en tu a: Σ|xᵢ−a|": _l1(a),
            "error absoluto en la mediana (mínimo)": _l1(_MEDIANA),
            "|media − mediana| (efecto del outlier)": abs(_MEDIA - _MEDIANA)}


def _ecuaciones_calibradas(p):
    return [f"\\text{{mediana}} = {_MEDIANA:.0f}\\qquad \\text{{media}} = {_MEDIA:.1f}\\ \\text{{(arrastrada por el outlier)}}",
            f"\\text{{mediana}} = \\arg\\min_a \\sum |x_i-a|\\qquad \\text{{ruptura}} = 50\\%"]


_P0 = {"a": 7.0}


def _v_parte_en_dos():
    debajo = int(np.sum(_DATOS < _MEDIANA))
    encima = int(np.sum(_DATOS > _MEDIANA))
    return debajo == encima, \
        (f"la mediana ({_MEDIANA:.0f}) parte los datos en dos mitades iguales: {debajo} por debajo y {encima} "
         "por encima — es el valor central, el que deja la mitad a cada lado (percentil 50, e24)")


def _v_minimiza_l1():
    grid = np.linspace(1, 20, 3801)
    argmin = grid[int(np.argmin([_l1(x) for x in grid]))]
    return abs(argmin - _MEDIANA) < 0.02, \
        (f"la mediana MINIMIZA el error absoluto: argmin_a Σ|xᵢ−a| = {argmin:.2f} = mediana = {_MEDIANA:.0f}. "
         "Igual que la media minimiza el error CUADRÁTICO (e17), pero con |·| en vez de (·)² — otra pérdida, otro óptimo")


def _v_robusta():
    # mover el outlier 40 → 400 no cambia la mediana (punto de ruptura 50%)
    datos_peor = _DATOS.copy(); datos_peor[-1] = 400.0
    med_peor = float(np.median(datos_peor))
    return med_peor == _MEDIANA, \
        (f"llevar el outlier de 40 a 400 NO mueve la mediana (sigue en {_MEDIANA:.0f}): es ROBUSTA, punto de "
         "ruptura 50% — a la mediana solo le importa de qué LADO está el dato, no cuán lejos (a la media sí, e17)")


def _v_vs_media_sesgo():
    return abs(_MEDIA - _MEDIANA) > 3, \
        (f"con un outlier, media ({_MEDIA:.1f}) y mediana ({_MEDIANA:.0f}) DIVERGEN: la media se va tras el 40, "
         "la mediana se queda con el grueso — por eso el 'ingreso mediano' describe mejor a la gente típica que el 'promedio'")


MODELO = Modelo(
    id="e18", nivel=2,
    nombre="La mediana",
    xlabel="candidato de centro  a", ylabel="error absoluto total",
    parametros=[
        Parametro("a", _P0["a"], 1.0, 15.0, 0.5, "Candidato de centro a",
                  grupo="descriptiva", definicion="valor de prueba; el error absoluto Σ|xᵢ−a| es mínimo en la mediana"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando hay un dato extremo, ¿por qué la mediana describe mejor 'lo típico' que el promedio?",
        variables=[("x₍₁₎…x₍ₙ₎", "los datos ordenados"),
                   ("mediana", "el valor central: parte la muestra en dos mitades"),
                   ("a", "candidato de centro (para ver qué minimiza la mediana)"),
                   ("Σ|xᵢ−a|", "error absoluto total respecto a a")],
        derivacion=["\\text{ordenar los datos: } x_{(1)} \\leq \\dots \\leq x_{(n)}",
                    "n \\text{ impar}: \\; \\text{mediana} = x_{((n+1)/2)} \\;(\\text{el del medio})",
                    "n \\text{ par}: \\; \\text{mediana} = \\tfrac{1}{2}\\big(x_{(n/2)} + x_{(n/2+1)}\\big)",
                    "\\text{propiedad}: \\; \\text{mediana} = \\arg\\min_a \\sum |x_i-a|"],
        contexto=("La mediana responde a la misma pregunta que la media —¿cuál es el "
                  "'centro' de estos datos?— pero con una regla del juego distinta, y "
                  "esa diferencia lo cambia todo cuando hay valores extremos. La "
                  "media minimiza el error al CUADRADO, y elevar al cuadrado hace que "
                  "un dato lejano pese enormemente: por eso un solo millonario "
                  "dispara el ingreso 'promedio' de un barrio pobre a una cifra que "
                  "no describe a nadie. La mediana, en cambio, minimiza el error "
                  "ABSOLUTO (sin elevar al cuadrado), y al no castigar la magnitud "
                  "de la distancia sino solo el LADO, es indiferente a cuán "
                  "estrafalario sea el outlier. Operativamente es el valor que parte "
                  "los datos ordenados en dos mitades: la mitad queda por debajo, la "
                  "mitad por encima. Su virtud es la ROBUSTEZ: su punto de ruptura es "
                  "50% —habría que corromper la mitad de las observaciones para "
                  "moverla arbitrariamente—, frente al 0% de la media (a la que un "
                  "solo dato basta para arrastrar sin límite). Por eso, cuando los "
                  "datos son asimétricos o tienen atípicos —ingresos, precios de "
                  "vivienda, tiempos de espera—, los estadísticos serios reportan la "
                  "mediana: describe a la persona TÍPICA, no al promedio distorsionado. "
                  "El precio de esa robustez es que la mediana ignora información "
                  "(no le importa si el dato de arriba es 10 o 10.000), así que es "
                  "menos eficiente que la media cuando NO hay atípicos y los datos "
                  "son simétricos. Media y mediana no compiten: resuelven problemas "
                  "distintos (pérdida cuadrática vs absoluta), y saber cuál usar es "
                  "leer bien la forma de los datos."),
        autores=("La mediana como estadístico: Galton la popularizó (s. XIX) con "
                 "ese nombre; la propiedad de minimizar el error absoluto y el punto "
                 "de ruptura: estadística robusta (Tukey, Huber, s. XX) — menciones. "
                 "Conocimiento estadístico general."),
        supuestos=[
            "Datos al menos ORDINALES: la mediana solo necesita poder ordenar (no requiere distancias, a diferencia de la media) — sirve para variables ordinales donde la media no.",
            "Con n impar la mediana es un dato; con n par es el promedio de los dos centrales (una convención).",
            "El interés es el centro bajo pérdida ABSOLUTA (o la robustez ante atípicos); si los datos son simétricos y limpios, la media es más eficiente.",
        ],
        ecuaciones=[
            Ecuacion("\\text{mediana} = x_{((n+1)/2)} \\;(n\\text{ impar})", "el valor central",
                     "ordenados los datos, la mediana es el del medio: deja la mitad de las observaciones a "
                     "cada lado — el percentil 50 (e24)."),
            Ecuacion("\\text{mediana} = \\arg\\min_a \\sum |x_i - a|", "minimiza el error absoluto",
                     "de todos los centros posibles, la mediana es el que minimiza la suma de distancias "
                     "absolutas — el análogo de la media, pero con |·| en vez de (·)²."),
            Ecuacion("\\text{punto de ruptura} = 50\\%", "robustez",
                     "hay que corromper la MITAD de los datos para mover la mediana sin control; a la media "
                     "le basta un solo dato (0%) — la mediana es el centro robusto."),
        ],
        intuicion=("La imagen es una fila de personas ordenadas por estatura: la "
                   "mediana es simplemente la persona del medio, y da igual si el "
                   "más alto mide 2 metros o 3 —sigue siendo el mismo del medio—. "
                   "La media, en cambio, si al más alto lo reemplazamos por un "
                   "gigante de 10 metros, se dispara, aunque nadie más haya "
                   "cambiado. Esa es toda la diferencia: la mediana cuenta POSICIONES "
                   "(¿de qué lado caes?), la media pesa MAGNITUDES (¿cuán lejos "
                   "estás?). Por eso la mediana es la medida de los datos 'sucios' "
                   "del mundo real —ingresos con multimillonarios, precios con "
                   "mansiones, tiempos con casos patológicos— y la razón por la que "
                   "los organismos serios reportan el ingreso MEDIANO de un país, no "
                   "el promedio: el promedio sube cuando los ricos se hacen más "
                   "ricos aunque el resto no cambie; la mediana solo sube si mejora "
                   "la persona del medio. La contracara: al ignorar magnitudes, la "
                   "mediana tira información, y con datos limpios y simétricos la "
                   "media aprovecha mejor los datos (es más eficiente). La regla "
                   "práctica: si media ≈ mediana, los datos son simétricos y da "
                   "igual; si media ≫ mediana, hay cola a la derecha (outliers "
                   "altos) y la mediana es la honesta."),
        equilibrio=("La mediana es el argmin de Σ|xᵢ−a| (único si n impar; un "
                    "intervalo si n par). Parte los datos 50/50 y tiene punto de "
                    "ruptura 50% — el centro robusto. Diverge de la media cuando los "
                    "datos son asimétricos: media≫mediana señala cola derecha."),
        limitaciones=[
            "Ignora magnitudes: no distingue un dato de arriba en 10 de uno en 10.000 — esa robustez cuesta información; con datos simétricos y limpios la media es más eficiente.",
            "Menos tratable algebraicamente: no tiene una fórmula suave como la media (no se deriva igual), lo que complica su teoría de muestreo (aunque hay resultados asintóticos).",
            "Con n par la 'mediana' es una convención (promedio de los dos centrales); y en variables muy discretas puede caer entre valores sin sentido sustantivo.",
        ],
        evolucion=("Completa el par con la media (e17): misma pregunta, pérdidas "
                   "distintas (absoluta vs cuadrática), robustez opuesta (50% vs "
                   "0%). Generaliza a los CUANTILES —cuartiles (e23), percentiles "
                   "(e24), deciles (e25)—, siendo la mediana el percentil 50. Su "
                   "robustez es el tema de las medidas robustas (e32) y la detección "
                   "de atípicos (e33), donde se une con la MAD (desviación absoluta "
                   "mediana). Con la moda (e19) completa las medidas de tendencia "
                   "central."),
    ),
    escenarios=[
        Escenario("candidato_bajo", "probar un centro bajo (a = 4)",
                  {"a": 4.0},
                  "con a=4 el error absoluto sube respecto al mínimo: mover el "
                  "candidato por debajo de la mediana deja más distancia total. La "
                  "'V' de Σ|xᵢ−a| sube hacia la izquierda.",
                  cadena=["elegir a = 4 (< mediana)", "más datos quedan a la derecha que a la izquierda",
                          "el error absoluto Σ|xᵢ−a| aumenta", "solo la mediana lo minimiza"]),
        Escenario("candidato_en_media", "probar el centro en la MEDIA (a = 11.3)",
                  {"a": 11.0},
                  "poner el candidato en la media (arrastrada por el outlier) da MÁS "
                  "error absoluto que la mediana: para la pérdida absoluta, la media "
                  "es un mal centro justamente por dejarse llevar por el 40.",
                  cadena=["elegir a ≈ media (11.3, tras el outlier)", "la media está lejos del grueso de los datos",
                          "el error absoluto es mayor que en la mediana", "confirma: para |·|, la mediana gana"]),
    ],
    verificaciones=[
        Verificacion("la mediana parte los datos en dos mitades", _v_parte_en_dos),
        Verificacion("la mediana minimiza el error absoluto Σ|xᵢ−a|", _v_minimiza_l1),
        Verificacion("la mediana es robusta (punto de ruptura 50%)", _v_robusta),
        Verificacion("con outlier, media y mediana divergen", _v_vs_media_sesgo),
    ],
    notas="La mediana minimiza el error ABSOLUTO Σ|xᵢ−a| (la media minimiza el cuadrático, e17) y es ROBUSTA (ruptura 50% vs 0%). Cuenta posiciones, no magnitudes: describe a la persona típica. media≫mediana ⇒ cola derecha.",
)
