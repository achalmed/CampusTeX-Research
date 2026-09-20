"""simuladores/macro/modelos/nivel_12/m108_deuda_sostenibilidad.py — deuda pública y sostenibilidad (nivel 12).

La aritmética de la deuda (m64: Δb ≈ b·(r−g) − sp) aplicada a la trayectoria
REAL del Perú, con datos del BCRP. La deuda pública peruana cuenta una historia
ejemplar: cayó de 44.7% del PBI en 2004 a un MÍNIMO de 19.2% en 2013 —el Perú
usó el superciclo para pagar deuda (disciplina fiscal, el fondo de
estabilización m66/m69)— y luego subió a 34% en 2020 con el COVID (déficit +
caída del PBI, la dinámica de crisis de m64), estabilizándose cerca de 32%. Es
el CONTRAEJEMPLO de m96 (Grecia 175%, Argentina en default): el Perú ahorró en
la bonanza, así que tenía ESPACIO fiscal para responder a la pandemia sin
entrar en crisis. La sostenibilidad no es tener deuda cero, es que g supere a
r y ahorrar en los buenos años (m64).

Procedencia: datos BCRP PN03371FQ (saldo de deuda pública del SPNF, millones
S/, fin de año) y PM04946AA (PBI nominal, millones S/), muestra 2004-2023; la
razón deuda/PBI se calcula como deuda/PBI nominal (transparente). La aritmética
de la deuda: m64 (conocimiento general). Análisis descriptivo, no pronóstico.
"""

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _serie():
    anos, deuda, pbin = _datos_bcrp.alinear("deuda_publica_soles", "pbi_nominal")
    b = deuda / pbin * 100                            # deuda como % del PBI
    return anos, b


def _idx(anos, p):
    a = int(p["anio_foco"])
    return int(list(anos).index(a)) if a in anos else len(anos) - 1


def _curvas(p):
    anos, b = _serie()
    i = _idx(anos, p)
    imin = int(b.argmin())
    puntos = [(float(anos[imin]), float(b[imin]), f"mínimo {b[imin]:.0f}% ({int(anos[imin])})"),
              (2020.0, float(b[anos == 2020][0]), "2020: COVID (salto)")]
    if int(anos[i]) not in (int(anos[imin]), 2020):
        puntos.append((float(anos[i]), float(b[i]), f"{int(anos[i])}: {b[i]:.0f}% del PBI"))
    return {"lineas": {"deuda pública (% del PBI)": (anos, b, config.ROJO),
                       "umbral de prudencia (~40%)": (anos, np.full(len(anos), 40.0), config.GRIS)},
            "puntos": puntos,
            "anotacion": (f"deuda pública del Perú (PN03371FQ / PM04946AA)\n"
                          f"{b[0]:.0f}% (2004) → {b.min():.0f}% (2013, disciplina) → {b[-1]:.0f}% (2023)\n"
                          "ahorró en el boom → espacio para el COVID (m64, m66)")}


def _resultados(p):
    anos, b = _serie()
    i = _idx(anos, p)
    return {"deuda/PBI inicial 2004 (%)": float(b[0]),
            "deuda/PBI mínima (%)": float(b.min()),
            "año de la deuda mínima": float(anos[int(b.argmin())]),
            "deuda/PBI 2020 COVID (%)": float(b[anos == 2020][0]),
            "deuda/PBI final 2023 (%)": float(b[-1]),
            "caída en el boom 2004-2013 (pp)": float(b[0] - b[anos == 2013][0]),
            f"deuda/PBI {int(anos[i])} (%)": float(b[i])}


def _ecuaciones_calibradas(p):
    anos, b = _serie()
    return [f"$b$: ${b[0]:.0f}\\%\\to{b.min():.0f}\\%$ (2004-2013, disciplina) $\\to {b[-1]:.0f}\\%$ (2023)",
            f"$\\Delta b \\approx b\\,(r-g) - sp$: en el boom $g\\gg r$ y $sp>0 \\Rightarrow b\\downarrow$ (m64)"]


_P0 = {"anio_foco": 2013.0}


