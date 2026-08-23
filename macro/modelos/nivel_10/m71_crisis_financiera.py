# m71_crisis_financiera.py — crisis financiera: apalancamiento y desapalancamiento
# (nivel 10).
#
# El balance apalancado y su fragilidad. Un intermediario con activos A,
# deuda D y capital E = A − D opera con apalancamiento  λ = A/E.
# Una caída del valor de activos de fracción `shock` golpea TODO al capital
# (la deuda es fija):  E' = E − shock·A = A(1/λ − shock).
#   apalancamiento nuevo:  λ' = A' / E' = (1−shock)/(1/λ − shock)
#   pérdida de capital amplificada:  ΔE/E = −shock·λ   (¡×λ!)
# Para restaurar λ objetivo con capital caído hay que VENDER activos:
# ventas = A − λ_obj·E' — y si todos venden, el precio cae más (fire sale):
# el desapalancamiento es contractivo (adelanta m79).
#
# Procedencia: mecánica de balance apalancado estándar (Adrian-Shin sobre
# leverage procíclico; Minsky sobre fragilidad — menciones) — conocimiento
# general; calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _balance(p):
    A, E = p["A"], p["A"] / p["lam"]
    D = A - E
    perdida = p["shock"] / 100 * A
    E1 = E - perdida
    A1 = (1 - p["shock"] / 100) * A
    lam1 = A1 / E1 if E1 > 0 else float("inf")
    ventas = A1 - p["lam_obj"] * E1 if E1 > 0 else A1
    return dict(A=A, E=E, D=D, E1=E1, A1=A1, lam1=lam1,
                ventas=max(0.0, ventas), perdida=perdida)


def _curvas(p):
    b = _balance(p)
    cats = ["capital $E$\ninicial", "pérdida\n$shock{\\cdot}A$", "capital $E'$\ntras shock",
            "ventas para\ndesapalancar"]
    vals = [b["E"], -b["perdida"], b["E1"], b["ventas"]]
    cols = [config.AZUL2, config.ROJO, config.DORADO, config.VERDE]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$\\lambda = {p['lam']:.0f}$ → una caída de {p['shock']:.0f}% "
                          f"borra {p['shock'] / 100 * p['lam'] * 100:.0f}% del capital\n"
                          f"$\\lambda' = {b['lam1']:.1f}$ "
                          f"({'INSOLVENTE' if b['E1'] <= 0 else 'más frágil'})\n"
                          "el desapalancamiento vende — y el precio cae más (m79)")}


def _resultados(p):
    b = _balance(p)
    return {"capital inicial E": b["E"],
            "apalancamiento λ = A/E": p["lam"],
            "pérdida de capital (ΔE/E, %)": -p["shock"] * p["lam"],
            "capital tras shock E'": b["E1"],
            "apalancamiento nuevo λ'": b["lam1"],
            "activos a vender para desapalancar": b["ventas"]}


def _ecuaciones_calibradas(p):
    b = _balance(p)
    return [f"$E = A/\\lambda = {b['A']:.0f}/{p['lam']:.0f} = {b['E']:.1f}$",
            f"$\\Delta E/E = -shock\\cdot\\lambda = -{p['shock']:.0f}\\%\\times{p['lam']:.0f} "
            f"= {-p['shock'] * p['lam']:.0f}\\%$",
            f"$\\lambda' = {b['lam1']:.1f}$"]


_P0 = {"A": 1000.0, "lam": 20.0, "shock": 3.0, "lam_obj": 20.0}


def _v_amplificacion():
    b = _balance(_P0)
    dEE = (b["E1"] - b["E"]) / b["E"] * 100
    return abs(dEE - (-_P0["shock"] * _P0["lam"])) < 1e-9, \
        (f"una caída de activos de {_P0['shock']:.0f}% borra {-dEE:.0f}% del capital = shock×λ: "
         "el apalancamiento amplifica exactamente por su factor")


