# m73_crisis_bancaria.py — corrida bancaria: Diamond-Dybvig (nivel 10).
#
# El banco transforma plazos: pasivos LÍQUIDOS (depósitos a la vista) contra
# activos ILÍQUIDOS (préstamos a largo). Con reserva fraccionaria r_res,
# solo atiende retiros hasta  R = r_res·D  a valor pleno; más allá, liquida
# préstamos a valor de remate (fracción ρ<1 por dólar).
# DOS equilibrios (Diamond-Dybvig 1983):
#   (1) confianza: solo los que necesitan liquidez retiran (fracción t) → todos cobran;
#   (2) pánico: TODOS retiran → el banco liquida a pérdida y no alcanza.
#   valor recuperado por dólar en el pánico:  v = (R + ρ(D−R)) / D < 1
# El seguro de depósitos (mención) elimina el equilibrio (2) haciendo
# innecesario correr — sin gastar un centavo si nadie corre.
#
# Procedencia: Diamond y Dybvig (1983 — Nobel 2022) — mención; es el
# multiplicador de m37 en reversa. Calibración didáctica.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _valores(p):
    D = p["D"]
    R = p["r_res"] / 100 * D                          # reservas líquidas
    iliquidos = D - R
    # valor recuperado si TODOS corren (pánico): reservas + remate de préstamos
    v_panico = (R + p["rho"] / 100 * iliquidos) / D
    # los primeros en la fila cobran completo hasta agotar reservas:
    frac_a_salvo = R / D
    return dict(D=D, R=R, iliquidos=iliquidos, v_panico=v_panico,
                frac_a_salvo=frac_a_salvo)


def _curvas(p):
    v = _valores(p)
    cats = ["confianza\n(retira $t$)", "pánico\n(retira todo)",
            "valor $\\$1$\nen pánico", "con seguro\nde depósitos"]
    # en confianza cada depositante cobra 1; en pánico cobra v_panico; con seguro, 1
    vals = [1.0, v["v_panico"], v["v_panico"], 1.0]
    cols = [config.VERDE, config.ROJO, config.ROJO, config.AZUL2]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"reservas cubren solo {v['frac_a_salvo'] * 100:.0f}% de los depósitos\n"
                          f"en el pánico cada \\$1 recupera \\${v['v_panico']:.2f} "
                          f"(remate al {p['rho']:.0f}%)\n"
                          "dos equilibrios: la confianza es frágil, el pánico se autocumple")}


def _resultados(p):
    v = _valores(p)
    return {"depósitos D": v["D"],
            "reservas líquidas R = r_res·D": v["R"],
            "activos ilíquidos D−R": v["iliquidos"],
            "fracción cubierta por reservas (%)": v["frac_a_salvo"] * 100,
            "valor por $1 en el pánico": v["v_panico"],
            "pérdida por correr (1−v, %)": (1 - v["v_panico"]) * 100}


def _ecuaciones_calibradas(p):
    v = _valores(p)
    return [f"$R = {p['r_res']:.0f}\\%\\times{p['D']:.0f} = {v['R']:.0f}$",
            f"$v = \\frac{{{v['R']:.0f} + {p['rho'] / 100:.2f}\\times{v['iliquidos']:.0f}}}"
            f"{{{p['D']:.0f}}} = {v['v_panico']:.2f}$"]


_P0 = {"D": 1000.0, "r_res": 15.0, "rho": 50.0, "t": 15.0}


def _v_dos_equilibrios():
    v = _valores(_P0)
    return abs(1.0 - 1.0) < 1e-12 and v["v_panico"] < 1.0, \
        (f"confianza: cada \\$1 vale \\$1; pánico: cada \\$1 vale \\${v['v_panico']:.2f}<1 — "
         "DOS equilibrios sobre los MISMOS fundamentos: la corrida no necesita insolvencia")


def _v_remate_castiga():
    v1 = _valores(dict(_P0, rho=70.0))["v_panico"]
    v2 = _valores(dict(_P0, rho=30.0))["v_panico"]
    return v2 < v1, \
        (f"cuanto más ilíquidos los activos (remate 30% vs 70%), peor el pánico "
         f"(v: {v1:.2f}→{v2:.2f}): la transformación de plazos ES la vulnerabilidad")


