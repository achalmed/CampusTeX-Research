# m21_oferta_corto_plazo.py — oferta agregada de corto plazo (SRAS) — nivel 4.
#
#   P = Pe + λ·(Y − Y*)
# La posición de la curva la fija Pe (el precio esperado al negociar contratos);
# su pendiente λ, el grado de rigidez nominal. dPe desplaza la SRAS: ese
# desplazamiento ES el mecanismo del ajuste al largo plazo (m25).
#
# Procedencia: forma reducida estándar de manuales; microfundamentos citados
# como mención (contratos: Fischer/Taylor; percepciones erróneas: Friedman;
# información imperfecta: Lucas — hay material de Lucas en la biblioteca, no
# verificado). Calibración: decisión de diseño didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _p(Y, pe, p):
    return pe + p["lam"] * (Y - p["Ystar"])


def _curvas(p):
    Y = np.linspace(500, 900, 200)
    lras_p = np.linspace(_p(500, p["Pe"], p), _p(900, p["Pe"] + p["dPe"], p), 2)
    return {"lineas": {"SRAS: $P = P^e + \\lambda(Y-Y^*)$": (Y, _p(Y, p["Pe"], p), config.VERDE),
                       "SRAS con $P^e$ mayor ($dP^e$)": (Y, _p(Y, p["Pe"] + p["dPe"], p), config.ROJO),
                       "LRAS ($Y=Y^*$, referencia)": (np.full(2, p["Ystar"]), lras_p, config.GRIS)},
            "puntos": [(p["Ystar"], p["Pe"], f"$(Y^*,\\,P^e)$")],
            "anotacion": (f"pendiente $\\lambda = {p['lam']:.3f}$\n"
                          f"$P(Y^*) = P^e = {p['Pe']:.2f}$\n"
                          f"$dP^e = {p['dPe']:+.2f}$ desplaza la curva verticalmente")}


def _resultados(p):
    return {"P en Y* (= Pe)": _p(p["Ystar"], p["Pe"], p),
            "P con brecha +50": _p(p["Ystar"] + 50, p["Pe"], p),
            "P con brecha −50": _p(p["Ystar"] - 50, p["Pe"], p),
            "pendiente λ": p["lam"],
            "desplazamiento vertical por dPe": p["dPe"]}


_P0 = {"Pe": 2.0, "dPe": 0.3, "lam": 0.004, "Ystar": 700.0}


def _v_ancla():
    return abs(_p(_P0["Ystar"], _P0["Pe"], _P0) - _P0["Pe"]) < 1e-12, \
        "en Y=Y* el precio efectivo iguala al esperado: sin sorpresas, sin brecha"


def _v_desplazamiento():
    d = _p(650.0, _P0["Pe"] + _P0["dPe"], _P0) - _p(650.0, _P0["Pe"], _P0)
    return abs(d - _P0["dPe"]) < 1e-12, f"dPe={_P0['dPe']} sube la curva exactamente eso, a cualquier Y"


def _v_pendiente():
    pend = (_p(800.0, _P0["Pe"], _P0) - _p(600.0, _P0["Pe"], _P0)) / 200.0
    return abs(pend - _P0["lam"]) < 1e-12, f"pendiente = λ = {pend:.4f}"


