# m31_trampa_pobreza.py — trampa de pobreza: equilibrios múltiples (nivel 5).
#
# Solow con una NO-convexidad: la productividad depende del nivel de capital
# (umbral de infraestructura/escala/instituciones):
#   A(k) = A_baja si k < k_umbral ;  A_alta si k ≥ k_umbral
# Resultado: DOS estados estacionarios estables (trampa y prosperidad)
# separados por el umbral. La historia (k0) decide el destino — histéresis —
# y la ayuda solo sirve si cruza el umbral ("big push").
#
# Procedencia: familia de modelos de trampas con no-convexidades (Rosenstein-
# Rodan "big push" 1943; Murphy-Shleifer-Vishny 1989; Azariadis-Drazen 1990 —
# menciones). Formulación con A(k) escalonada: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_05 import _solow
import config


def _A(k, p):
    return p["A_alta"] if k >= p["umbral"] else p["A_baja"]


def _ngd(p):
    return p["n"] + p["delta"]


def _tray(k0, p, T):
    k = np.empty(int(T) + 1)
    k[0] = k0
    for t in range(int(T)):
        k[t + 1] = k[t] + p["s"] * _A(k[t], p) * k[t] ** p["alpha"] - _ngd(p) * k[t]
    return k


def _equilibrios(p):
    ngd = _ngd(p)
    k_bajo = _solow.k_estrella(p["s"], p["A_baja"], p["alpha"], ngd)
    k_alto = _solow.k_estrella(p["s"], p["A_alta"], p["alpha"], ngd)
    hay_trampa = k_bajo < p["umbral"] <= k_alto
    return k_bajo, k_alto, hay_trampa


def _curvas(p):
    ngd = _ngd(p)
    k_bajo, k_alto, hay_trampa = _equilibrios(p)
    k1 = np.linspace(0.05, p["umbral"], 150)
    k2 = np.linspace(p["umbral"], max(12.0, 1.4 * k_alto), 150)
    k_all = np.linspace(0.05, max(12.0, 1.4 * k_alto), 2)
    destino = _tray(p["k0"] + p["ayuda"], p, 800)[-1]
    return {"lineas": {"inversión con $A_{baja}$ ($k<$ umbral)": (k1, p["s"] * p["A_baja"] * k1 ** p["alpha"], config.ROJO),
                       "inversión con $A_{alta}$ ($k\\geq$ umbral)": (k2, p["s"] * p["A_alta"] * k2 ** p["alpha"], config.VERDE),
                       "reposición $(n+\\delta)k$": (k_all, ngd * k_all, config.GRIS)},
            "puntos": [(k_bajo, ngd * k_bajo, f"trampa $k^*_b={k_bajo:.1f}$"),
                       (k_alto, ngd * k_alto, f"prosperidad $k^*_a={k_alto:.1f}$"),
                       (p["umbral"], ngd * p["umbral"], "umbral")],
            "anotacion": (f"{'DOS equilibrios estables' if hay_trampa else 'la trampa NO existe con estos parámetros'}\n"
                          f"partida $k_0{{+}}ayuda = {p['k0'] + p['ayuda']:.1f}$ → destino $k = {destino:.1f}$")}


def _resultados(p):
    k_bajo, k_alto, hay_trampa = _equilibrios(p)
    destino = float(_tray(p["k0"] + p["ayuda"], p, 800)[-1])
    return {"k* de la trampa": k_bajo,
            "k* de la prosperidad": k_alto,
            "¿hay trampa? (1=sí)": 1.0 if hay_trampa else 0.0,
            "partida efectiva k0+ayuda": p["k0"] + p["ayuda"],
            "destino de largo plazo": destino,
            "y en el destino": float(_A(destino, p) * destino ** p["alpha"]),
            "razón de ingresos alto/bajo": (_A(k_alto, p) * k_alto ** p["alpha"])
                                           / (_A(k_bajo, p) * k_bajo ** p["alpha"])}


_P0 = {"s": 0.20, "A_baja": 0.6, "A_alta": 1.2, "umbral": 3.0,
       "alpha": 0.33, "n": 0.01, "delta": 0.05, "k0": 1.5, "ayuda": 0.0}


def _v_dos_equilibrios():
    k_bajo, k_alto, hay = _equilibrios(_P0)
    ngd = _ngd(_P0)
    r_b = _P0["s"] * _P0["A_baja"] * k_bajo ** _P0["alpha"] - ngd * k_bajo
    r_a = _P0["s"] * _P0["A_alta"] * k_alto ** _P0["alpha"] - ngd * k_alto
    ok = hay and abs(r_b) < 1e-12 and abs(r_a) < 1e-12
    return ok, (f"coexisten dos EE estables: trampa k*={k_bajo:.2f} (<umbral) y "
                f"prosperidad k*={k_alto:.2f} (≥umbral), ambos puntos fijos exactos")


