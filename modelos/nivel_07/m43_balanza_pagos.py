# m43_balanza_pagos.py — balanza de pagos: la contabilidad externa (nivel 7).
#
# Doble partida con el resto del mundo:
#   CC = X − M + RN + TR        (bienes/servicios + rentas + transferencias)
#   CC + CF = ΔRIN              (lo que no financia el capital, lo ponen —
#                                o lo pierden — las reservas del banco central)
# Con flotación pura ΔRIN = 0 y la cuenta financiera es el espejo exacto de
# la corriente: TODO déficit se financia. La estructura recuerda a la peruana:
# rentas negativas (utilidades mineras) compensadas por remesas (menciones;
# los datos reales entran vía BCRP en m110).
#
# Procedencia: contabilidad de balanza de pagos (manual del FMI, mención) —
# conocimiento general; calibración didáctica.

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _cuentas(p):
    cc = p["X"] - p["M"] + p["RN"] + p["TR"]
    return cc, p["CF"], cc + p["CF"]


def _curvas(p):
    cc, cf, drin = _cuentas(p)
    cats = ["$X$", "$-M$", "$RN$", "$TR$", "$CC$", "$CF$", "$\\Delta RIN$"]
    vals = [p["X"], -p["M"], p["RN"], p["TR"], cc, cf, drin]
    cols = [config.AZUL2, config.ROJO, config.ROJO, config.VERDE,
            config.AZUL, config.VERDE, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$CC = {p['X']:.0f} - {p['M']:.0f} {p['RN']:+.0f} {p['TR']:+.0f} = {cc:+.0f}$\n"
                          f"$CC + CF = \\Delta RIN = {drin:+.0f}$\n"
                          "todo se financia: es doble partida")}


def _resultados(p):
    cc, cf, drin = _cuentas(p)
    return {"cuenta corriente CC": cc,
            "balanza comercial X−M": p["X"] - p["M"],
            "rentas netas RN": p["RN"], "transferencias TR (remesas)": p["TR"],
            "cuenta financiera CF (entrada neta)": cf,
            "ΔRIN (reservas del banco central)": drin,
            "CF que exigiría flotación pura": -cc}


def _ecuaciones_calibradas(p):
    cc, cf, drin = _cuentas(p)
    return [f"$CC = {p['X']:.0f} - {p['M']:.0f} + ({p['RN']:.0f}) + {p['TR']:.0f} = {cc:+.0f}$",
            f"$\\Delta RIN = {cc:+.0f} + {cf:+.0f} = {drin:+.0f}$"]


_P0 = {"X": 250.0, "M": 240.0, "RN": -30.0, "TR": 15.0, "CF": 20.0}


def _v_identidad():
    cc, cf, drin = _cuentas(_P0)
    return abs((cc + cf) - drin) < 1e-12, \
        f"CC + CF = ΔRIN exacto ({cc:+.0f} {cf:+.0f} = {drin:+.0f}): la doble partida no perdona"


def _v_flotacion_espejo():
    cc, _, _ = _cuentas(_P0)
    cf_flot = -cc
    drin = cc + cf_flot
    return abs(drin) < 1e-12, (f"con flotación pura (ΔRIN=0) la cuenta financiera es el espejo "
                               f"exacto de la corriente: CF = {cf_flot:+.0f} = −CC")


def _v_descomposicion():
    cc, _, _ = _cuentas(_P0)
    suma = _P0["X"] - _P0["M"] + _P0["RN"] + _P0["TR"]
    return abs(cc - suma) < 1e-12, "CC = comercial + rentas + transferencias, sin residuo"


def _v_defensa_gasta_reservas():
    _, _, drin = _cuentas(dict(_P0, CF=-60.0))
    return drin < 0, (f"si el capital huye (CF=−60) y nadie ajusta, ΔRIN = {drin:+.0f}: "
                      "el banco central financia la salida con reservas — el reloj de m50 y m74")


