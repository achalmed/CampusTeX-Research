"""simuladores/macro/modelos/nivel_09/m67_equivalencia_ricardiana.py — equivalencia ricardiana (nivel 9).

¿La deuda pública es riqueza? Barro (1974): NO — es impuestos DIFERIDOS.
Una rebaja dT financiada con bonos que se repagan mañana con intereses:
  VP de los impuestos futuros = dT·(1+r)/(1+r) = dT   (exacto)
El hogar RICARDIANO lo ve y ahorra la rebaja completa: consumo intacto,
ahorro privado +dT compensa el desahorro público −dT: NADA real cambia.
La equivalencia se rompe con hogares "mano a boca" (fracción λ, sin acceso
al crédito): ellos gastan mpc de la rebaja — y solo ellos.
  dC = λ·mpc·dT ;  dS_nacional = −dC

Procedencia: Barro (1974, "Are Government Bonds Net Wealth?" — mención);
el antecedente escéptico es el propio Ricardo (mención) — conocimiento
general.
"""

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _efectos(p):
    dC = p["lam"] * p["mpc"] * p["dT"]
    dS_priv = p["dT"] - dC
    dS_pub = -p["dT"]
    return dC, dS_priv, dS_pub, dS_priv + dS_pub


def _curvas(p):
    dC, dS_priv, dS_pub, dS_nac = _efectos(p)
    cats = ["$\\Delta C$\n(demanda)", "$\\Delta S_{priv}$", "$\\Delta S_{pub}$",
            "$\\Delta S_{nacional}$"]
    vals = [dC, dS_priv, dS_pub, dS_nac]
    cols = [config.ROJO, config.AZUL2, config.GRIS, config.DORADO]
    return {"barras": (cats, vals, cols),
            "anotacion": (f"rebaja dT = {p['dT']:.0f} financiada con bonos\n"
                          f"VP de impuestos futuros = $dT\\,(1+r)/(1+r)$ = {p['dT']:.0f}\n"
                          f"con λ = {p['lam']:.1f}, se gasta solo {dC:.1f}")}


def _resultados(p):
    dC, dS_priv, dS_pub, dS_nac = _efectos(p)
    return {"ΔC (efecto demanda)": dC,
            "Δ ahorro privado": dS_priv,
            "Δ ahorro público": dS_pub,
            "Δ ahorro nacional": dS_nac,
            "VP impuestos futuros (= dT)": p["dT"],
            "fuga ricardiana (dT − ΔC)": p["dT"] - dC}


def _ecuaciones_calibradas(p):
    dC = p["lam"] * p["mpc"] * p["dT"]
    return [f"$VP = {p['dT']:.0f} \\times \\frac{{1+{p['r'] / 100:.2f}}}{{1+{p['r'] / 100:.2f}}} = {p['dT']:.0f}$",
            f"$\\Delta C = {p['lam']:.1f} \\times {p['mpc']:.1f} \\times {p['dT']:.0f} = {dC:.1f}$"]


_P0 = {"dT": 10.0, "r": 5.0, "lam": 0.3, "mpc": 0.8}


def _v_mundo_ricardiano():
    dC, dS_priv, dS_pub, dS_nac = _efectos(dict(_P0, lam=0.0))
    ok = abs(dC) < 1e-12 and abs(dS_priv - _P0["dT"]) < 1e-12 and abs(dS_nac) < 1e-12
    return ok, ("con λ=0: ΔC=0, el ahorro privado sube EXACTAMENTE dT y el nacional no se "
                "mueve — la rebaja se guardó entera para los impuestos que vienen")


def _v_vp_impuestos():
    vp = _P0["dT"] * (1 + _P0["r"] / 100) / (1 + _P0["r"] / 100)
    return abs(vp - _P0["dT"]) < 1e-12, \
        (f"el valor presente del repago = dT = {vp:.0f} exacto: la deuda pública es "
         "impuestos diferidos — a cualquier tasa r")