MODELO = Modelo(
    id="m21", nivel=4,
    nombre="Oferta agregada de corto plazo (SRAS)",
    xlabel="Producto ($Y$)", ylabel="Nivel de precios ($P$)",
    parametros=[
        Parametro("dPe", _P0["dPe"], -0.6, 0.8, 0.05, "Cambio del precio esperado dPe"),
        Parametro("lam", _P0["lam"], 0.001, 0.02, 0.001, "Rigidez/pendiente λ"),
        Parametro("Pe", _P0["Pe"], 1.0, 3.5, 0.1, "Precio esperado Pe"),
        Parametro("Ystar", _P0["Ystar"], 550, 850, 10, "Producto potencial Y*"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ficha=Ficha(
        pregunta="¿Por qué producir más exige precios más altos solo en el corto plazo?",
        contexto=("¿Por qué producir MÁS exige precios más altos solo en el corto "
                  "plazo? Porque hay compromisos nominales tomados con expectativas: "
                  "salarios pactados esperando Pe, precios de catálogo, contratos. "
                  "Cuando la demanda sorprende, las empresas ajustan cantidades y algo "
                  "de precios — hasta que los contratos se renegocian. Tres familias de "
                  "microfundamento compiten por explicar λ: salarios rígidos "
                  "(contratos), percepciones erróneas de los trabajadores (Friedman) e "
                  "información imperfecta de las empresas (las 'islas' de Lucas)."),
        autores=("Forma reducida de manual; microfundamentos: Friedman (1968), Lucas "
                 "(información imperfecta, 1972 — mención; hay material en la "
                 "biblioteca), contratos escalonados de Fischer (1977) y Taylor (1980) "
                 "(menciones). Es la hermana del lado de precios de la Phillips (m13)."),
        supuestos=[
            "Pe está DADO dentro del período: los contratos ya se firmaron (la revisión de Pe entre períodos es m25).",
            "λ constante: el grado de rigidez no depende del tamaño ni del signo del shock (dudoso con inflación alta).",
            "Y* exógeno aquí (lo produce m22).",
        ],
        ecuaciones=[
            Ecuacion("P = P^e + \\lambda\\,(Y - Y^*)", "SRAS",
                     "en Y* no hay sorpresas (P=Pe); producir sobre el potencial exige exprimir "
                     "recursos y pagar más — λ traduce la brecha en presión de precios."),
            Ecuacion("\\lambda \\to 0: \\text{keynesiano} \\;;\\; \\lambda \\to \\infty: \\text{clásico}",
                     "los dos extremos",
                     "λ=0 es el mundo de precios fijos de los niveles 1-2; λ→∞ es la LRAS vertical "
                     "(m22): la SRAS interpola entre las dos escuelas."),
        ],
        intuicion=("La SRAS es una curva de SORPRESAS: solo se está fuera de (Y*, Pe) "
                   "si el precio efectivo difiere del esperado. Por eso su posición se "
                   "mueve con las expectativas: cada vez que Pe se revisa al alza, "
                   "producir cualquier Y cuesta más — la curva sube. Ese "
                   "desplazamiento, repetido, es el ajuste hacia el largo plazo."),
        equilibrio=("Como IS o LM, la SRAS sola no determina nada: aporta la relación "
                    "de oferta que la AD (m20) necesita para fijar (Y, P) en m23."),
        limitaciones=[
            "λ y Pe son formas reducidas: los microfundamentos rivales (contratos, percepciones, información) implican dinámicas distintas de ajuste que aquí se resumen en un número.",
            "Rigidez simétrica: la evidencia sugiere más rigidez a la baja (recortar salarios nominales es raro).",
            "Con inflación alta y crónica la rigidez desaparece (indexación): λ efectivo crece — la SRAS es una curva de inflación BAJA.",
        ],
        evolucion=("m22 aporta la LRAS (el ancla de largo plazo), m23 junta AD+SRAS+"
                   "LRAS, y m25 pone a Pe en movimiento (Pe_{t+1}=P_t) para mostrar la "
                   "autocorrección. La versión con inflación (no niveles) y "
                   "expectativas racionales es la Phillips nuevo keynesiana (m55)."),
    ),
    escenarios=[
        Escenario("expectativas_al_alza", "los contratos se firman esperando más inflación (dPe=+0.3)",
                  {"dPe": 0.3},
                  "la SRAS entera sube 0.3: mismas cantidades, todo más caro — así se "
                  "propaga una inflación esperada aunque la demanda no cambie.",
                  cadena=["↑Pe (contratos esperan más inflación)", "producir cualquier Y cuesta más",
                          "SRAS → arriba en dPe", "inflación esperada = inflación efectiva"]),
        Escenario("desinflacion_creible", "expectativas a la baja (dPe=−0.3)",
                  {"dPe": -0.3},
                  "una promesa creíble de menos inflación BAJA la SRAS: la credibilidad "
                  "(m41) ahorra recesión — el argumento central de las metas de inflación.",
                  cadena=["↓Pe creíble", "los contratos se firman más baratos",
                          "SRAS → abajo", "desinflar sin recesión (m40-m41)"]),
        Escenario("oferta_flexible", "λ pequeño (0.002): precios lentos, cantidades rápidas",
                  {"lam": 0.002},
                  "mundo más keynesiano: la misma brecha presiona menos los precios.",
                  cadena=["↓λ", "los precios responden poco a la brecha",
                          "SRAS más plana", "el corto plazo keynesiano se alarga"]),
    ],
    verificaciones=[
        Verificacion("ancla: P(Y*) = Pe", _v_ancla),
        Verificacion("dPe desplaza la curva exactamente dPe", _v_desplazamiento),
        Verificacion("pendiente = λ", _v_pendiente),
    ],
    notas="La posición de la SRAS son las expectativas: moverlas es el mecanismo del largo plazo (m25).",
)