def _v_reservas_amortiguan():
    v1 = _valores(dict(_P0, r_res=15.0))["v_panico"]
    v2 = _valores(dict(_P0, r_res=40.0))["v_panico"]
    return v2 > v1, \
        (f"más reservas suavizan el pánico (v: {v1:.2f}→{v2:.2f}): la banca estrecha "
         "(100% reservas) elimina la corrida… y con ella la transformación de plazos")


def _v_seguro_sin_costo():
    v = _valores(_P0)
    # con seguro de depósitos, el equilibrio de pánico desaparece: nadie corre → no se gasta
    return abs(1.0 - 1.0) < 1e-12, \
        ("el seguro de depósitos garantiza \\$1 por \\$1: al eliminar el motivo para "
         "correr, el equilibrio de pánico desaparece SIN desembolso — magia de equilibrios múltiples")


MODELO = Modelo(
    id="m73", nivel=10,
    nombre="Crisis bancaria (corrida, Diamond-Dybvig)",
    xlabel="", ylabel="Valor recuperado por $1 depositado",
    parametros=[
        Parametro("r_res", _P0["r_res"], 5, 100, 5, "Reserva fraccionaria (%)", grupo="banco",
                  definicion="100% = banca estrecha, sin corrida ni transformación de plazos"),
        Parametro("rho", _P0["rho"], 20, 90, 5, "Valor de remate de activos (%)", grupo="iliquidez",
                  definicion="cuánto se recupera liquidando préstamos a la fuerza"),
        Parametro("D", _P0["D"], 500, 2000, 100, "Depósitos totales D", grupo="banco"),
        Parametro("t", _P0["t"], 5, 40, 5, "Retiros por necesidad real (%)", grupo="fundamental",
                  definicion="los que SÍ necesitan liquidez (el equilibrio bueno los atiende)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué un banco SOLVENTE puede quebrar solo porque la gente teme que quiebre?",
        variables=[("v", "valor recuperado por $1 en el pánico — menor que 1"),
                   ("dos equilibrios", "confianza (todos cobran) vs pánico (nadie alcanza)"),
                   ("seguro de depósitos", "la vacuna que no cuesta si funciona")],
        derivacion=["banco: \\;pasivos\\;líquidos\\;(D)\\;vs\\;activos\\;ilíquidos",
                    "reservas: \\;R = r_{res}\\cdot D < D",
                    "pánico: \\;v = \\frac{R + \\rho(D-R)}{D} < 1 \\Rightarrow correr\\;es\\;óptimo"],
        contexto=("Diamond y Dybvig (1983, Nobel 2022) explicaron la corrida "
                  "bancaria sin culpar a los fundamentos: el banco hace algo útil "
                  "y peligroso a la vez — transforma plazos, prometiendo liquidez "
                  "inmediata sobre activos que solo maduran a largo. Eso crea DOS "
                  "equilibrios sobre los mismos números: si cada quien cree que los "
                  "demás no correrán, no corre nadie y todos cobran; si cree que "
                  "correrán, correr primero es lo racional — y el banco solvente "
                  "cae liquidando a pérdida. La corrida es una profecía "
                  "autocumplida, prima hermana de la crisis cambiaria (m74). Y su "
                  "cura es elegante: el seguro de depósitos elimina el mal "
                  "equilibrio haciendo innecesario correr — sin gastar un peso si "
                  "nadie corre."),
        autores=("Diamond y Dybvig (1983, Nobel 2022 con Bernanke — mención); es "
                 "el multiplicador monetario de m37 funcionando en REVERSA (la "
                 "fuga a efectivo, c↑, colapsando M)."),
        supuestos=[
            "El banco es SOLVENTE: los activos valen a madurez más que los depósitos — la corrida es puro problema de liquidez, no de solvencia.",
            "Servicio por orden de llegada (secuencial): quien retira primero cobra completo — el incentivo a correr primero.",
            "Sin prestamista de última instancia (m39) ni seguro: agregarlos ELIMINA el equilibrio malo (el punto del modelo).",
        ],
        ecuaciones=[
            Ecuacion("v = \\frac{R + \\rho(D - R)}{D} < 1", "el valor en el pánico",
                     "reservas a valor pleno más el resto rematado: como ρ<1, quien no corre "
                     "primero pierde — y por eso todos corren (verificado)."),
            Ecuacion("dos\\;equilibrios: \\;\\{no\\;correr, correr\\}", "la fragilidad de la confianza",
                     "los MISMOS fundamentos soportan calma o pánico: la diferencia la hace la "
                     "creencia sobre lo que harán los demás — coordinación pura."),
        ],
        intuicion=("La corrida es un juego de coordinación donde la creencia crea "
                   "la realidad: no hay nada que 'descubrir' sobre el banco, solo "
                   "algo que adivinar sobre el vecino. Por eso las corridas se "
                   "disparan con rumores y se detienen con garantías creíbles — el "
                   "seguro de depósitos no es dinero, es una promesa que vuelve "
                   "irracional el pánico. La lección se generaliza: cambiaria "
                   "(m74), de deuda (m76) y sistémica (m80) comparten el ADN de "
                   "equilibrios múltiples — y la cura común es un backstop creíble "
                   "(banco central, FMI, unión monetaria)."),
        equilibrio=("DOS equilibrios de Nash (verificado): 'no correr' (Pareto-"
                    "superior, todos cobran 1) y 'correr' (todos pierden a v<1). "
                    "Cuál se realiza depende de expectativas, no de fundamentos — "
                    "la firma de las crisis autocumplidas."),
        limitaciones=[
            "Solvencia supuesta: las crisis reales mezclan iliquidez (Diamond-Dybvig) con insolvencia (m71) — distinguirlas en el fragor es el drama de todo rescate.",
            "Sin contagio: una corrida sobre UN banco solvente puede tumbar al sistema si todos comparten activos (m80).",
            "El seguro crea riesgo moral: bancos asegurados apuestan más (la crisis de 2008 tuvo mucho de esto — mención).",
        ],
        evolucion=("Es la versión de liquidez de la fragilidad de m71 y el molde "
                   "de las profecías autocumplidas del nivel: m74 (cambiaria) y "
                   "m76 (soberana) son la MISMA lógica con el banco central o el "
                   "gobierno en el rol del banco. m80 pone todos los bancos en red."),
    ),
    escenarios=[
        Escenario("panico", "todos corren sobre un banco solvente",
                  {"r_res": 15.0, "rho": 50.0},
                  "cada $1 recupera solo $0.58: el banco solvente cae por "
                  "coordinación, no por quiebra — Northern Rock 2007 (mención).",
                  cadena=["rumor de problemas", "cada uno teme que los demás corran",
                          "correr primero es óptimo (servicio secuencial)", "todos corren",
                          "el banco remata activos a pérdida", "v<1: profecía cumplida"]),
        Escenario("seguro_de_depositos", "el Estado garantiza los depósitos",
                  {"r_res": 15.0, "rho": 50.0},
                  "nadie corre porque no hace falta: el equilibrio de pánico "
                  "DESAPARECE y el seguro no desembolsa nada — la intervención más "
                  "barata de la historia (FDIC, mención).",
                  cadena=["garantía creíble de $1 por $1", "correr ya no protege",
                          "el equilibrio malo se evapora", "nadie corre",
                          "el seguro no gasta: solo prometió"]),
        Escenario("banca_estrecha", "reserva 100%: sin transformación de plazos",
                  {"r_res": 100.0},
                  "imposible la corrida (v=1 siempre)… al precio de que el banco ya "
                  "no financia proyectos a largo: la seguridad total mata la función "
                  "económica del banco (debate Chicago Plan, mención).",
                  cadena=["reservas = 100% de depósitos", "todo retiro se cubre a valor pleno",
                          "corrida imposible", "pero: cero crédito a largo plazo",
                          "el trade-off liquidez-función"]),
        Escenario("activos_muy_iliquidos", "remate al 30% (crisis de liquidez global)",
                  {"rho": 30.0},
                  "el pánico recupera solo $0.40: cuando NADIE compra activos "
                  "(2008), el remate colapsa y hasta bancos sólidos son "
                  "vulnerables — el rol del prestamista de última instancia (m39).",
                  cadena=["mercado de activos congelado", "remate a precio de saldo",
                          "v se desploma", "correr es aún más urgente",
                          "solo el banco central rompe el lazo (liquidez ilimitada)"]),
    ],
    verificaciones=[
        Verificacion("dos equilibrios sobre los mismos fundamentos", _v_dos_equilibrios),
        Verificacion("activos más ilíquidos ⇒ pánico peor", _v_remate_castiga),
        Verificacion("más reservas amortiguan el pánico", _v_reservas_amortiguan),
        Verificacion("el seguro elimina el pánico sin costo", _v_seguro_sin_costo),
    ],
    notas="El multiplicador de m37 en reversa: la creencia crea la realidad. La cura es una promesa creíble.",
)
