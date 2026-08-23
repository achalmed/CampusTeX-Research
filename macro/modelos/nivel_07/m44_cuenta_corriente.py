# m44_cuenta_corriente.py — cuenta corriente: ahorro menos inversión (nivel 7).
#
# La identidad que cambia la conversación:
#   CC = S − I = (S_p − I) + (T − G)
# El "déficit externo" deja de ser un problema comercial y se vuelve un hecho
# de AHORRO: quien invierte más de lo que ahorra, importa ahorro del resto del
# mundo. Corolario célebre: los DÉFICITS GEMELOS (más déficit fiscal ⇒ más
# déficit externo, ceteris paribus).
#
# Procedencia: identidad de cuentas nacionales abiertas (conocimiento
# general); enfoque intertemporal de la CC: Obstfeld-Rogoff (mención).

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _cc(p):
    priv = p["Sp"] - p["I"]
    fisc = p["T"] - p["G"]
    return priv, fisc, priv + fisc


def _curvas(p):
    priv, fisc, cc = _cc(p)
    cats = ["$S_p - I$\n(privado)", "$T - G$\n(fiscal)", "$CC$"]
    vals = [priv, fisc, cc]
    cols = [config.AZUL2, config.ROJO, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"$CC = ({p['Sp']:.0f}-{p['I']:.0f}) + ({p['T']:.0f}-{p['G']:.0f}) "
                          f"= {cc:+.0f}$\n"
                          "déficit externo = ahorro nacional insuficiente")}


def _resultados(p):
    priv, fisc, cc = _cc(p)
    return {"cuenta corriente CC": cc,
            "balance privado Sp − I": priv,
            "balance fiscal T − G": fisc,
            "ahorro nacional S = Sp + (T−G)": p["Sp"] + fisc,
            "ahorro externo usado (−CC)": -cc}


def _ecuaciones_calibradas(p):
    priv, fisc, cc = _cc(p)
    return [f"$CC = ({p['Sp']:.0f} - {p['I']:.0f}) + ({p['T']:.0f} - {p['G']:.0f}) = {cc:+.0f}$"]


_P0 = {"Sp": 190.0, "I": 200.0, "T": 150.0, "G": 145.0}


def _v_identidad():
    priv, fisc, cc = _cc(_P0)
    return abs(cc - (priv + fisc)) < 1e-12, \
        f"CC = (Sp−I) + (T−G) exacta: {priv:+.0f} {fisc:+.0f} = {cc:+.0f}"


def _v_gemelos():
    cc0 = _cc(_P0)[2]
    cc1 = _cc(dict(_P0, G=_P0["G"] + 30))[2]
    return abs((cc1 - cc0) + 30) < 1e-12, \
        ("con Sp, I, T fijos, ΔCC = −ΔG exacto: +30 de déficit fiscal son +30 de "
         "déficit externo — los gemelos en su versión contable pura")


def _v_espejo_m43():
    cc = _cc(_P0)[2]
    return abs(-cc - 5.0) < 1e-12, (f"CC = {cc:+.0f} implica usar {-cc:.0f} de ahorro externo: "
                                    "exactamente el CF de flotación pura de m43")


def _v_inversion_deficit():
    cc0 = _cc(_P0)[2]
    cc1 = _cc(dict(_P0, I=240.0))[2]
    return cc1 < cc0, (f"un boom de inversión (I: 200→240) abre la CC a {cc1:+.0f}: "
                       "el 'déficit bueno' — se importa ahorro para construir capacidad")