def _v_disciplina_boom():
    anos, b = _serie()
    b04 = float(b[0])
    b13 = float(b[anos == 2013][0])
    return b04 > 40 and b13 < 22 and b13 < b04, \
        (f"el Perú usó el superciclo para pagar deuda: {b04:.0f}% del PBI (2004) → {b13:.0f}% (2013): "
         "con g≫r y superávits primarios la deuda cae (m64) — la disciplina del fondo de estabilización (m66)")


def _v_covid_salto():
    anos, b = _serie()
    b19 = float(b[anos == 2019][0])
    b20 = float(b[anos == 2020][0])
    return b20 > b19 + 5, \
        (f"2020: la deuda saltó {b19:.0f}%→{b20:.0f}% del PBI con el COVID: déficit por el estímulo + caída del PBI "
         "(numerador arriba, denominador abajo) — la dinámica de crisis de m64, pero desde una base baja")


def _v_sostenible():
    anos, b = _serie()
    return b.max() < 45 and b[-1] < 40, \
        (f"la deuda peruana se mantuvo MODERADA (máx {b.max():.0f}%, {b[-1]:.0f}% en 2023): baja para la región — "
         "la sostenibilidad no es deuda cero, es el espacio que la disciplina compró (contraejemplo de m96)")


def _v_espacio_fiscal():
    anos, b = _serie()
    b13 = float(b[anos == 2013][0])
    b20 = float(b[anos == 2020][0])
    return b20 - b13 > 10 and b20 < 40, \
        (f"el ahorro del boom dio ESPACIO: desde el mínimo de {b13:.0f}% (2013) el Perú pudo subir a {b20:.0f}% (2020) "
         "para financiar la respuesta al COVID sin crisis — ahorrar en los buenos años ES la sostenibilidad (m64, m69)")