def _v_insolvencia():
    b = _balance(dict(_P0, shock=5.0))
    return b["E1"] <= 0, \
        (f"con λ=20, un shock de 5% (=1/λ) AGOTA el capital (E'={b['E1']:.0f}): "
         "la insolvencia llega cuando el shock alcanza 1/λ — el margen es delgadísimo")


def _v_desapalancar_vende():
    b0 = _balance(dict(_P0, shock=2.0))
    return b0["ventas"] > 0, \
        (f"tras el shock, restaurar λ objetivo exige VENDER {b0['ventas']:.0f} de activos: "
         "el ajuste de balance es contractivo — la semilla del fire sale (m79)")


def _v_solvente_sin_ventas():
    b = _balance(dict(_P0, shock=0.0, lam_obj=25.0))
    return abs(b["ventas"]) < 1e-9, \
        "sin shock y con λ objetivo mayor que el actual, no hay ventas forzadas: la calma antes"


MODELO = Modelo(
    id="m71", nivel=10,
    nombre="Crisis financiera (apalancamiento)",
    xlabel="", ylabel="Balance (u.m.)",
    parametros=[
        Parametro("lam", _P0["lam"], 2, 40, 1, "Apalancamiento λ = A/E", grupo="fragilidad",
                  definicion="activos por unidad de capital: >1/shock = insolvencia potencial"),
        Parametro("shock", _P0["shock"], 0, 8, 0.5, "Caída del valor de activos (%)", grupo="detonante"),
        Parametro("A", _P0["A"], 200, 2000, 100, "Activos totales A", grupo="balance"),
        Parametro("lam_obj", _P0["lam_obj"], 10, 30, 1, "Apalancamiento objetivo", grupo="ajuste",
                  definicion="al que el intermediario quiere volver vendiendo"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué una caída pequeña del valor de los activos puede borrar TODO el capital de un banco — y por qué el ajuste empeora la caída?",
        variables=[("λ = A/E", "apalancamiento — el amplificador de pérdidas"),
                   ("E = A − D", "capital — el delgado colchón que absorbe TODO el shock"),
                   ("ventas", "el desapalancamiento — contractivo por diseño (m79)")],
        derivacion=["E = A - D, \\quad \\lambda = A/E",
                    "\\Delta E = -shock\\cdot A \\;\\Rightarrow\\; \\frac{\\Delta E}{E} = -shock\\cdot\\lambda",
                    "insolvencia \\iff shock \\geq 1/\\lambda"],
        contexto=("Los intermediarios financieros son máquinas de apalancamiento: "
                  "un banco de inversión pre-2008 operaba con λ de 30 o más — 30 "
                  "dólares de activos por cada dólar de capital. La aritmética del "
                  "balance vuelve esa eficiencia en fragilidad: como la deuda es "
                  "fija, cualquier pérdida de valor golpea íntegra al capital, "
                  "amplificada por λ. Una caída de 3% en activos con λ=20 borra el "
                  "60% del capital; una de 5% lo agota. Y el remedio — vender para "
                  "reducir λ — deprime más los precios si todos lo hacen a la vez "
                  "(fire sale): la crisis financiera es el apalancamiento "
                  "funcionando en reversa."),
        autores=("Mecánica de balance apalancado (conocimiento general); leverage "
                 "procíclico: Adrian y Shin (mención); fragilidad endógena por "
                 "estabilidad: Minsky (mención); fire sales: Shleifer-Vishny "
                 "(mención)."),
        supuestos=[
            "Deuda de valor fijo (nominal): todo el riesgo lo absorbe el capital — el supuesto que crea la amplificación.",
            "Shock exógeno de una vez: la endogeneidad (fire sale que baja precios que fuerzan más ventas) es la ESPIRAL, aquí insinuada.",
            "Un intermediario aislado: el contagio y la red son m80.",
        ],
        ecuaciones=[
            Ecuacion("\\frac{\\Delta E}{E} = -shock\\cdot\\lambda", "la amplificación",
                     "el apalancamiento no crea el shock: lo MULTIPLICA — cada punto de caída de "
                     "activos son λ puntos de capital perdido (verificado exacto)."),
            Ecuacion("shock \\geq 1/\\lambda \\Rightarrow insolvencia", "el margen de seguridad",
                     "con λ=20 el colchón es 5%: la distancia entre 'sólido' e 'insolvente' es una "
                     "corrección de mercado ordinaria — por eso el apalancamiento se regula (Basilea, mención)."),
        ],
        intuicion=("El apalancamiento es un amplificador simétrico que solo se "
                   "recuerda en las malas: en el boom multiplica ganancias (y "
                   "nadie se queja), en la caída multiplica pérdidas (y todos se "
                   "sorprenden). La trampa del desapalancamiento cierra el círculo: "
                   "para sobrevivir hay que vender, vender baja los precios, "
                   "precios bajos destruyen más capital, que fuerza más ventas. "
                   "Ese lazo — no el shock inicial — es lo que convierte una "
                   "corrección en crisis (m79 lo formaliza como acelerador "
                   "financiero)."),
        equilibrio=("Balance contable exacto; el 'equilibrio' post-shock es "
                    "inestable si el desapalancamiento retroalimenta precios — la "
                    "diferencia entre una pérdida y una crisis está en si el lazo "
                    "de m79 se activa."),
        limitaciones=[
            "Precios de activos exógenos: el fire sale (ventas que bajan precios que fuerzan ventas) es el mecanismo REAL de crisis — aquí solo su primer paso (m79 lo cierra).",
            "Sin liquidez vs solvencia: un banco solvente puede caer por falta de liquidez (corrida, m73) — otra cara de la fragilidad.",
            "Un actor: el riesgo SISTÉMICO (correlación de balances, contagio) exige la red de m80.",
        ],
        evolucion=("Abre el nivel de crisis con el mecanismo común a casi todas: "
                   "el balance frágil. m72 le da un detonante (la burbuja que "
                   "revienta), m73 su versión de liquidez (la corrida), m79 cierra "
                   "el lazo precio-balance (acelerador financiero) y m80 lo pone en "
                   "red (sistémico)."),
    ),
    escenarios=[
        Escenario("correccion_ordinaria", "una caída de activos de 3% con λ=20",
                  {"shock": 3.0},
                  "el 60% del capital evaporado por una corrección que en un balance "
                  "sin deuda sería trivial: el apalancamiento convierte lo normal en "
                  "existencial.",
                  cadena=["caída de 3% en activos", "la deuda no cede: todo al capital",
                          "ΔE/E = −60% (×λ)", "λ salta", "presión a vender (m79)"]),
        Escenario("insolvencia", "el shock alcanza 1/λ: caída de 5%",
                  {"shock": 5.0},
                  "el capital se agota exacto: con λ=20 basta una caída de 5% para "
                  "la insolvencia — Bear Stearns y Lehman vivían en este margen "
                  "(mención).",
                  cadena=["shock = 1/λ", "la pérdida iguala al capital",
                          "E' = 0: insolvencia", "nadie presta al insolvente (m73)",
                          "colapso o rescate"]),
        Escenario("banca_conservadora", "el mismo shock con λ=8 (Basilea)",
                  {"lam": 8.0, "shock": 5.0},
                  "el capital cae 40% pero sobrevive: menos apalancamiento es menos "
                  "eficiencia en el boom y menos fragilidad en la caída — el "
                  "trade-off que regula Basilea (mención).",
                  cadena=["λ bajo (más capital)", "el mismo shock", "ΔE/E = −40% (menor ×λ)",
                          "sigue solvente", "la regulación compra resiliencia"]),
    ],
    verificaciones=[
        Verificacion("amplificación ΔE/E = −shock·λ exacta", _v_amplificacion),
        Verificacion("insolvencia cuando shock alcanza 1/λ", _v_insolvencia),
        Verificacion("desapalancar exige vender (contractivo)", _v_desapalancar_vende),
        Verificacion("sin shock ni presión, no hay ventas forzadas", _v_solvente_sin_ventas),
    ],
    notas="El apalancamiento amplifica en ambas direcciones — pero solo se recuerda en la caída. El lazo con el precio es m79.",
)