def _v_ayuda_timida():
    k_bajo, _, _ = _equilibrios(_P0)
    final = _tray(_P0["k0"] + 1.0, _P0, 2000)[-1]
    return abs(final - k_bajo) < 1e-6, ("ayuda de 1.0 (no cruza el umbral): la economía VUELVE a la "
                                        f"trampa (k={final:.2f}) — la ayuda se diluyó")


def _v_gran_empuje():
    _, k_alto, _ = _equilibrios(_P0)
    final = _tray(_P0["k0"] + 2.0, _P0, 2000)[-1]
    return abs(final - k_alto) < 1e-6, ("ayuda de 2.0 (cruza el umbral): despegue permanente hasta "
                                        f"k={final:.2f} — el big push funciona SOLO si es suficiente")


def _v_histeresis():
    k_bajo, k_alto, _ = _equilibrios(_P0)
    f1 = _tray(2.0, _P0, 2000)[-1]
    f2 = _tray(4.0, _P0, 2000)[-1]
    ok = abs(f1 - k_bajo) < 1e-6 and abs(f2 - k_alto) < 1e-6
    return ok, ("mismos parámetros, destinos opuestos según k0 (2.0→trampa, 4.0→prosperidad): "
                "la HISTORIA importa — histéresis, lo que m30 descartaba")


