"""simuladores/macro/modelos/nivel_09/m62_restriccion_presupuestaria.py — la restricción presupuestaria del gobierno (nivel 9).

La contabilidad que gobierna todo el nivel: cada sol de USO se financia:
  G + r·B  =  T + ΔB + SM
  (gasto + intereses = impuestos + deuda nueva + señoreaje)
Distinción operativa clave:
  déficit PRIMARIO  = G − T            (lo que controla la política HOY)
  déficit TOTAL     = G + r·B − T      (lo que hay que financiar)
La diferencia — los intereses r·B — es la herencia del pasado: el gasto que
ningún ministro decide y todos pagan.

Procedencia: contabilidad fiscal estándar (conocimiento general);
calibración didáctica.
"""

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _cuentas(p):
    intereses = p["r"] / 100 * p["B"]
    primario = p["G"] - p["T"]
    total = primario + intereses
    dB = total - p["SM"]
    return intereses, primario, total, dB


def _curvas(p):
    intereses, primario, total, dB = _cuentas(p)
    cats = ["$G-T$\n(primario)", "$r{\\cdot}B$\n(intereses)", "déficit\ntotal",
            "$\\Delta B$\n(deuda nueva)", "$SM$\n(señoreaje)"]
    vals = [primario, intereses, total, dB, p["SM"]]
    cols = [config.AZUL2, config.ROJO, config.AZUL, config.DORADO, config.VERDE]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$G + rB = T + \\Delta B + SM$\n"
                          f"${p['G']:.0f} + {intereses:.0f} = {p['T']:.0f} + {dB:.0f} + {p['SM']:.0f}$\n"
                          "todo uso tiene fuente: no hay cuarta columna")}


def _resultados(p):
    intereses, primario, total, dB = _cuentas(p)
    return {"déficit primario G−T": primario,
            "intereses r·B (la herencia)": intereses,
            "déficit total": total,
            "deuda nueva ΔB": dB,
            "señoreaje SM": p["SM"],
            "comprobación usos−fuentes": (p["G"] + intereses) - (p["T"] + dB + p["SM"])}


def _ecuaciones_calibradas(p):
    intereses, primario, total, dB = _cuentas(p)
    return [f"$déficit\\;primario = {p['G']:.0f} - {p['T']:.0f} = {primario:.0f}$",
            f"$déficit\\;total = {primario:.0f} + {intereses:.0f} = {total:.0f}$",
            f"$\\Delta B = {total:.0f} - {p['SM']:.0f} = {dB:.0f}$"]


_P0 = {"G": 100.0, "T": 90.0, "B": 200.0, "r": 5.0, "SM": 2.0}


def _v_identidad():
    intereses, primario, total, dB = _cuentas(_P0)
    res = (_P0["G"] + intereses) - (_P0["T"] + dB + _P0["SM"])
    return abs(res) < 1e-12, "usos = fuentes exacto: la restricción no es una teoría, es aritmética"


def _v_primario_vs_total():
    intereses, primario, total, dB = _cuentas(_P0)
    return abs(total - (primario + intereses)) < 1e-12, \
        (f"total ({total:.0f}) = primario ({primario:.0f}) + intereses ({intereses:.0f}): "
         "la herencia del pasado se paga antes de decidir nada")


def _v_herencia_crece_con_B():
    i1 = _cuentas(_P0)[0]
    i2 = _cuentas(dict(_P0, B=400.0))[0]
    return abs(i2 - 2 * i1) < 1e-12, \
        (f"duplicar la deuda duplica los intereses ({i1:.0f}→{i2:.0f}): el gasto que "
         "ningún ministro decide — la semilla de la bola de nieve (m63)")


def _v_senoreaje_sustituye_deuda():
    dB1 = _cuentas(_P0)[3]
    dB2 = _cuentas(dict(_P0, SM=10.0))[3]
    return abs((dB1 - dB2) - 8.0) < 1e-12, \
        ("cada sol de señoreaje es un sol menos de deuda nueva: la puerta a la "
         "imprenta (m36) está DENTRO de esta identidad")


