# m70_multiplicadores.py — multiplicadores fiscales: el juicio empírico
# (nivel 9, cierre).
#
# La síntesis del arco m04→m60→m69: el multiplicador es un objeto
# CONDICIONAL al estado. Predictor didáctico con factores multiplicativos
# (calibrados a los RANGOS de la literatura — decisión de diseño declarada):
#   mult = base × (1+0.8·zlb) × (1−0.4·apertura) × (1−0.4·bc_activo·(1−zlb))
#               × (1−0.3·deuda_alta)
# Lecturas de la evidencia (menciones): Ramey (2019): rangos 0.6-1 en tiempos
# normales; Blanchard-Leigh (2013): >1 en consolidaciones post-2008;
# Ilzetzki-Mendoza-Végh (2013): menores en economías abiertas y endeudadas;
# Auerbach-Gorodnichenko (2012): mayores en recesión. El caso "Perú normal"
# (abierto, BCRP activo, deuda baja) cae en 0.4-0.6 — m107 lo estimará.
#
# Procedencia: factores didácticos = decisión de diseño calibrada a rangos
# de literatura empírica (menciones arriba); NO son estimaciones.

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
import config


def _mult(p, **cambios):
    q = dict(p, **cambios)
    return (q["base"] * (1 + 0.8 * q["zlb"]) * (1 - 0.4 * q["apertura"])
            * (1 - 0.4 * q["bc_activo"] * (1 - q["zlb"])) * (1 - 0.3 * q["deuda_alta"]))


def _curvas(p):
    casos = [("tu\nconfiguración", _mult(p), config.DORADO),
             ("Perú\nnormal", _mult(p, zlb=0.0, apertura=0.6, bc_activo=1.0, deuda_alta=0.0), config.AZUL2),
             ("ZLB 2009\n(cerrada)", _mult(p, zlb=1.0, apertura=0.2, bc_activo=1.0, deuda_alta=0.0), config.ROJO),
             ("consolidación\ndeuda alta", _mult(p, zlb=0.0, apertura=0.4, bc_activo=1.0, deuda_alta=1.0), config.GRIS),
             ("libro de texto\n(m04, cerrada)", 2.5, config.VERDE)]
    cats = [c[0] for c in casos]
    vals = [c[1] for c in casos]
    cols = [c[2] for c in casos]
    return {"barras": (cats, vals, cols),
            "anotacion": ("el multiplicador es CONDICIONAL al estado:\n"
                          "ZLB lo infla (la regla duerme, m12+m56);\n"
                          "apertura (m49), BC activo (m56) y deuda (m65) lo comen")}


def _resultados(p):
    return {"multiplicador de tu configuración": _mult(p),
            "factor ZLB (1+0.8·zlb)": 1 + 0.8 * p["zlb"],
            "factor apertura (1−0.4·ap)": 1 - 0.4 * p["apertura"],
            "factor BC activo": 1 - 0.4 * p["bc_activo"] * (1 - p["zlb"]),
            "factor deuda alta": 1 - 0.3 * p["deuda_alta"]}


def _ecuaciones_calibradas(p):
    return [f"$mult = {p['base']:.1f} \\times {1 + 0.8 * p['zlb']:.2f} \\times "
            f"{1 - 0.4 * p['apertura']:.2f} \\times "
            f"{1 - 0.4 * p['bc_activo'] * (1 - p['zlb']):.2f} \\times "
            f"{1 - 0.3 * p['deuda_alta']:.2f} = {_mult(p):.2f}$"]


_P0 = {"base": 1.0, "zlb": 0.0, "apertura": 0.6, "bc_activo": 1.0, "deuda_alta": 0.0}


def _v_zlb_apaga_al_bc():
    m_con = _mult(_P0, zlb=1.0, bc_activo=1.0)
    m_sin = _mult(_P0, zlb=1.0, bc_activo=0.0)
    return abs(m_con - m_sin) < 1e-12, \
        ("en el ZLB, que el BC sea 'activo' no cambia nada (la regla pide tasas que el "
         "piso no deja bajar, m12): el freno de m56 se apaga — por eso el ZLB infla multiplicadores")


def _v_apertura_come():
    m_cerrada = _mult(_P0, apertura=0.0)
    m_abierta = _mult(_P0, apertura=0.8)
    return m_abierta < m_cerrada, \
        (f"la apertura come multiplicador ({m_cerrada:.2f}→{m_abierta:.2f}): las "
         "importaciones (m49) fugan el impulso — Ilzetzki et al. (mención)")