MODELO = Modelo(
    id="m44", nivel=7,
    nombre="Cuenta corriente (ahorro − inversión)",
    xlabel="", ylabel="Balances (u.m.)",
    parametros=[
        Parametro("Sp", _P0["Sp"], 100, 300, 5, "Ahorro privado Sp", grupo="privado"),
        Parametro("I", _P0["I"], 100, 300, 5, "Inversión I", grupo="privado",
                  definicion="si supera al ahorro, alguien de afuera pone la diferencia"),
        Parametro("T", _P0["T"], 80, 250, 5, "Ingresos fiscales T", grupo="fiscal"),
        Parametro("G", _P0["G"], 80, 250, 5, "Gasto público G", grupo="fiscal"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Por qué el déficit externo se decide en el ahorro y no en la aduana?",
        variables=[("CC", "cuenta corriente — el ahorro que sobra (o falta)"),
                   ("Sp − I", "balance privado — hogares y empresas"),
                   ("T − G", "balance fiscal — el gemelo potencial")],
        derivacion=["Y = C + I + G + CC \\;\\;(demanda\\;abierta)",
                    "Y - T - C = S_p \\;\\Rightarrow\\; CC = S_p - I + (T - G)",
                    "\\Delta G \\uparrow,\\;resto\\;fijo \\;\\Rightarrow\\; \\Delta CC = -\\Delta G"],
        contexto=("Mientras el debate público pelea con aranceles y 'competitividad', "
                  "la identidad dice otra cosa: la cuenta corriente es la diferencia "
                  "entre lo que un país ahorra y lo que invierte. EE.UU. en los 80 "
                  "estrenó el corolario: los recortes de impuestos abrieron el "
                  "déficit fiscal y — gemelo mediante — el externo. El enfoque "
                  "intertemporal (Obstfeld-Rogoff, mención) completa la lectura: la "
                  "CC es el canal por el que los países se prestan consumo e "
                  "inversión a través del tiempo."),
        autores=("Identidad de cuentas nacionales abiertas (conocimiento general); "
                 "enfoque intertemporal: Obstfeld y Rogoff (mención); el debate de "
                 "los gemelos: años 80 (mención)."),
        supuestos=["Contabilidad ex post: los gemelos EXACTOS requieren ceteris paribus (Sp e I fijos) — la equivalencia ricardiana (m67) rompería el gemelo vía Sp.",
                   "Sin valoración: no distingue si el déficit financia inversión productiva o consumo (la distinción decide la sostenibilidad).",
                   "Un período: la restricción intertemporal (pagar después) llega con la deuda (nivel 9)."],
        ecuaciones=[
            Ecuacion("CC = (S_p - I) + (T - G)", "la cuenta corriente como ahorro neto",
                     "dos balances y nada más: el externo es la SUMA del privado y el fiscal — "
                     "toda política que toque S, I, T o G toca la CC."),
            Ecuacion("\\Delta CC = -\\Delta G\\big|_{S_p,I,T}", "déficits gemelos",
                     "el caso puro: cada sol de gasto público no financiado con impuestos ni "
                     "ahorro privado extra se importa."),
        ],
        intuicion=("El truco mental: reemplazar 'déficit externo' por 'importación de "
                   "ahorro'. De inmediato las preguntas cambian: ¿para qué se usa ese "
                   "ahorro (I o C)?, ¿quién lo trae (m43: IED o cartera)?, ¿hasta "
                   "cuándo (nivel 9)? Un déficit que financia minas puede ser "
                   "virtuoso; uno que financia consumo público, un gemelo camino a "
                   "m76."),
        equilibrio=("Identidad, no equilibrio. El 'nivel correcto' de CC es una "
                    "pregunta intertemporal: suavizar consumo e inversión en el "
                    "tiempo — el país como hogar de m03/m05 escalado."),
        limitaciones=[
            "El gemelo exacto es frágil: si los hogares anticipan impuestos (m67) o la inversión responde, el coeficiente empírico es < 1.",
            "Sin precios: E y el RER (m45-m46) son los que mueven X y M detrás de estas letras.",
            "No dice nada de sostenibilidad: eso exige la dinámica de deuda externa (m64 en versión externa).",
        ],
        evolucion=("Con las cantidades (m43) y el ahorro (m44) entendidos, faltan "
                   "los PRECIOS del comercio: el tipo de cambio nominal (m45), el "
                   "real (m46) y sus anclas (m47-m48), para llegar armados al "
                   "Mundell-Fleming (m49)."),
    ),
    escenarios=[
        Escenario("deficits_gemelos", "expansión fiscal sin financiamiento: G de 145 a 175",
                  {"G": 175.0},
                  "la CC pasa de −5 a −35: cada sol del fisco se importó — el "
                  "experimento de los 80 en cuatro barras.",
                  cadena=["↑G sin ↑T", "↓(T−G)", "ahorro nacional cae",
                          "la inversión no encuentra ahorro local", "ΔCC = −ΔG: gemelos"]),
        Escenario("boom_de_inversion", "la inversión salta a 240 (proyectos mineros)",
                  {"I": 240.0},
                  "déficit externo de 45… financiando capacidad futura: el 'déficit "
                  "bueno' — la CC como préstamo intertemporal.",
                  cadena=["proyectos rentables > ahorro local", "↑I",
                          "se importa ahorro (CC < 0)", "si I es productiva, se paga sola"]),
        Escenario("ajuste_fiscal", "consolidación: G baja a 120",
                  {"G": 120.0},
                  "la CC pasa a +25: el ajuste fiscal ES política externa — la "
                  "receta estándar ante gemelos desbocados.",
                  cadena=["↓G", "↑(T−G)", "↑ahorro nacional", "CC mejora uno a uno"]),
    ],
    verificaciones=[
        Verificacion("identidad CC = (Sp−I)+(T−G) exacta", _v_identidad),
        Verificacion("gemelos puros: ΔCC = −ΔG exacto", _v_gemelos),
        Verificacion("coherencia con m43 (CF espejo)", _v_espejo_m43),
        Verificacion("el boom de inversión abre la CC (déficit 'bueno')", _v_inversion_deficit),
    ],
    notas="Cambiar 'déficit externo' por 'importación de ahorro' reordena todas las preguntas.",
)
