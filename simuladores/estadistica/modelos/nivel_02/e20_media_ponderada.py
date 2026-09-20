"""simuladores/estadistica/modelos/nivel_02/e20_media_ponderada.py — la media ponderada (sección II, tema 20).

La media cuando las observaciones NO pesan igual. La media simple (e17) da a
cada dato el mismo peso 1/n; la ponderada le da a cada uno un peso wᵢ y calcula
Σwᵢxᵢ/Σwᵢ. Es el promedio correcto cuando los datos representan cantidades
distintas: el promedio ponderado de notas por créditos (el "promedio
ponderado" académico), el rendimiento de una cartera por monto invertido, un
índice de precios por participación. El modelo deja subir el peso de un valor
y ver la media desplazarse hacia él, siempre entre el mínimo y el máximo.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config

_X = np.array([4.0, 6.0, 10.0])                      # tres valores (p.ej. notas)
_W12 = np.array([1.0, 1.0])                          # pesos fijos de los dos primeros
_SIMPLE = float(_X.mean())                           # media simple = 20/3 ≈ 6.67


def _ponderada(w3):
    w = np.array([_W12[0], _W12[1], float(w3)])
    return float(np.sum(w * _X) / np.sum(w))


def _curvas(p):
    w3 = p["w3"]
    grid = np.linspace(0.2, 10, 160)
    mp = np.array([_ponderada(w) for w in grid])
    return {"lineas": {"media ponderada (según el peso del 10)": (grid, mp, config.AZUL2),
                       f"media simple = {_SIMPLE:.2f}": (grid, np.full(len(grid), _SIMPLE), config.GRIS),
                       "máximo = 10": (grid, np.full(len(grid), 10.0), config.ROJO)},
            "puntos": [(w3, _ponderada(w3), f"peso={w3:.1f} → media {_ponderada(w3):.2f}")],
            "anotacion": (f"valores {list(_X.astype(int))}, pesos [1, 1, {w3:.1f}]\n"
                          f"media ponderada = Σwᵢxᵢ/Σwᵢ = {_ponderada(w3):.2f}\n"
                          "más peso al 10 la acerca al 10; siempre entre el mín y el máx")}


def _resultados(p):
    w3 = p["w3"]
    w = np.array([_W12[0], _W12[1], float(w3)])
    return {"media ponderada": _ponderada(w3),
            "media simple (pesos iguales)": _SIMPLE,
            "peso del valor 10 (w₃)": float(w3),
            "suma de pesos Σwᵢ": float(np.sum(w)),
            "mínimo de los datos": float(_X.min()),
            "máximo de los datos": float(_X.max())}


def _ecuaciones_calibradas(p):
    w3 = p["w3"]
    return [f"\\bar x_w = \\frac{{\\sum w_i x_i}}{{\\sum w_i}} = \\frac{{4+6+10\\cdot {w3:.1f}}}{{2+{w3:.1f}}} = {_ponderada(w3):.2f}",
            f"\\text{{pesos iguales}} \\Rightarrow \\bar x_w = \\bar x\\ \\text{{(media simple)}} = {_SIMPLE:.2f}"]


_P0 = {"w3": 1.0}


def _v_reduce_a_simple():
    return abs(_ponderada(1.0) - _SIMPLE) < 1e-9, \
        (f"con pesos iguales (w₃=1) la media ponderada = media simple ({_SIMPLE:.2f}): la media simple es el "
         "caso particular de pesos todos iguales — no son dos fórmulas distintas, una contiene a la otra")


def _v_entre_min_y_max():
    valores = [_ponderada(w) for w in (0.2, 1, 3, 10)]
    return all(_X.min() <= v <= _X.max() for v in valores), \
        (f"la media ponderada SIEMPRE cae entre el mínimo ({_X.min():.0f}) y el máximo ({_X.max():.0f}) de los "
         "datos, sea cual sea el peso: es un promedio (combinación convexa), no puede salirse del rango")


def _v_monotona():
    return _ponderada(10.0) > _ponderada(1.0) > _ponderada(0.2), \
        (f"más peso al valor alto (10) sube la media: {_ponderada(0.2):.2f} → {_ponderada(1.0):.2f} → "
         f"{_ponderada(10.0):.2f} — la media ponderada se mueve hacia los datos que más pesan (créditos, montos, participación)")


def _v_formula():
    w3 = 3.0
    w = np.array([1.0, 1.0, w3])
    directa = float(np.sum(w * _X) / np.sum(w))
    return abs(directa - _ponderada(w3)) < 1e-12, \
        (f"media ponderada = Σwᵢxᵢ/Σwᵢ = {np.sum(w*_X):.0f}/{np.sum(w):.0f} = {directa:.2f}: cada dato aporta "
         "proporcional a su peso — el promedio 'justo' cuando las observaciones representan cantidades distintas")


MODELO = Modelo(
    id="e20", nivel=2,
    nombre="La media ponderada",
    xlabel="peso del valor 10  (w₃)", ylabel="valor de la media",
    parametros=[
        Parametro("w3", _P0["w3"], 0.2, 10.0, 0.2, "Peso del valor 10 (w₃)",
                  grupo="descriptiva", definicion="cuánto pesa la observación alta; a más peso, la media se acerca a 10"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Cuando unas observaciones cuentan más que otras (créditos, montos, participación), ¿cómo se promedia?",
        variables=[("xᵢ", "los valores"),
                   ("wᵢ", "el peso de cada valor (créditos, monto, importancia)"),
                   ("x̄_w", "media ponderada = Σwᵢxᵢ / Σwᵢ")],
        derivacion=["\\text{media simple: cada dato pesa } 1/n \\Rightarrow \\bar x = \\tfrac{1}{n}\\sum x_i",
                    "\\text{si los datos pesan distinto } (w_i) \\Rightarrow \\bar x_w = \\frac{\\sum w_i x_i}{\\sum w_i}",
                    "\\text{pesos iguales } (w_i = w) \\Rightarrow \\bar x_w = \\bar x \\;(\\text{caso particular})"],
        contexto=("Muchas veces las observaciones no son intercambiables: unas "
                  "representan más que otras, y promediarlas por igual engaña. El "
                  "ejemplo que todo estudiante conoce es el promedio PONDERADO de "
                  "notas: un curso de 5 créditos debe pesar más en tu promedio que "
                  "uno de 2, porque representa más horas de trabajo; promediar las "
                  "notas 'a secas' (media simple) trataría ambos igual y "
                  "distorsionaría el resultado. La media ponderada resuelve esto "
                  "dándole a cada dato un peso wᵢ y calculando Σwᵢxᵢ/Σwᵢ: la suma de "
                  "los valores multiplicados por sus pesos, dividida por la suma de "
                  "los pesos. Aparece en todas partes: el rendimiento de una cartera "
                  "de inversión (cada activo pesa según el monto invertido), un "
                  "índice de precios como el IPC (cada bien pesa según su "
                  "participación en el gasto, e83 del macro-lab), el promedio de "
                  "satisfacción de una empresa (cada sucursal pesa según su número "
                  "de clientes). La relación con la media simple es esclarecedora: "
                  "la media simple NO es una fórmula distinta, es el caso particular "
                  "de la ponderada cuando todos los pesos son iguales —cada dato "
                  "pesa 1/n—. Y como es un promedio genuino (una combinación "
                  "convexa), la media ponderada siempre cae entre el mínimo y el "
                  "máximo de los datos, por más desiguales que sean los pesos: "
                  "ponderar redistribuye la influencia, no inventa valores fuera de "
                  "rango. La clave práctica está en elegir bien los pesos: pesos mal "
                  "escogidos (o manipulados) hacen que el 'promedio' diga lo que uno "
                  "quiera —de ahí que la transparencia sobre CÓMO se pondera sea "
                  "tan importante en índices oficiales—."),
        autores=("La media ponderada es tan antigua como la contabilidad y la "
                 "astronomía (promediar observaciones de distinta calidad con pesos "
                 "inversos a su error, Gauss) — mención histórica. Conocimiento "
                 "estadístico general."),
        supuestos=[
            "Los pesos wᵢ son no negativos y representan la 'importancia' o 'cantidad' de cada observación (créditos, monto, frecuencia, fiabilidad).",
            "Datos cuantitativos (se multiplican por pesos y se promedian): la ponderación exige distancias con sentido.",
            "La elección de los pesos es sustantiva, no estadística: cambiar los pesos cambia el resultado, así que deben justificarse y ser transparentes.",
        ],
        ecuaciones=[
            Ecuacion("\\bar x_w = \\frac{\\sum w_i x_i}{\\sum w_i}", "media ponderada",
                     "la suma de valores por sus pesos, sobre la suma de pesos: cada dato influye "
                     "proporcionalmente a su peso — el promedio 'justo' cuando las observaciones difieren en importancia."),
            Ecuacion("w_i = w \\;\\forall i \\Rightarrow \\bar x_w = \\bar x", "contiene a la media simple",
                     "con pesos iguales la ponderada se reduce a la media simple: la media de e17 es el caso "
                     "particular de pesos uniformes — una fórmula, no dos."),
            Ecuacion("\\min x_i \\le \\bar x_w \\le \\max x_i", "combinación convexa",
                     "por ser un promedio, siempre cae dentro del rango de los datos, sin importar los pesos: "
                     "ponderar redistribuye influencia, no crea valores nuevos."),
        ],
        intuicion=("La media ponderada es la media 'con sentido de proporción': "
                   "reconoce que no todos los datos representan lo mismo. La imagen "
                   "es la del balancín de e17, pero ahora los pesos que cuelgan de "
                   "cada punto son distintos —un dato con peso 5 tira cinco veces "
                   "más fuerte que uno con peso 1—, y el punto de equilibrio se "
                   "corre hacia donde están los pesos grandes. Por eso tu promedio "
                   "sube más si sacas buena nota en el curso de muchos créditos que "
                   "en el de pocos, y por eso el rendimiento de tu cartera lo "
                   "domina el activo donde pusiste más plata. La lección de fondo, "
                   "que reaparecerá en toda la estadística, es que 'promediar' "
                   "esconde una decisión: la de cómo pesar. La media simple parece "
                   "neutral, pero solo es un caso particular —el de decidir que todo "
                   "pesa igual—, que a menudo NO es lo correcto. Elegir los pesos "
                   "con honestidad (por créditos, por monto, por población) es lo "
                   "que separa un índice informativo de uno tramposo: un IPC bien "
                   "ponderado describe el costo de vida real; uno con pesos "
                   "manipulados puede esconder la inflación."),
        equilibrio=("La media ponderada es una combinación convexa de los datos: "
                    "única, y siempre en [mín, máx]. Se reduce a la media simple con "
                    "pesos iguales, y se desplaza monótonamente hacia los datos de "
                    "mayor peso. No hay 'equilibrio' que resolver: es un promedio "
                    "con influencia redistribuida."),
        limitaciones=[
            "Depende críticamente de los pesos: pesos mal elegidos o manipulados hacen que el promedio diga cualquier cosa — la transparencia sobre la ponderación es esencial.",
            "Como la media simple, NO es robusta: un dato extremo con peso grande la arrastra (hereda la fragilidad de e17; la mediana ponderada sería la versión robusta).",
            "Exige datos cuantitativos y pesos con sentido: no aplica a categorías, y pesos negativos romperían la interpretación de promedio.",
        ],
        evolucion=("Generaliza la media simple (e17) reconociendo que las "
                   "observaciones pueden pesar distinto; la media simple es su caso "
                   "de pesos iguales. Es la base de los índices (IPC, e83 macro), la "
                   "esperanza matemática (E[X]=Σ p(x)·x es una media ponderada por "
                   "probabilidades, e43), y la regresión ponderada (e145, "
                   "heterocedasticidad). Junto con las medias geométrica (e21) y "
                   "armónica (e22) completa la familia de promedios."),
    ),
    escenarios=[
        Escenario("pesos_iguales", "pesos iguales: es la media simple",
                  {"w3": 1.0},
                  "con w₃=1 (todos los pesos iguales) la media ponderada coincide "
                  "con la simple (6.67): la media de e17 es el caso particular de "
                  "ponderar por igual — no son fórmulas distintas.",
                  cadena=["poner todos los pesos iguales (w₃=1)", "cada dato influye 1/n",
                          "media ponderada = media simple = 6.67", "la simple es un caso de la ponderada"]),
        Escenario("mucho_peso_alto", "mucho peso al valor alto (w₃=10)",
                  {"w3": 10.0},
                  "al darle peso 10 al valor 10, la media ponderada se acerca a 10 "
                  "(≈8.7): el dato de mayor peso domina el promedio, como el activo "
                  "donde invertiste más domina el rendimiento de la cartera.",
                  cadena=["subir el peso del valor 10 (w₃=10)", "ese dato tira diez veces más fuerte",
                          "la media se desplaza hacia el 10 (≈8.7)", "pero sin pasarse de 10 (combinación convexa)"]),
    ],
    verificaciones=[
        Verificacion("con pesos iguales se reduce a la media simple", _v_reduce_a_simple),
        Verificacion("siempre cae entre el mínimo y el máximo", _v_entre_min_y_max),
        Verificacion("más peso a un valor la desplaza hacia él", _v_monotona),
        Verificacion("fórmula Σwᵢxᵢ/Σwᵢ", _v_formula),
    ],
    notas="Media ponderada = Σwᵢxᵢ/Σwᵢ: cada dato influye según su peso (créditos, monto, participación). Contiene a la media simple (pesos iguales) y siempre cae en [mín,máx]. La elección de pesos es una decisión sustantiva, no estadística.",
)
