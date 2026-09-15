"""simuladores/macro/modelos/nivel_12/m107_gasto_multiplicador.py — gasto público y el multiplicador fiscal (nivel 12).

El multiplicador fiscal (m37: ¿cuánto PBI genera un sol de gasto público?) con
datos peruanos, y la lección de por qué es tan difícil de medir. El gasto no
financiero del gobierno general pasó de 17% del PBI (2006) a 24% en 2020 (el
estímulo COVID) y ~21% después. Si uno REGRESA ingenuamente el crecimiento del
PBI sobre el crecimiento del gasto, obtiene un "multiplicador" de ~0.1 —
absurdamente bajo. No es el multiplicador: está sesgado por la endogeneidad de
m106 (el gasto es contracíclico, sube cuando el PBI cae: en 2020 el gasto real
creció +10% mientras el PBI caía −11%). El multiplicador IDENTIFICADO para el
Perú, en la literatura que usa variación exógena del gasto (m70), es ~0.5-1:
positivo pero modesto, porque una economía pequeña y abierta FILTRA vía
importaciones (m43); y es CONDICIONAL (m70): mayor en recesión/ZLB (m91) que en
auge. No hay un número único.

Procedencia: datos BCRP PN02207FM (gasto no financiero del gobierno general,
mensual→anual) y PM04946AA (PBI nominal); crecimiento real deflactando por el
deflactor implícito (PBI nominal/PBI real 2007). El concepto de multiplicador:
m37; su medición y condicionalidad: m70 (conocimiento general). El rango
0.5-1 es de la literatura (m70), NO estimado aquí; el ~0.1 naive SÍ es del dato.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, gasto, pbin = _datos_bcrp.alinear("gasto_gg", "pbi_nominal")
    _, _, pbisoles = _datos_bcrp.alinear("gasto_gg", "pbi_soles")
    gasto_real = gasto / (pbin / pbisoles)              # deflactor implícito (base 2007)
    gg = np.diff(gasto_real) / gasto_real[:-1] * 100     # crecimiento real del gasto
    share = gasto / pbin * 100                           # gasto como % del PBI
    ax = anos[1:].astype(int)
    gmap = dict(zip(*[[int(a) for a in _datos_bcrp.serie("pbi_var", anual=True)[0]],
                      list(_datos_bcrp.serie("pbi_var", anual=True)[1])]))
    gpbi = np.array([gmap[a] for a in ax])
    return anos, share, ax, gg, gpbi


def _naive(gg, gpbi):
    _, b, _ = _datos_bcrp.ols(gg, gpbi)
    return b


def _curvas(p):
    anos, share, ax, gg, gpbi = _series()
    b = _naive(gg, gpbi)
    k = p["multiplicador"]
    return {"lineas": {"gasto público (% del PBI)": (anos, share, config.VERDE),
                       "crecimiento del PBI (%)": (ax.astype(float), gpbi, config.AZUL2)},
            "puntos": [(2020.0, float(share[list(anos).index(2020)]),
                        "2020: gasto 24% del PBI (estímulo COVID)")],
            "anotacion": (f"gasto (PN02207FM) vs PBI (PN01728AM)\n"
                          f"multiplicador NAIVE (regresión) = {b:.2f} — sesgado (m106)\n"
                          f"identificado (m70): ~0.5-1; supuesto k = {k:.1f}")}


def _resultados(p):
    anos, share, ax, gg, gpbi = _series()
    b = _naive(gg, gpbi)
    k = p["multiplicador"]
    i20 = list(ax).index(2020)
    # impulso fiscal directo 2020 ≈ (share/100) × crec real del gasto; efecto total ≈ k × impulso
    impulso20 = share[list(anos).index(2020)] / 100 * gg[i20]
    return {"multiplicador naive (regresión, sesgado)": float(b),
            "gasto público 2006 (% PBI)": float(share[0]),
            "gasto público máximo (% PBI)": float(share.max()),
            "gasto público 2020 COVID (% PBI)": float(share[list(anos).index(2020)]),
            "multiplicador supuesto k": float(k),
            "impulso fiscal directo 2020 (pp de demanda)": float(impulso20),
            "efecto total 2020 bajo k (pp)": float(k * impulso20)}


def _ecuaciones_calibradas(p):
    anos, share, ax, gg, gpbi = _series()
    b = _naive(gg, gpbi)
    return [f"multiplicador naive $= {b:.2f}$ (sesgado por endogeneidad, m106) $\\neq$ verdadero",
            f"identificado (m70): $k \\approx 0.5\\text{{-}}1$; abierto $\\Rightarrow$ filtra por importaciones (m43)"]


_P0 = {"multiplicador": 0.7}


def _v_estado_crecio():
    anos, share, ax, gg, gpbi = _series()
    s20 = float(share[list(anos).index(2020)])
    return share[0] < 18 and s20 > 23, \
        (f"el gasto público pasó de {share[0]:.0f}% del PBI (2006) a {s20:.0f}% en 2020 (estímulo COVID): "
         "el Estado creció y respondió fuerte a la crisis — el impulso fiscal más grande de la muestra")


def _v_naive_sesgado():
    anos, share, ax, gg, gpbi = _series()
    b = _naive(gg, gpbi)
    return b < 0.35, \
        (f"el multiplicador NAIVE (regresión cruda) es {b:.2f}, absurdamente bajo: está sesgado por la "
         "endogeneidad (el gasto es contracíclico, m106; en 2020 subió mientras el PBI caía) — NO es el multiplicador")


def _v_identificado_modesto():
    return True, \
        ("el multiplicador IDENTIFICADO del Perú (literatura con variación exógena, m70) es ~0.5-1: positivo "
         "pero modesto, porque una economía pequeña y abierta FILTRA el estímulo vía importaciones (m43) — no es ni 0.1 ni 2")


def _v_condicional():
    return True, \
        ("el multiplicador es CONDICIONAL (m70), no un número fijo: mayor en recesión/ZLB (m91) que en auge, "
         "mayor para inversión que para transferencias — por eso el estímulo COVID (2020) y el rebote de 2021 (m81) tienen más efecto que el gasto en un boom")


MODELO = Modelo(
    id="m107", nivel=12,
    nombre="Gasto público → multiplicador fiscal (BCRP)",
    xlabel="Año", ylabel="Porcentaje (%)",
    parametros=[
        Parametro("multiplicador", _P0["multiplicador"], 0.0, 2.0, 0.1, "Multiplicador fiscal supuesto (k)",
                  grupo="análisis", definicion="¿cuánto PBI por sol de gasto? naive~0.1, identificado~0.5-1 (m70), ZLB>1 (m91)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Cuánto PBI genera un sol de gasto público en el Perú — y por qué la respuesta ingenua (0.1) es tan errada?",
        variables=[("G_t", "gasto no financiero del gobierno general, % del PBI (BCRP PN02207FM)"),
                   ("k", "multiplicador fiscal: PBI generado por sol de gasto (m37)"),
                   ("naive vs identificado", "0.1 (sesgado) vs 0.5-1 (m70)")],
        derivacion=["dato: \\;G_t \\;(PN02207FM, \\%\\;PBI), \\;g_t \\;(PN01728AM)",
                    "naive: \\;regresar\\;g\\;sobre\\;\\Delta G \\Rightarrow k \\approx 0.1 \\;(sesgado, m106)",
                    "identificado\\;(m70): \\;k \\approx 0.5\\text{-}1 \\;(abierto\\Rightarrow filtra, m43)",
                    "CONDICIONAL: \\;k_{recesión/ZLB} > k_{auge} \\;(m70, m91)"],
        contexto=("El multiplicador fiscal —cuánto producto genera cada sol de "
                  "gasto público (m37)— es una de las cifras más disputadas y más "
                  "difíciles de medir de la macroeconomía, y este modelo muestra por "
                  "qué, con datos peruanos. Los hechos: el gasto no financiero del "
                  "gobierno general del Perú creció de 17% del PBI en 2006 a un pico "
                  "de 24% en 2020 —el mayor impulso fiscal de la muestra, la "
                  "respuesta al COVID— y se estabilizó cerca de 21%. La tentación es "
                  "medir el multiplicador directamente: regresar el crecimiento del "
                  "PBI sobre el crecimiento del gasto. Al hacerlo se obtiene un "
                  "número ridículo: alrededor de 0.1, como si un sol de gasto "
                  "generara diez céntimos de producto. Ese número es falso, y saber "
                  "por qué es la lección. Está sesgado a la baja por la misma "
                  "endogeneidad de m106: el gasto público es contracíclico, sube "
                  "cuando la economía cae. El caso extremo es 2020, cuando el gasto "
                  "real creció más de 10% mientras el PBI se desplomaba 11% —el "
                  "estímulo respondía a la caída, no la causaba—; esa coincidencia "
                  "de gasto alto con crecimiento bajo arrastra la correlación hacia "
                  "cero. Para medir el multiplicador DE VERDAD hay que encontrar "
                  "cambios del gasto que no respondan al ciclo (reglas, "
                  "shocks, el método narrativo o un SVAR, m70), y la literatura que "
                  "lo hace encuentra, para economías como la peruana, un "
                  "multiplicador de aproximadamente 0.5 a 1: positivo pero modesto. "
                  "¿Por qué modesto? Porque el Perú es una economía pequeña y "
                  "ABIERTA (m43): buena parte del estímulo se filtra hacia "
                  "importaciones en vez de quedarse activando la demanda interna. Y "
                  "—clave— el multiplicador es CONDICIONAL (m70): es mayor en "
                  "recesión y en la trampa de liquidez (cuando el banco central no "
                  "puede compensar, m91) que en un auge; mayor para inversión "
                  "pública (que además construye capacidad, m26) que para "
                  "transferencias. No existe 'el' multiplicador: existe un rango que "
                  "depende del estado de la economía. Por eso el estímulo del COVID "
                  "(2020) y el rebote de 2021 tuvieron más tracción que la que "
                  "tendría el mismo gasto en pleno superciclo."),
        autores=("Datos: BCRP (PN02207FM gasto no financiero, PM04946AA PBI "
                 "nominal, PN01728AM PBI var%); el multiplicador: m37; su medición "
                 "(identificación) y condicionalidad: m70; el ZLB: m91; la filtración "
                 "en economía abierta: m43 (conocimiento general). El rango 0.5-1 es "
                 "de la literatura, no estimado aquí."),
        supuestos=[
            "El multiplicador naive (regresión de g sobre Δgasto) se muestra para REFUTARLO: está sesgado por endogeneidad (m106), no es una estimación válida.",
            "El rango identificado 0.5-1 se cita de la literatura (m70) como conocimiento general — NO se estima en este modelo (exigiría variación exógena del gasto y un diseño de identificación).",
            "El impulso fiscal y el efecto bajo k son ILUSTRATIVOS (share × crecimiento real del gasto, × k): dan orden de magnitud, no una contabilidad estructural del multiplicador.",
        ],
        ecuaciones=[
            Ecuacion("k_{naive} = \\partial g / \\partial(\\Delta G) \\approx 0.1 \\;(sesgado)", "el número falso",
                     "la regresión cruda da ~0.1 porque el gasto es contracíclico (m106): sube cuando el PBI "
                     "cae, arrastrando la correlación a cero — NO es el multiplicador."),
            Ecuacion("k_{identificado} \\approx 0.5\\text{-}1 \\;(m70, economía\\;abierta)", "el rango creíble",
                     "la literatura con variación exógena encuentra ~0.5-1 para economías pequeñas y abiertas: "
                     "positivo pero modesto, porque el estímulo se filtra vía importaciones (m43)."),
            Ecuacion("k_{recesión/ZLB} > k_{auge} \\;(m70, m91)", "el multiplicador es condicional",
                     "no hay un número único: el multiplicador es mayor cuando hay capacidad ociosa y el "
                     "banco central no compensa (m91) — por eso el estímulo COVID rindió más que en un boom."),
        ],
        intuicion=("Este modelo es una advertencia y una calibración a la vez. La "
                   "advertencia: si alguien te dice 'los datos muestran que el gasto "
                   "público no sirve, mira la correlación', ya sabes que está "
                   "midiendo mal —la contraciclicidad (m106) garantiza que la "
                   "correlación cruda salga cerca de cero o negativa, sin que eso "
                   "diga nada sobre el efecto real. La calibración: el multiplicador "
                   "peruano creíble no es ni el 0.1 del naive ni el 2 de los "
                   "entusiastas, sino algo entre 0.5 y 1, y condicional al estado de "
                   "la economía. Esa modestia tiene una raíz estructural clara —la "
                   "apertura (m43): cuando el Estado peruano gasta, una fracción "
                   "importante se va en importaciones y no activa la demanda local—, "
                   "y una implicación de política: el gasto rinde más cuando más se "
                   "necesita (recesión, ZLB, m91) y cuando es inversión que además "
                   "construye capacidad (m26), y menos cuando la economía ya está en "
                   "auge. El estímulo del COVID ilustra las dos caras: fue enorme y "
                   "necesario (el multiplicador era alto en plena recesión), pero el "
                   "shock era tan grande que el PBI cayó igual —y luego rebotó con "
                   "fuerza. El desliz de este ejercicio (slider k) deja al lector "
                   "poner el multiplicador que crea y ver el efecto: la enseñanza es "
                   "que el número correcto depende, y que la correlación cruda no lo "
                   "da."),
        equilibrio=("No hay equilibrio que resolver: es el contraste entre un "
                    "multiplicador naive mal medido (~0.1, sesgado por m106) y el "
                    "rango identificado de la literatura (~0.5-1, m70), condicional "
                    "al estado (mayor en recesión/ZLB, m91). El slider k deja "
                    "explorar el supuesto."),
        limitaciones=[
            "No se ESTIMA el multiplicador: se refuta el naive (sesgado) y se cita el rango identificado (m70) — estimarlo exige un diseño de identificación (SVAR, narrativo, reglas) fuera de este modelo ilustrativo.",
            "Muestra corta y anual (gasto desde 2006): los multiplicadores se estudian mejor a mayor frecuencia y con más historia; aquí se ilustra el concepto, no se produce una cifra oficial.",
            "El multiplicador agregado esconde heterogeneidad: inversión vs transferencias vs remuneraciones tienen multiplicadores muy distintos (m91), que este nivel agregado no separa.",
        ],
        evolucion=("Cierra el corazón del bloque fiscal: m106 mostró la endogeneidad "
                   "con la inversión pública, m107 la lleva al multiplicador y su "
                   "rango condicional (m70), y m108 pasa a la deuda que financia "
                   "este gasto y su sostenibilidad (m64). Junto con m91 (gasto "
                   "productivo y ZLB) y m70 (juicio empírico), completa la política "
                   "fiscal del laboratorio, ahora con datos peruanos."),
    ),
    escenarios=[
        Escenario("naive_enganoso", "el multiplicador naive (k≈0.1)",
                  {"multiplicador": 0.1},
                  "el número que sale de regresar crudamente: ~0.1, absurdamente "
                  "bajo. No mide el efecto del gasto — mide la contraciclicidad "
                  "(m106). El error de leer causalidad de una correlación.",
                  cadena=["regresar PBI sobre gasto (crudo)", "sale k≈0.1 (absurdo)",
                          "es endogeneidad: el gasto sube cuando el PBI cae (m106)", "NO es el multiplicador — es sesgo"]),
        Escenario("identificado_normal", "el rango identificado en tiempos normales (k≈0.7)",
                  {"multiplicador": 0.7},
                  "lo que encuentra la literatura seria (m70) para una economía "
                  "abierta como la peruana: ~0.5-1. Positivo pero modesto — parte "
                  "del estímulo se filtra por importaciones (m43).",
                  cadena=["usar variación exógena del gasto (m70)", "k≈0.5-1 en economía abierta",
                          "el estímulo se filtra vía importaciones (m43)", "positivo pero modesto — la cifra creíble"]),
        Escenario("recesion_zlb", "el multiplicador en recesión/ZLB (k>1)",
                  {"multiplicador": 1.4},
                  "cuando hay capacidad ociosa y el banco central no puede compensar "
                  "(ZLB, m91), el multiplicador sube por encima de 1: el gasto rinde "
                  "más justo cuando más se necesita (2020). Condicional (m70).",
                  cadena=["recesión profunda + ZLB (2020, m91)", "capacidad ociosa, el BC no compensa",
                          "el multiplicador sube por encima de 1 (m70)", "el estímulo rinde más cuando más se necesita"]),
    ],
    verificaciones=[
        Verificacion("el gasto público creció y saltó en el COVID (24%)", _v_estado_crecio),
        Verificacion("el multiplicador naive (~0.1) está sesgado (m106)", _v_naive_sesgado),
        Verificacion("el identificado es modesto: ~0.5-1 (m70, m43)", _v_identificado_modesto),
        Verificacion("el multiplicador es condicional al estado (m70)", _v_condicional),
    ],
    notas="El multiplicador naive (~0.1) está sesgado por endogeneidad (m106); el identificado (m70) es ~0.5-1 (abierto→filtra, m43) y CONDICIONAL (mayor en ZLB/recesión, m91). No hay número único.",
)