MODELO = Modelo(
    id="m108", nivel=12,
    nombre="Deuda pública → sostenibilidad (BCRP)",
    xlabel="Año", ylabel="Deuda pública (% del PBI)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2004, 2023, 1, "Año a destacar en la trayectoria",
                  grupo="análisis", definicion="año a inspeccionar; 2013 es el mínimo (fin de la fase de desendeudamiento)"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="¿Es sostenible la deuda pública del Perú — y qué hizo bien que Grecia y Argentina (m96) no?",
        variables=[("b_t", "deuda pública como % del PBI (PN03371FQ / PM04946AA)"),
                   ("2004→2013", "la fase de desendeudamiento: 45% → 19% (disciplina del boom)"),
                   ("2020", "el salto del COVID: 26% → 34% (déficit + caída del PBI)")],
        derivacion=["b_t = Deuda_t / PBI\\;nominal_t \\;(PN03371FQ / PM04946AA)",
                    "\\Delta b \\approx b\\,(r-g) - sp \\;(aritmética\\;de\\;la\\;deuda, m64)",
                    "boom: \\;g \\gg r \\;y\\; sp>0 \\Rightarrow b\\;cae\\;(44.7\\%\\to19.2\\%)",
                    "COVID: \\;déficit\\;+\\;PBI\\downarrow \\Rightarrow b\\;sube\\;(a\\;34\\%), \\;pero\\;base\\;baja"],
        contexto=("Este modelo aplica la aritmética de la deuda que el nivel 9 "
                  "construyó (m64: la deuda como porcentaje del PBI cambia según "
                  "Δb ≈ b·(r−g) − sp, donde r es la tasa de la deuda, g el "
                  "crecimiento y sp el superávit primario) a la trayectoria REAL "
                  "del Perú, y el resultado es una historia de manual sobre cómo se "
                  "hace bien. En 2004 la deuda pública peruana era 44.7% del PBI, un "
                  "nivel incómodo heredado de décadas de inestabilidad. Durante el "
                  "superciclo de commodities, el Perú hizo exactamente lo que la "
                  "teoría recomienda: con un crecimiento altísimo (g muy por encima "
                  "de la tasa r) y superávits primarios (ahorrando parte del "
                  "windfall del cobre, m105, en el fondo de estabilización fiscal, "
                  "m66), la deuda cayó año tras año hasta un mínimo de 19.2% del PBI "
                  "en 2013 — se redujo a menos de la mitad en menos de una década. "
                  "Esta fue una decisión deliberada y contracíclica (m69): pagar "
                  "deuda en los buenos años. Su recompensa llegó en 2020: cuando el "
                  "COVID golpeó, el Perú pudo desplegar uno de los mayores paquetes "
                  "de estímulo de la región y la deuda saltó a 34% del PBI (déficit "
                  "por el gasto extraordinario más la caída del PBI que encoge el "
                  "denominador, la dinámica de crisis de m64) — pero PARTIENDO de un "
                  "nivel tan bajo que el salto fue absorbible, sin pánico de los "
                  "mercados ni prima de riesgo disparada. La deuda se estabilizó "
                  "luego cerca de 32%, de las más bajas de América Latina. El "
                  "contraste con m96 es la lección: Grecia llegó a la crisis con 175% "
                  "y Argentina con default recurrente porque gastaron en los buenos "
                  "años; el Perú ahorró, y por eso su deuda es sostenible. La "
                  "sostenibilidad no es tener deuda cero —es que el crecimiento "
                  "supere a la tasa de interés y ahorrar en la bonanza para tener "
                  "espacio en la tormenta."),
        autores=("Datos: BCRP (PN03371FQ deuda pública del SPNF, PM04946AA PBI "
                 "nominal); la aritmética de la deuda: m64; el fondo de "
                 "estabilización y la política contracíclica: m66/m69; el "
                 "contraejemplo de crisis: m96 (conocimiento general)."),
        supuestos=[
            "b = deuda del SPNF / PBI nominal (fin de año): la razón estándar; la deuda es un saldo a fin de período y el PBI un flujo anual.",
            "La lectura por episodios (desendeudamiento del boom, salto COVID) es descriptiva; la descomposición exacta de Δb en (r−g) y sp exigiría la tasa efectiva de la deuda y el resultado primario, que aquí se citan cualitativamente (m64).",
            "'Sostenible' se usa en el sentido de m64 (la razón no explota y hay espacio de mercado), no como un umbral rígido; el umbral de ~40% del gráfico es una referencia de prudencia, no una ley.",
        ],
        ecuaciones=[
            Ecuacion("b_t = Deuda_t / PBI_t \\;(nominal)", "la razón deuda/PBI",
                     "el saldo de deuda del sector público no financiero sobre el PBI nominal: la "
                     "variable de sostenibilidad de m64, calculada con datos del BCRP."),
            Ecuacion("boom: \\;g \\gg r, \\; sp>0 \\;\\Rightarrow\\; b: 44.7\\%\\to19.2\\%", "el desendeudamiento",
                     "con crecimiento muy superior a la tasa y superávits primarios, la deuda cae sola "
                     "(la aritmética de m64 a favor) — el Perú lo aprovechó (disciplina, m66/m69)."),
            Ecuacion("COVID: \\;déficit + PBI\\downarrow \\;\\Rightarrow\\; b: 26\\%\\to34\\%", "el salto absorbible",
                     "la dinámica de crisis de m64 (numerador arriba, denominador abajo), pero desde una "
                     "base tan baja que fue sostenible — el espacio que compró la disciplina."),
        ],
        intuicion=("La imagen es una curva que baja fuerte y luego sube: la deuda "
                   "peruana cae de 45% a 19% en el boom y salta a 34% con el COVID. "
                   "Contada con la aritmética de m64, es la diferencia entre un país "
                   "que entiende el ciclo y uno que no. En los buenos años, cuando el "
                   "cobre llovía y la economía crecía 6-9%, el Perú no gastó todo el "
                   "windfall: pagó deuda. Eso parece aburrido —hasta que llega una "
                   "pandemia y resulta que tienes margen para gastar sin que los "
                   "mercados te castiguen. Grecia y Argentina (m96) hicieron lo "
                   "contrario —gastar en la bonanza— y llegaron a sus crisis sin "
                   "colchón. La moraleja de m64 hecha política peruana: la "
                   "sostenibilidad de la deuda se construye en los buenos tiempos, "
                   "no en los malos; cuando g supera a r, la deuda se paga casi "
                   "sola, y desperdiciar esa ventana es el error que se paga después. "
                   "El Perú, con todas sus limitaciones institucionales, hizo esta "
                   "parte bien —y su prima de riesgo, de las más bajas de la región, "
                   "es la prueba. La pregunta hacia adelante: ¿mantendrá la "
                   "disciplina ahora que la deuda subió y el crecimiento se moderó?"),
        equilibrio=("La razón deuda/PBI no explota: cayó a 19% en el boom y, tras el "
                    "salto del COVID a 34%, se estabilizó cerca de 32% — sostenible "
                    "en el sentido de m64 (g histórico > r, con espacio de mercado). "
                    "El 'equilibrio' es dinámico: depende de mantener g > r y "
                    "disciplina primaria."),
        limitaciones=[
            "Descomposición cualitativa: no se separa numéricamente Δb en el efecto (r−g) y el superávit primario (exigiría la tasa efectiva de la deuda y el resultado primario serie a serie, m64).",
            "Deuda bruta del SPNF: no neta de activos (el Perú tiene ahorros en el fondo de estabilización y reservas); la posición NETA es aún más sólida que la bruta mostrada.",
            "Muestra 2004-2023: no capta las crisis de deuda peruanas previas (los 80), que son el recordatorio de por qué la disciplina posterior importó tanto.",
        ],
        evolucion=("Aplica la aritmética de m64 y cierra el bloque fiscal (m106-m108) "
                   "mostrando al Perú como el CONTRAEJEMPLO virtuoso de m96 "
                   "(Grecia/Argentina): ahorrar en el boom (el windfall de m105) da "
                   "el espacio para el estímulo de m106/m107 en la crisis. Conecta "
                   "con m66 (fondo de estabilización) y m69 (contracíclico), y "
                   "prepara los shocks externos (m110-m111) que esa solidez fiscal "
                   "ayuda a resistir."),
    ),
    escenarios=[
        Escenario("minimo_2013", "el mínimo tras el desendeudamiento (2013)",
                  {"anio_foco": 2013.0},
                  "2013: la deuda toca 19% del PBI, su mínimo — el Perú aprovechó el "
                  "boom (g≫r) y los superávits para reducirla a menos de la mitad de "
                  "2004. La aritmética de m64 a favor, bien usada.",
                  cadena=["superciclo: crecimiento 6-9% (g≫r)", "superávits primarios (ahorro del windfall, m66)",
                          "la deuda cae año a año (Δb<0, m64)", "mínimo de 19% del PBI en 2013 — colchón construido"]),
        Escenario("covid_2020", "el salto del COVID (2020)",
                  {"anio_foco": 2020.0},
                  "2020: la deuda salta a 34% del PBI — estímulo masivo + caída del "
                  "PBI. Pero desde una base tan baja que fue absorbible sin crisis: "
                  "el colchón del boom en acción (m64, m69).",
                  cadena=["COVID: shock de volumen (PBI −10.9%)", "estímulo fiscal masivo (déficit) + PBI cae",
                          "la deuda salta 26%→34% (Δb>0, m64)", "pero desde base baja → absorbible, sin pánico",
                          "el espacio fiscal que la disciplina compró"]),
        Escenario("inicio_2004", "el punto de partida (2004)",
                  {"anio_foco": 2004.0},
                  "2004: la deuda era 45% del PBI, herencia incómoda de décadas "
                  "inestables. Lo notable no es el nivel sino lo que vino después: "
                  "el Perú decidió bajarlo en vez de gastar el boom.",
                  cadena=["2004: deuda alta (45%), herencia de inestabilidad", "empieza el superciclo",
                          "decisión: pagar deuda en vez de gastar todo", "el camino al mínimo de 2013 (disciplina)"]),
    ],
    verificaciones=[
        Verificacion("el Perú se desendeudó en el boom (45%→19%, m64)", _v_disciplina_boom),
        Verificacion("2020: la deuda saltó con el COVID (m64 crisis)", _v_covid_salto),
        Verificacion("la deuda se mantuvo moderada y sostenible", _v_sostenible),
        Verificacion("ahorrar en el boom dio espacio fiscal (vs m96)", _v_espacio_fiscal),
    ],
    notas="La aritmética de m64 en el Perú: deuda 45%→19% en el boom (g≫r + superávits), salto a 34% con el COVID desde base baja. Ahorrar en la bonanza ES la sostenibilidad — el contraejemplo de m96.",
)