def _v_peru_vs_zlb():
    peru = _mult(_P0, zlb=0.0, apertura=0.6, bc_activo=1.0, deuda_alta=0.0)
    zlb = _mult(_P0, zlb=1.0, apertura=0.2, bc_activo=1.0, deuda_alta=0.0)
    return peru < 1.0 < zlb, \
        (f"'Perú normal' da {peru:.2f} (<1: abierto y con BCRP activo) y 'ZLB cerrada' "
         f"da {zlb:.2f} (>1): los DOS resultados centrales de la literatura, en un predictor")


def _v_rango_acotado():
    esquinas = [_mult(_P0, zlb=z, apertura=a, bc_activo=b, deuda_alta=d)
                for z in (0.0, 1.0) for a in (0.0, 1.0)
                for b in (0.0, 1.0) for d in (0.0, 1.0)]
    return 0.2 <= min(esquinas) and max(esquinas) <= 2.0, \
        (f"todas las configuraciones caen en [{min(esquinas):.2f}, {max(esquinas):.2f}] ⊂ "
         "[0.2, 2.0]: el rango que la evidencia acota (Ramey, mención)")


MODELO = Modelo(
    id="m70", nivel=9,
    nombre="Multiplicadores fiscales (el juicio empírico)",
    xlabel="", ylabel="Multiplicador dY/dG",
    parametros=[
        Parametro("zlb", _P0["zlb"], 0, 1, 1, "¿Tasa en el piso? (ZLB)", grupo="estado",
                  definicion="la regla duerme: el freno de m56 se apaga"),
        Parametro("apertura", _P0["apertura"], 0.0, 1.0, 0.1, "Apertura comercial", grupo="estructura",
                  definicion="cuánto impulso se fuga en importaciones (m49)"),
        Parametro("bc_activo", _P0["bc_activo"], 0, 1, 1, "¿Banco central respondiendo?", grupo="estado",
                  definicion="Taylor despierto (m56) come multiplicador"),
        Parametro("deuda_alta", _P0["deuda_alta"], 0, 1, 1, "¿Deuda alta? (>90%)", grupo="estructura",
                  definicion="ricardianos nerviosos + prima (m65, m67)"),
        Parametro("base", _P0["base"], 0.5, 1.5, 0.1, "Multiplicador base", grupo="calibración"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Después de nueve niveles de teoría: ¿cuánto vale de verdad un sol de gasto — y de qué depende la respuesta?",
        variables=[("mult", "el objeto condicional — no un número, una función del estado"),
                   ("zlb, bc_activo", "el régimen monetario — el determinante #1 (m56/m12)"),
                   ("apertura, deuda", "las fugas estructurales — m49 y m65/m67")],
        derivacion=["mult = base \\times f_{zlb} \\times f_{apertura} \\times f_{BC} \\times f_{deuda}",
                    "f_{BC} = 1 - 0.4\\,bc\\,(1-zlb): \\;el\\;ZLB\\;apaga\\;al\\;BC",
                    "factores: decisión de diseño calibrada a RANGOS de la literatura (menciones)"],
        contexto=("El arco fiscal del currículo termina donde empezó el keynesiano "
                  "(m04), pero con matices de tres décadas de evidencia: Ramey "
                  "(2019, survey) acota los multiplicadores 'normales' en 0.6-1; "
                  "Blanchard-Leigh (2013) mostró que las consolidaciones post-2008 "
                  "operaron con multiplicadores >1 (el error de m69); Ilzetzki, "
                  "Mendoza y Végh (2013) encontraron multiplicadores menores en "
                  "economías abiertas, flexibles y endeudadas; Auerbach y "
                  "Gorodnichenko (2012), mayores en recesión. Este predictor NO "
                  "estima nada: ordena esos hallazgos en factores declarados, para "
                  "que el usuario razone como razona la literatura — "
                  "condicionalmente."),
        autores=("Ramey (2019); Blanchard y Leigh (2013); Ilzetzki, Mendoza y "
                 "Végh (2013); Auerbach y Gorodnichenko (2012) — menciones. Los "
                 "factores numéricos son decisión de diseño didáctica, NO "
                 "estimaciones."),
        supuestos=[
            "Factores multiplicativos e independientes: la realidad los mezcla con interacciones (la literatura los estima condicionales de a uno o dos).",
            "Los tamaños (0.8, 0.4, 0.3) son calibración didáctica a los RANGOS citados — auditables y discutibles por diseño.",
            "Multiplicador de gasto en bienes: transferencias e impuestos tienen los suyos (m67: el censo de λ).",
        ],
        ecuaciones=[
            Ecuacion("f_{BC} = 1 - 0.4\\,bc\\,(1 - zlb)", "la interacción clave",
                     "el hallazgo central post-2008: en el ZLB la regla no puede frenar (m12+m56) "
                     "y el multiplicador se libera — verificado: con zlb=1, el BC 'activo' es irrelevante."),
            Ecuacion("mult^{Per\\acute{u}} \\approx 0.4-0.6 < 1 < mult^{ZLB} \\approx 1.7",
                     "los dos mundos",
                     "abierto + BCRP despierto + deuda baja contra cerrado + tasa en el piso: los "
                     "polos de la evidencia, reproducidos por los factores."),
        ],
        intuicion=("El viaje completo del multiplicador: 2.5 en la pizarra de m04, "
                   "0.71 con la tasa endógena (m10), 0 o 1.8 según el cambio "
                   "(m49), <1 con Taylor despierto (m56), y la evidencia "
                   "confirmando la lógica: el multiplicador es GRANDE exactamente "
                   "cuando los frenos duermen (ZLB, recesión, economía cerrada) y "
                   "CHICO cuando alguien más maneja (BC activo, apertura, "
                   "ricardianos). Para el Perú fiscal la lectura operativa es "
                   "humilde: en tiempos normales, cada sol rinde ~medio sol de "
                   "demanda — el resto lo deciden el BCRP y la aduana."),
        equilibrio=("No hay equilibrio: es un predictor condicional. Sus "
                    "verificaciones son de COHERENCIA con la literatura que lo "
                    "calibra: interacción ZLB-BC, apertura que come, los dos polos "
                    "y el rango acotado."),
        limitaciones=[
            "NO es una estimación: es la literatura ordenada en factores — el multiplicador peruano real exige los datos del MEF (m107).",
            "Sin dinámica: los multiplicadores acumulados (2-3 años) difieren de los de impacto (Ramey, mención).",
            "La identificación empírica es EL problema (shocks fiscales exógenos son raros: militares, revisiones narrativas — menciones): heredado por cualquier lectura.",
        ],
        evolucion=("Cierra el nivel 9 devolviendo la pregunta al terreno donde "
                   "nació (m04) con la respuesta madura: depende, y sabemos DE QUÉ "
                   "depende. El nivel 10 examina qué pasa cuando todo esto falla a "
                   "la vez (crisis); m107 estimará el multiplicador peruano con "
                   "inversión pública del MEF."),
    ),
    escenarios=[
        Escenario("peru_normal", "abierto (0.6), BCRP activo, deuda baja",
                  {"zlb": 0.0, "apertura": 0.6, "bc_activo": 1.0, "deuda_alta": 0.0},
                  "mult ≈ 0.46: cada sol de gasto rinde medio sol de demanda — la "
                  "aritmética de una economía abierta con banco central despierto.",
                  cadena=["impulso fiscal", "el BCRP responde (m56)", "parte se importa (m49)",
                          "mult < 1", "la política fiscal no actúa sola"]),
        Escenario("gran_recesion_zlb", "2009: tasa en el piso, economía semicerrada",
                  {"zlb": 1.0, "apertura": 0.2, "bc_activo": 1.0, "deuda_alta": 0.0},
                  "mult ≈ 1.66: con la regla dormida y poca fuga externa, el "
                  "multiplicador se libera — el caso que rehabilitó la política "
                  "fiscal tras 2008.",
                  cadena=["ZLB: la tasa no puede frenar (m12)", "el factor BC se apaga",
                          "poca fuga importadora", "mult > 1.5",
                          "el momento keynesiano de m04, redivivo"]),
        Escenario("consolidacion_endeudada", "ajustar con deuda alta y BC activo",
                  {"zlb": 0.0, "apertura": 0.4, "bc_activo": 1.0, "deuda_alta": 1.0},
                  "mult ≈ 0.35: los ricardianos nerviosos (m67) y la prima (m65) "
                  "achican el multiplicador — el único consuelo de la austeridad "
                  "de m69 es que aquí duele menos.",
                  cadena=["deuda alta", "hogares anticipan impuestos (m67)",
                          "el BC además responde", "mult chico",
                          "ajustar aquí contrae menos… y rinde menos"]),
    ],
    verificaciones=[
        Verificacion("el ZLB apaga al banco central (interacción clave)", _v_zlb_apaga_al_bc),
        Verificacion("la apertura come multiplicador (Ilzetzki et al.)", _v_apertura_come),
        Verificacion("los dos polos: Perú<1<ZLB", _v_peru_vs_zlb),
        Verificacion("rango acotado a la evidencia [0.2, 2.0]", _v_rango_acotado),
    ],
    notas="El cierre del arco m04→m70: 'depende' — y después de nueve niveles, sabemos exactamente de qué.",
)