def _v_ruptura_lineal():
    dC1 = _efectos(dict(_P0, lam=0.3))[0]
    dC2 = _efectos(dict(_P0, lam=0.6))[0]
    return abs(dC2 - 2 * dC1) < 1e-12, \
        (f"ΔC escala lineal con λ ({dC1:.1f}→{dC2:.1f}): la equivalencia se rompe "
         "exactamente en proporción a los hogares sin acceso al crédito")


def _v_fuga_nacional():
    dC, dS_priv, dS_pub, dS_nac = _efectos(_P0)
    return abs(dS_nac + dC) < 1e-12, \
        ("ΔS_nacional = −ΔC exacto: lo único que la rebaja 'cuesta' al ahorro del país "
         "es lo que los restringidos gastan — el resto es un pase de manos")


MODELO = Modelo(
    id="m67", nivel=9,
    nombre="Equivalencia ricardiana",
    xlabel="", ylabel="Variaciones (u.m.)",
    parametros=[
        Parametro("lam", _P0["lam"], 0.0, 1.0, 0.05, "Hogares mano a boca λ", grupo="la ruptura",
                  definicion="sin acceso al crédito: los únicos que gastan la rebaja"),
        Parametro("dT", _P0["dT"], 2, 25, 1, "Rebaja de impuestos dT", grupo="experimento"),
        Parametro("mpc", _P0["mpc"], 0.3, 1.0, 0.05, "Propensión a consumir de los mab", grupo="conducta"),
        Parametro("r", _P0["r"], 1, 10, 0.5, "Tasa de interés r (%)", grupo="mercado",
                  definicion="irrelevante para el VP — esa es la gracia"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si la deuda de hoy son los impuestos de mañana, ¿una rebaja financiada con bonos estimula algo?",
        variables=[("dT", "la rebaja — ¿regalo o préstamo forzoso del fisco?"),
                   ("λ", "los hogares restringidos — donde la equivalencia se rompe"),
                   ("ΔS_nacional", "el veredicto — cero si todos son ricardianos")],
        derivacion=["bonos\\;hoy: +dT \\;\\;\\to\\;\\; impuestos\\;mañana: dT(1+r)",
                    "VP = \\frac{dT(1+r)}{1+r} = dT",
                    "\\Delta C = \\lambda\\,mpc\\,dT \\;\\;(solo\\;los\\;restringidos)"],
        contexto=("Barro (1974) hizo la pregunta con precisión de ajedrecista: si "
                  "el gobierno me baja impuestos hoy y emite bonos, y esos bonos "
                  "son los impuestos de mañana traídos a valor presente EXACTO, "
                  "¿en qué cambió mi riqueza? En nada — respondió — y por tanto "
                  "ahorro la rebaja para pagar el repago: la política de "
                  "transferencias es un pase de manos contable. La provocación "
                  "completó la crítica de m42 (lo anticipado no funciona) en el "
                  "terreno fiscal, y obligó a la profesión a precisar POR QUÉ los "
                  "multiplicadores existen: hogares restringidos de crédito, "
                  "miopía, horizontes finitos (Blanchard OLG, mención) — el λ de "
                  "este modelo."),
        autores=("Barro (1974, mención); el escepticismo original: Ricardo "
                 "(mención — quien dudaba de su propia equivalencia); la ruptura "
                 "por horizontes: Blanchard (1985, OLG — mención)."),
        supuestos=[
            "Los ricardianos ven el VP completo del repago (previsión + horizonte infinito o herencias operativas).",
            "Impuestos de suma fija: con impuestos distorsivos la equivalencia se rompe por otra vía (mención).",
            "λ exógeno: en crisis el crédito se corta y λ SUBE — la equivalencia es más débil justo cuando el fisco actúa (m70).",
        ],
        ecuaciones=[
            Ecuacion("VP = dT\\,\\frac{1+r}{1+r} = dT", "la deuda como impuestos diferidos",
                     "el corazón del argumento: r aparece y se cancela — a CUALQUIER tasa, el "
                     "bono es exactamente el impuesto futuro (verificado)."),
            Ecuacion("\\Delta C = \\lambda\\,mpc\\,dT", "la ruptura medible",
                     "solo gasta quien no puede intertemporalizar: el multiplicador de "
                     "transferencias es un CENSO de restricciones de crédito."),
        ],
        intuicion=("La equivalencia convierte el debate fiscal en una pregunta "
                   "empírica sobre λ: ¿cuántos hogares viven al día? De ahí dos "
                   "corolarios prácticos: las transferencias FOCALIZADAS en "
                   "restringidos (λ≈1 por diseño) rinden más demanda por sol que "
                   "las rebajas generales; y el gemelo de m44 (ΔCC=−ΔG) se "
                   "debilita en países ricardianos, porque Sp sube a compensar. El "
                   "gasto DIRECTO en bienes, ojo, escapa parcialmente: alguien "
                   "compra el cemento aunque el hogar ahorre (m60)."),
        equilibrio=("Contabilidad de un shock: con λ=0 el equilibrio real es "
                    "INVARIANTE (verificado: ΔS_nacional=0); con λ>0, el efecto "
                    "demanda es exactamente λ·mpc·dT — lineal, auditable."),
        limitaciones=[
            "Horizontes finitos sin herencias operativas rompen el VP (OLG): los que reciben la rebaja no son los que pagan el repago.",
            "Impuestos distorsivos y timing: suavizar tasas impositivas SÍ importa (tax smoothing de Barro, mención).",
            "λ no es constante: procíclico al crédito — la equivalencia se evapora en las crisis, cuando más se usa la política.",
        ],
        evolucion=("Es el contrapeso teórico del nivel: m68 y m69 discuten CUÁNDO "
                   "usar la política fiscal, y este modelo recuerda que su potencia "
                   "depende de QUIÉN la recibe (λ). El juicio final es empírico y "
                   "condicional: m70."),
    ),
    escenarios=[
        Escenario("mundo_ricardiano", "todos con acceso al crédito: λ = 0",
                  {"lam": 0.0},
                  "ΔC = 0 y ahorro nacional intacto: la rebaja fue un préstamo "
                  "forzoso que los hogares devolvieron al banco de inmediato — "
                  "Barro en estado puro.",
                  cadena=["rebaja con bonos", "VP del repago = dT (visto por todos)",
                          "se ahorra la rebaja completa", "ΔC = 0",
                          "el ahorro privado compensa al público: nada real cambió"]),
        Escenario("hogares_al_dia", "país con λ = 0.6 (crédito escaso)",
                  {"lam": 0.6},
                  "ΔC = 4.8 de cada 10: en economías con poca profundidad "
                  "financiera la política fiscal recupera potencia — el λ alto es "
                  "el caso de buena parte de América Latina (mención).",
                  cadena=["λ alto", "muchos hogares gastan lo que llega",
                          "ΔC = λ·mpc·dT", "el multiplicador de transferencias existe",
                          "focalizar en restringidos lo maximiza"]),
        Escenario("rebaja_grande", "dT = 20 con λ = 0.3",
                  {"dT": 20.0},
                  "el efecto escala lineal: 4.8 de 20 se gastan, 15.2 se guardan "
                  "para el repago — el tamaño no cambia la proporción ricardiana.",
                  cadena=["↑dT", "misma estructura de hogares",
                          "ΔC escala con dT", "la fuga ricardiana también"]),
    ],
    verificaciones=[
        Verificacion("λ=0: compensación total exacta (Barro)", _v_mundo_ricardiano),
        Verificacion("VP del repago = dT a cualquier tasa", _v_vp_impuestos),
        Verificacion("la ruptura es lineal en λ", _v_ruptura_lineal),
        Verificacion("ΔS_nacional = −ΔC (solo cuesta lo gastado)", _v_fuga_nacional),
    ],
    notas="La deuda como impuestos diferidos: el multiplicador de transferencias es un censo de restricciones de crédito.",
)