MODELO = Modelo(
    id="m62", nivel=9,
    nombre="Restricción presupuestaria del gobierno",
    xlabel="", ylabel="Flujos fiscales (u.m.)",
    parametros=[
        Parametro("G", _P0["G"], 60, 160, 5, "Gasto público G", grupo="decisiones de hoy"),
        Parametro("T", _P0["T"], 60, 160, 5, "Impuestos T", grupo="decisiones de hoy"),
        Parametro("B", _P0["B"], 0, 600, 25, "Deuda heredada B", grupo="herencia",
                  definicion="el pasado que cobra intereses"),
        Parametro("r", _P0["r"], 1, 12, 0.5, "Tasa de interés r (%)", grupo="herencia"),
        Parametro("SM", _P0["SM"], 0, 15, 1, "Señoreaje SM", grupo="financiamiento",
                  definicion="la imprenta (m36): tentadora y prohibida al BCRP (mención)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿De dónde sale cada sol que el gobierno gasta — y cuánto del presupuesto lo decidió el pasado?",
        variables=[("G − T", "el primario — lo único que la política controla HOY"),
                   ("r·B", "los intereses — la herencia que se paga primero"),
                   ("ΔB, SM", "las dos salidas: más deuda o imprenta (m36)")],
        derivacion=["G + r\\,B = T + \\Delta B + SM",
                    "d\\acute{e}ficit\\;primario = G - T",
                    "d\\acute{e}ficit\\;total = (G - T) + r\\,B"],
        contexto=("Todo el nivel 9 vive dentro de una identidad: el gobierno, como "
                  "cualquier deudor, financia lo que gasta. La distinción "
                  "primario/total — que parece contable — es LA distinción política: "
                  "los intereses r·B son el voto del pasado en el presupuesto de "
                  "hoy, y cuando crecen (por B o por r), desplazan gasto sin que "
                  "nadie lo haya decidido. Las tres salidas del déficit — impuestos, "
                  "deuda, imprenta — son los tres capítulos siguientes del nivel "
                  "(m63-m65, m67, y la puerta ya conocida de m36)."),
        autores=("Contabilidad fiscal estándar (manuales de finanzas públicas, "
                 "conocimiento general); su lectura intertemporal — la deuda como "
                 "impuestos diferidos — es Barro (m67, mención)."),
        supuestos=["Un período y una tasa única r (la estructura de vencimientos llega con los datos, m108).",
                   "SM como flujo dado: su costo inflacionario vive en m36 (y su prohibición peruana: Constitución de 1993, mención).",
                   "Sin default: la deuda siempre se honra (el nivel 10 rompe esto)."],
        ecuaciones=[
            Ecuacion("G + r\\,B = T + \\Delta B + SM", "la identidad de financiamiento",
                     "no hay cuarta columna: lo que no cubren impuestos ni imprenta, lo cubre "
                     "deuda nueva — que mañana será más r·B."),
            Ecuacion("d\\acute{e}ficit\\;total = primario + r\\,B", "la herencia visible",
                     "separa lo que el gobierno DECIDE (primario) de lo que ARRASTRA (intereses): "
                     "toda la dinámica de m63-m64 nace de esta separación."),
        ],
        intuicion=("Leer un presupuesto empieza por esta resta: ¿cuánto del déficit "
                   "es decisión y cuánto es herencia? Un país con primario "
                   "equilibrado puede tener déficit total creciente solo porque r·B "
                   "crece — y ese es exactamente el mecanismo de bola de nieve que "
                   "m63 pone en movimiento. La identidad también muestra la "
                   "tentación: el señoreaje 'financia' sin impuestos ni deuda… al "
                   "precio que m36 ya cobró."),
        equilibrio=("Identidad contable (se cumple siempre); el 'equilibrio fiscal' "
                    "— qué primario estabiliza la deuda — es la pregunta de m63-m64."),
        limitaciones=[
            "Estática: la deuda de mañana (ΔB) vuelve como intereses de pasado mañana — la dinámica es m63.",
            "Sin PIB: los niveles absolutos engañan; el ratio deuda/PIB (m64) es la métrica que importa.",
            "r exógena: en la realidad r responde al propio B (prima de riesgo, m48/m76) — el círculo vicioso de las crisis.",
        ],
        evolucion=("m63 itera esta identidad en el tiempo (la bola de nieve), m64 "
                   "la divide por el PIB (la ecuación central del nivel), m65 "
                   "pregunta cuánta deuda cabe, y m67 pregunta si los hogares ven "
                   "a través de ella (la deuda como impuestos diferidos)."),
    ),
    escenarios=[
        Escenario("apreton_primario", "los impuestos suben de 90 a 105",
                  {"T": 105.0},
                  "el primario pasa a superávit (−5) pero el déficit total sigue "
                  "positivo (+5): los intereses no negocian — la herencia manda.",
                  cadena=["↑T", "primario a superávit", "los intereses r·B siguen intactos",
                          "el total mejora solo lo que el primario dio", "ΔB cae pero no a cero"]),
        Escenario("herencia_pesada", "la tasa sube de 5% a 9%",
                  {"r": 9.0},
                  "los intereses saltan de 10 a 18 sin que nadie gaste un sol más: "
                  "el presupuesto lo reescribió el mercado de bonos (m48).",
                  cadena=["↑r (mercado o FED)", "r·B salta", "déficit total crece con primario intacto",
                          "más ΔB hoy", "más intereses mañana: la espiral de m63"]),
        Escenario("tentacion_de_la_imprenta", "señoreaje de 2 a 10",
                  {"SM": 10.0},
                  "la deuda nueva cae uno a uno con la emisión: la identidad no "
                  "prohíbe la imprenta — solo la Laffer de m36 (y la ley) lo hacen.",
                  cadena=["↑SM", "ΔB baja uno a uno", "el déficit se 'financia' sin bonos",
                          "la factura llega por m36: impuesto inflación"]),
    ],
    verificaciones=[
        Verificacion("usos = fuentes exacto (la identidad)", _v_identidad),
        Verificacion("total = primario + intereses", _v_primario_vs_total),
        Verificacion("la herencia escala con B (semilla de m63)", _v_herencia_crece_con_B),
        Verificacion("señoreaje sustituye deuda uno a uno", _v_senoreaje_sustituye_deuda),
    ],
    notas="La identidad madre del nivel 9: primario (decisión) + intereses (herencia) = deuda nueva + imprenta.",
)
