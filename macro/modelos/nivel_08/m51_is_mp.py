"""simuladores/macro/modelos/nivel_08/m51_is_mp.py — el modelo IS-MP: keynesianismo sin curva LM (nivel 8).

La actualización operativa del m10: el banco central ya no fija M (la LM
murió con la demanda de dinero inestable, m34/m37) — fija la TASA con una
regla (m38-m39). El aparato queda:
  IS:  Y = k·(A0 − b·r),  k = 1/(1−c1)
  MP:  r = r̄ + φ_π·π      (la regla de política, dado π)
La M desaparece del modelo: es un residuo que el corredor (m39) acomoda.

Procedencia: Romer (2000, "Keynesian Macroeconomics without the LM Curve",
mención) — conocimiento general; calibración didáctica.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _k(p):
    return 1 / (1 - p["c1"])


def _r_mp(p, pi=None):
    pi = p["pi"] if pi is None else pi
    return p["rbar"] + p["phi_pi"] * pi


def _y_eq(p):
    return _k(p) * (p["A0"] - p["b"] * _r_mp(p))


def _curvas(p):
    Y = np.linspace(300, 900, 200)
    r_is = (p["A0"] - Y / _k(p)) / p["b"]
    r_mp = np.full_like(Y, _r_mp(p))
    return {"lineas": {"IS: $Y = k\\,(A_0 - b\\,r)$": (Y, r_is, config.AZUL2),
                       "MP: $r = \\bar{r} + \\phi_\\pi\\,\\pi$ (regla)": (Y, r_mp, config.ROJO)},
            "equilibrio": (_y_eq(p), _r_mp(p)),
            "anotacion": (f"con $\\pi = {p['pi']:.1f}\\%$ la regla fija $r = {_r_mp(p):.2f}\\%$\n"
                          f"$Y = {_y_eq(p):,.1f}$\n"
                          "la M no aparece: la acomoda el corredor (m39)")}


def _resultados(p):
    return {"tasa fijada por la regla r": _r_mp(p),
            "producto Y": _y_eq(p),
            "multiplicador dY/dA0 (con π dado)": _k(p),
            "dY/dπ (la política endógena)": -_k(p) * p["b"] * p["phi_pi"],
            "pendiente de la MP en (Y,r)": 0.0}


def _ecuaciones_calibradas(p):
    return [f"$r = {p['rbar']:.1f} + {p['phi_pi']:.2f} \\times {p['pi']:.1f} = {_r_mp(p):.2f}$",
            f"$Y = {_k(p):.2f}\\,({p['A0']:.0f} - {p['b']:.0f} \\times {_r_mp(p):.2f}) = {_y_eq(p):,.1f}$"]


_P0 = {"A0": 300.0, "c1": 0.6, "b": 20.0, "rbar": 2.0, "phi_pi": 0.5, "pi": 2.0}


def _v_equilibrio():
    Y = _y_eq(_P0)
    res = Y - _k(_P0) * (_P0["A0"] - _P0["b"] * _r_mp(_P0))
    return abs(res) < 1e-12, f"el equilibrio satisface la IS con la r de la regla (Y={Y:,.1f})"


def _v_multiplicador_pleno():
    d = (_y_eq(dict(_P0, A0=_P0["A0"] + 1)) - _y_eq(_P0))
    return abs(d - _k(_P0)) < 1e-12, \
        (f"con π DADO, dY/dA0 = k = {_k(_P0):.2f}: la MP horizontal no frena el impulso — "
         "el freno llegará cuando π responda (m56)")


def _v_politica_endogena():
    d = _y_eq(dict(_P0, pi=3.0)) - _y_eq(_P0)
    teo = -_k(_P0) * _P0["b"] * _P0["phi_pi"]
    return abs(d - teo) < 1e-9, \
        (f"+1pp de inflación mueve Y en {teo:,.1f} vía la regla: el enfriamiento ya no es "
         "una decisión — es un REFLEJO institucional")


def _v_sin_dinero():
    claves = set(_P0)
    return "M" not in claves and "MP" not in claves, \
        "no hay M entre los parámetros: la cantidad de dinero salió del modelo (la acomoda m39)"


MODELO = Modelo(
    id="m51", nivel=8,
    nombre="Modelo IS-MP",
    xlabel="Producto ($Y$)", ylabel="Tasa de interés ($r$)",
    parametros=[
        Parametro("pi", _P0["pi"], -1, 8, 0.5, "Inflación observada π (%)", grupo="situación",
                  definicion="lo que activa la regla"),
        Parametro("A0", _P0["A0"], 150, 450, 10, "Gasto autónomo A0", grupo="demanda"),
        Parametro("rbar", _P0["rbar"], 0, 5, 0.25, "Tasa base de la regla r̄", grupo="regla"),
        Parametro("phi_pi", _P0["phi_pi"], 0.0, 1.5, 0.05, "Respuesta a inflación φ_π", grupo="regla"),
        Parametro("c1", _P0["c1"], 0.3, 0.85, 0.05, "Propensión a consumir c1", grupo="estructura"),
        Parametro("b", _P0["b"], 8, 35, 1, "Sensibilidad de la demanda a r (b)", grupo="estructura"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si los bancos centrales fijan la tasa y no la cantidad de dinero, ¿cómo debe verse el 'IS-LM' del siglo XXI?",
        variables=[("Y", "producto — endógeno"),
                   ("r", "la tasa — la FIJA la regla, no el mercado de dinero"),
                   ("π", "inflación — exógena aquí; endógena en m56"),
                   ("M", "…no está: es el residuo que acomoda el corredor (m39)")],
        derivacion=["IS: \\;Y = k\\,(A_0 - b\\,r), \\quad k = \\frac{1}{1-c_1}",
                    "MP: \\;r = \\bar{r} + \\phi_\\pi\\,\\pi \\;\\;(la\\;regla\\;de\\;m38)",
                    "\\Rightarrow\\; Y = k\\,(A_0 - b\\,\\bar{r} - b\\,\\phi_\\pi\\,\\pi)"],
        contexto=("Durante décadas se enseñó un modelo (IS-LM, con M exógena) que "
                  "describía un banco central que ya no existía. Romer (2000) "
                  "propuso la corrección mínima: reemplazar la LM por una curva de "
                  "POLÍTICA MONETARIA — la regla de tasas que los bancos centrales "
                  "realmente siguen (m38) e implementan (m39). El resultado es más "
                  "simple Y más realista: la M desaparece del pizarrón, como "
                  "desapareció de los directorios."),
        autores=("Romer (2000, mención); la práctica que lo motivó: los bancos "
                 "centrales de metas (m40) operando con tasas desde los 90."),
        supuestos=[
            "π es DADA en este aparato estático: la MP es horizontal a la r que la regla dicta para esa inflación (la dinámica π↔Y es m56).",
            "El corredor (m39) implementa cualquier r que la regla pida: M es perfectamente endógena.",
            "Demanda lineal en r (la IS del nivel 2, sin sector externo).",
        ],
        ecuaciones=[
            Ecuacion("r = \\bar{r} + \\phi_\\pi\\,\\pi", "la curva MP",
                     "no es un mercado: es una FUNCIÓN DE REACCIÓN hecha curva — horizontal en "
                     "(Y, r) porque, dado π, el banco central sirve esa tasa a cualquier Y."),
            Ecuacion("Y = k\\,(A_0 - b\\,\\bar{r} - b\\,\\phi_\\pi\\,\\pi)", "la demanda con política endógena",
                     "la inflación entra a la demanda POR la regla: más π ⇒ más r ⇒ menos Y — "
                     "esta pendiente negativa en (π, Y) es la AD moderna (m52)."),
        ],
        intuicion=("El cambio es de sujeto: en m10 la tasa 'resultaba' del mercado "
                   "de dinero; aquí la tasa 'se decide' y el dinero resulta. Con π "
                   "dada, la MP horizontal deja al multiplicador trabajar completo "
                   "(¡sin expulsión!) — el freno moderno no es la escasez de M sino "
                   "la RESPUESTA del banco central cuando la inflación despierta. "
                   "Por eso este modelo pide a gritos su dinámica: m52 y m56."),
        equilibrio=("Intersección IS-MP única (verificada exacta); la estática "
                    "comparativa respecto de π es la política endógena en acción "
                    "(dY/dπ = −k·b·φπ, verificada)."),
        limitaciones=[
            "π exógena es media verdad: el producto retroalimenta a la inflación (Phillips) — sin eso no hay ancla (m52/m56 lo cierran).",
            "Sin ZLB: la regla puede pedir r<0 y aquí se concede (m12 diría que no).",
            "Economía cerrada: la MP de una economía abierta pelea con la UIP (m48-m49).",
        ],
        evolucion=("Es el primer tercio del modelo moderno: m52 le añade la oferta "
                   "(AD-AS dinámico), m54-m55 microfundan sus dos curvas con "
                   "expectativas racionales, y m56 arma el sistema completo de 3 "
                   "ecuaciones — el lenguaje de los bancos centrales de hoy."),
    ),
    escenarios=[
        Escenario("brote_inflacionario", "π sube de 2% a 6% y la regla responde",
                  {"pi": 6.0},
                  "la MP salta a r=5% y Y cae de 600 a 500: nadie 'decidió' enfriar — "
                  "la regla lo hizo sola. La estabilización como reflejo.",
                  cadena=["↑π", "la regla dicta ↑r (m38)", "la MP horizontal sube",
                          "↓I por la IS", "↓Y: enfriamiento automático"]),
        Escenario("estimulo_fiscal", "A0 sube de 300 a 340 con π quieta",
                  {"A0": 340.0},
                  "Y sube 100 (multiplicador pleno k=2.5): sin LM no hay expulsión "
                  "por dinero — hasta que la inflación despierte y la regla cobre (m56).",
                  cadena=["↑A0", "la MP no se mueve (π dada)", "sin freno de r",
                          "ΔY = k·ΔA0 pleno", "la factura llega cuando π responda (m56)"]),
        Escenario("recorte_de_tasa", "el banco central baja r̄ de 2% a 1%",
                  {"rbar": 1.0},
                  "la MP baja en paralelo y Y sube 50: la política monetaria moderna "
                  "en su gesto más simple — mover la base de la regla.",
                  cadena=["decisión: ↓r̄", "toda la MP baja", "crédito más barato a cada Y",
                          "↑I", "↑Y = k·b·Δr̄"]),
    ],
    verificaciones=[
        Verificacion("equilibrio IS-MP exacto", _v_equilibrio),
        Verificacion("con π dada, multiplicador pleno (sin LM no hay expulsión)", _v_multiplicador_pleno),
        Verificacion("política endógena: dY/dπ = −k·b·φπ exacto", _v_politica_endogena),
        Verificacion("la M no existe en el modelo (residuo de m39)", _v_sin_dinero),
    ],
    notas="El IS-LM del siglo XXI: la tasa se decide, el dinero resulta. π espera su turno en m56.",
)