MODELO = Modelo(
    id="m43", nivel=7,
    nombre="Balanza de pagos",
    xlabel="", ylabel="Flujos externos (u.m.)",
    parametros=[
        Parametro("X", _P0["X"], 100, 400, 10, "Exportaciones X", grupo="cuenta corriente",
                  definicion="para Perú: cobre y minería mandan (m103)"),
        Parametro("M", _P0["M"], 100, 400, 10, "Importaciones M", grupo="cuenta corriente"),
        Parametro("RN", _P0["RN"], -80, 20, 5, "Rentas netas RN", grupo="cuenta corriente",
                  definicion="intereses y utilidades; negativa si el capital es extranjero"),
        Parametro("TR", _P0["TR"], 0, 60, 5, "Transferencias TR (remesas)", grupo="cuenta corriente"),
        Parametro("CF", _P0["CF"], -100, 100, 5, "Cuenta financiera CF", grupo="financiamiento",
                  definicion="entrada neta de capitales (IED, cartera, deuda)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Quién paga el déficit externo de un país — y por qué las reservas son el amortiguador de última instancia?",
        variables=[("CC", "cuenta corriente — el ahorro externo que se usa (o se presta)"),
                   ("CF", "cuenta financiera — el financiamiento que entra o huye"),
                   ("ΔRIN", "reservas — el residuo que absorbe lo que nadie financió")],
        derivacion=["CC = X - M + RN + TR",
                    "CC + CF = \\Delta RIN \\;\\;(doble\\;partida)",
                    "flotación\\;pura: \\;\\Delta RIN = 0 \\Rightarrow CF = -CC"],
        contexto=("Toda transacción con el exterior tiene dos patas: el bien que "
                  "cruza la frontera y el pago que la cruza en sentido contrario. La "
                  "balanza de pagos es esa doble partida elevada a país, y su "
                  "identidad central — CC + CF = ΔRIN — es el tablero donde se leen "
                  "los booms de materias primas, las fugas de capital y las defensas "
                  "cambiarias. La estructura didáctica aquí evoca la peruana: "
                  "superávit comercial minero, rentas negativas (utilidades que se "
                  "van) y remesas que suman."),
        autores=("Contabilidad estandarizada por el FMI (Manual de Balanza de Pagos, "
                 "mención); la lectura macro moderna viene del enfoque intertemporal "
                 "(m44)."),
        supuestos=["Es CONTABILIDAD ex post (como m02): se cumple siempre; el comportamiento llega en m44-m49.",
                   "Errores y omisiones se omiten (en los datos reales existen y se registran — mención).",
                   "CF agregada: no distingue IED estable de cartera volátil (la distinción importa en m75)."],
        ecuaciones=[
            Ecuacion("CC = X - M + RN + TR", "cuenta corriente",
                     "más que comercio: las rentas del capital (negativas si las minas son "
                     "extranjeras) y las remesas de los migrantes también son ingreso corriente."),
            Ecuacion("CC + CF = \\Delta RIN", "la identidad de financiamiento",
                     "un déficit corriente lo financia el capital (CF>0) o lo pagan las reservas "
                     "(ΔRIN<0): no hay tercera opción — de ahí el reloj de las crisis (m74)."),
        ],
        intuicion=("El 'déficit externo' no es un pecado sino una transacción: alguien "
                   "de afuera está financiando gasto interno. La pregunta correcta "
                   "nunca es '¿hay déficit?' sino '¿quién lo financia y qué compra?' "
                   "(m44). Y cuando el financiamiento se corta de golpe, la identidad "
                   "se cobra en reservas o en ajuste brusco: el sudden stop (m75)."),
        equilibrio=("No hay equilibrio que encontrar (identidad); el 'equilibrio' "
                    "económico — qué CC es sostenible — es el tema de m44 y del "
                    "nivel de deuda externa (nivel 9)."),
        limitaciones=[
            "Sin precios ni tipo de cambio: los FLUJOS responden a E (m45-m46) y a ingresos (m49) — aquí son perillas.",
            "CF homogénea: la composición (IED vs cartera) decide la fragilidad (m75).",
            "Las RIN parecen gratis: tienen costo de oportunidad y un piso crítico (m50, m74).",
        ],
        evolucion=("m44 le pone teoría a la CC (ahorro−inversión y los déficits "
                   "gemelos); m45-m48 le ponen precio (tipos de cambio y paridades); "
                   "m49 junta todo en el Mundell-Fleming; y m110 leerá esta identidad "
                   "con los datos del BCRP para el shock externo peruano."),
    ),
    escenarios=[
        Escenario("boom_del_cobre", "las exportaciones saltan de 250 a 310",
                  {"X": 310.0},
                  "la CC pasa a +55 y las reservas acumulan: el ciclo peruano de "
                  "términos de intercambio en su fase amable (m88, m103).",
                  cadena=["↑precio del cobre", "↑X", "CC → superávit",
                          "entra más de lo que sale", "ΔRIN > 0: el BCRP acumula"]),
        Escenario("fuga_de_capitales", "el financiamiento se revierte: CF = −60",
                  {"CF": -60.0},
                  "con la CC intacta, ΔRIN = −65: las reservas pagan la salida — el "
                  "primer acto de toda crisis cambiaria (m74) y el reloj del trilema (m50).",
                  cadena=["sube el riesgo o la FED (m48)", "CF se hace negativa",
                          "nadie financia la CC", "ΔRIN < 0: el BC vende reservas",
                          "si persiste: ajuste o crisis (m74-m75)"]),
        Escenario("remesas_al_alza", "las transferencias suben de 15 a 35",
                  {"TR": 35.0},
                  "la CC mejora sin exportar un kilo más: el amortiguador silencioso "
                  "de varias economías andinas.",
                  cadena=["migrantes envían más", "↑TR", "CC mejora",
                          "menos necesidad de financiamiento externo"]),
        Escenario("factura_minera", "las utilidades remesadas suben: RN = −60",
                  {"RN": -60.0},
                  "el superávit comercial convive con déficit corriente: exportar "
                  "mucho no basta si la renta del capital se va — la paradoja minera.",
                  cadena=["boom con capital extranjero", "↑ utilidades remesadas",
                          "RN más negativa", "CC empeora pese al superávit comercial"]),
    ],
    verificaciones=[
        Verificacion("identidad CC + CF = ΔRIN exacta", _v_identidad),
        Verificacion("flotación pura: CF = −CC (espejo exacto)", _v_flotacion_espejo),
        Verificacion("descomposición de la CC sin residuo", _v_descomposicion),
        Verificacion("la fuga se paga con reservas (reloj de m74)", _v_defensa_gasta_reservas),
    ],
    notas="La doble partida del país: todo déficit tiene financista — o funeral de reservas.",
)