MODELO = Modelo(
    id="m31", nivel=5,
    nombre="Trampa de pobreza",
    xlabel="Capital por trabajador ($k$)", ylabel="Flujos por trabajador",
    parametros=[
        Parametro("ayuda", _P0["ayuda"], 0.0, 4.0, 0.25, "Ayuda/inversión externa (Δk0)", grupo="política",
                  definicion="capital inyectado de una vez: ¿cruza el umbral?"),
        Parametro("k0", _P0["k0"], 0.3, 10.0, 0.25, "Capital inicial k0", grupo="historia"),
        Parametro("umbral", _P0["umbral"], 1.5, 6.0, 0.25, "Umbral de despegue", grupo="tecnología",
                  definicion="escala mínima (infraestructura, instituciones) para A alta"),
        Parametro("A_baja", _P0["A_baja"], 0.3, 1.0, 0.05, "Productividad bajo el umbral", grupo="tecnología"),
        Parametro("A_alta", _P0["A_alta"], 0.8, 2.0, 0.05, "Productividad sobre el umbral", grupo="tecnología"),
        Parametro("s", _P0["s"], 0.05, 0.5, 0.01, "Tasa de ahorro s", grupo="estructura"),
        Parametro("alpha", _P0["alpha"], 0.2, 0.5, 0.01, "Participación del capital α", grupo="estructura"),
        Parametro("n", _P0["n"], 0.0, 0.04, 0.005, "Crecimiento poblacional n", grupo="estructura"),
        Parametro("delta", _P0["delta"], 0.02, 0.10, 0.005, "Depreciación δ", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Por qué algunos países no despegan nunca — y cuándo la ayuda sirve y cuándo se diluye?",
        variables=[("k", "capital por trabajador — endógena, con DOS destinos posibles"),
                   ("A(k)", "productividad dependiente de la escala — la no-convexidad"),
                   ("k0, ayuda", "historia y política — deciden el lado del umbral")],
        derivacion=["\\Delta k = s\\,A(k)\\,k^{\\alpha} - (n+\\delta)\\,k",
                    "A(k) = A_b \\;(k<\\bar{k}), \\;\\; A_a \\;(k\\geq\\bar{k})",
                    "k^*_b = \\Big(\\tfrac{sA_b}{n+\\delta}\\Big)^{\\frac{1}{1-\\alpha}} < \\bar{k} \\leq k^*_a"],
        contexto=("m30 dijo que la estructura decide el destino; este modelo pregunta "
                  "¿y si la estructura DEPENDE del nivel? Con productividad que exige "
                  "escala mínima — infraestructura, mercados densos, instituciones — "
                  "la curva de inversión se quiebra y aparecen dos mundos "
                  "autosostenidos: pobreza que se perpetúa y prosperidad que se "
                  "financia sola. Es la formalización del 'big push' de "
                  "Rosenstein-Rodan (1943): industrializar requiere empujar TODO a la "
                  "vez por encima del umbral, o el esfuerzo se escurre de vuelta."),
        autores=("Rosenstein-Rodan (1943, big push); formalizaciones: Murphy, "
                 "Shleifer y Vishny (1989), Azariadis y Drazen (1990) — menciones. "
                 "La versión con A(k) escalonada es una simplificación didáctica."),
        supuestos=["No-convexidad: A salta en un umbral de k (escala mínima) — TODO el resultado descansa aquí.",
                   "El umbral es de capital físico por simplicidad (podría ser humano, institucional, de demanda).",
                   "Los demás de Solow (s exógena, economía cerrada: la ayuda externa entra solo como Δk0)."],
        ecuaciones=[
            Ecuacion("A(k) = \\begin{cases} A_b & k < \\bar{k} \\\\ A_a & k \\geq \\bar{k}\\end{cases}",
                     "productividad con umbral",
                     "por debajo del umbral la economía es estructuralmente menos productiva: "
                     "poca infraestructura, mercados ralos, informalidad."),
            Ecuacion("k^*_b < \\bar{k} \\leq k^*_a", "condición de existencia de la trampa",
                     "cada régimen debe ser consistente con su lado del umbral: si A_b mejora lo "
                     "suficiente, k*_b cruza el umbral y la trampa DESAPARECE — la reforma "
                     "estructural como alternativa al big push."),
        ],
        intuicion=("En Solow clásico toda ayuda acerca al único k*; aquí hay un punto "
                   "de quiebre: por debajo, la gravedad tira hacia la trampa y la "
                   "ayuda insuficiente SE DILUYE (verificado: +1.0 de capital vuelve "
                   "exactamente a la trampa); por encima, el sistema se financia solo. "
                   "De ahí las dos escuelas de política: el gran empuje (cruzar el "
                   "umbral de una vez) y la reforma estructural (subir A_baja hasta "
                   "que el umbral deje de existir)."),
        equilibrio=("Dos EE estables separados por el umbral (inestable): histéresis "
                    "verificada — mismos parámetros, destino según la historia. La "
                    "convergencia condicional de m30 se rompe: aquí ni la estructura "
                    "basta, importa el punto de partida."),
        limitaciones=[
            "El salto discreto de A es una caricatura: los modelos serios derivan la no-convexidad de complementariedades (MSV 1989) o umbrales de capital humano (Azariadis-Drazen).",
            "Evidencia empírica disputada: distinguir 'trampa' de 'fundamentales malos persistentes' es difícil.",
            "La ayuda como Δk0 de una vez ignora incentivos, absorción y gobernanza — el debate Sachs-Easterly (mención) es exactamente sobre esto.",
        ],
        evolucion=("Última pieza del aparato de convergencia: m30 (estructura) + m31 "
                   "(historia y umbrales). Lo que sigue ataca el otro flanco de Solow: "
                   "¿y si el crecimiento no se apaga? m32 (AK) elimina los "
                   "rendimientos decrecientes; m33 (capital humano) los suaviza — dos "
                   "caminos para endogeneizar el motor."),
    ),
    escenarios=[
        Escenario("sin_ayuda", "la economía parte en k0 = 1.5, dentro de la cuenca de la trampa",
                  {"ayuda": 0.0},
                  "converge a k*=2.8 y se queda: pobreza DE EQUILIBRIO — estable, "
                  "autosostenida, sin fuerza interna que la rompa.",
                  cadena=["k0 < umbral", "régimen A_baja", "gravita a k*_bajo",
                          "ingresos bajos → ahorro bajo en niveles", "pobreza autosostenida"]),
        Escenario("ayuda_timida", "inyección de capital de 1.0 (no cruza el umbral)",
                  {"ayuda": 1.0},
                  "k salta a 2.5, sigue bajo el umbral… y la gravedad de la trampa lo "
                  "devuelve a 2.8: millones diluidos sin cambiar el destino.",
                  cadena=["k0+ayuda = 2.5 < umbral", "sigue en régimen A_baja",
                          "la reposición supera a la inversión extra", "regreso a k*_bajo",
                          "ayuda diluida (Easterly, mención)"]),
        Escenario("gran_empuje", "big push de 2.0 (cruza el umbral)",
                  {"ayuda": 2.0},
                  "k0+ayuda = 3.5 ≥ umbral: cambia el régimen, la inversión supera a "
                  "la reposición y la economía despega SOLA hasta k*=7.9.",
                  cadena=["k0+ayuda ≥ umbral", "régimen A_alta", "inversión > reposición",
                          "despegue autosostenido", "k*_alto: prosperidad permanente"]),
        Escenario("reforma_estructural", "subir A_baja a 0.9 elimina la trampa",
                  {"A_baja": 0.9},
                  "con A_baja=0.9, k*_bajo=5.2 > umbral: el equilibrio pobre deja de "
                  "existir y la economía despega SIN ayuda — la alternativa al big push.",
                  cadena=["↑A_baja (reforma)", "k*_bajo cruza el umbral", "la trampa deja de existir",
                          "un solo destino: prosperidad", "reforma > transferencia"]),
    ],
    verificaciones=[
        Verificacion("dos equilibrios estables coexisten (puntos fijos exactos)", _v_dos_equilibrios),
        Verificacion("la ayuda tímida se diluye (vuelve a la trampa)", _v_ayuda_timida),
        Verificacion("el gran empuje escapa (despegue permanente)", _v_gran_empuje),
        Verificacion("histéresis: la historia decide el destino", _v_histeresis),
    ],
    notas="La primera vez que la HISTORIA (k0) decide el destino: adiós a la convergencia garantizada.",
)
