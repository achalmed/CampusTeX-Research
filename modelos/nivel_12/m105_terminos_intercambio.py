# m105_terminos_intercambio.py — términos de intercambio: PIB vs ingreso (nivel 12).
#
# Cierra el bloque del canal externo generalizando el cobre (m103) a los
# TÉRMINOS DE INTERCAMBIO completos (BCRP PN38923BM, el precio de todo lo que el
# Perú exporta sobre el precio de todo lo que importa). Dos hallazgos:
#   (1) el cobre MUEVE los términos de intercambio del Perú (corr +0.85): la TdI
#       es, sobre todo, el precio del cobre (m103) más el oro;
#   (2) y sin embargo la TdI casi no correlaciona con el crecimiento del PBI
#       (corr ~0). ¿Contradice a m103? No: lo AGUDIZA. La clave es que el PBI
#       mide VOLUMEN (cuánto se produce), mientras que una mejora de términos de
#       intercambio es un efecto de PRECIO que eleva el INGRESO nacional (cuánto
#       compra lo producido), no el volumen. El BCRP lo mide aparte (el "Efecto
#       Términos de Intercambio", PM04904AA): pasó de −27 mil M S/ en 2004 (TdI
#       bajo el año base) a +56 mil M S/ en 2024 (TdI en récord). En el
#       superciclo el INGRESO creció 8.1% vs PBI 6.6% (+1.5pp de windfall); y en
#       2024 la TdI récord dejó un PBI modesto (+3.5%) pero un ingreso de +7.5%.
# Lección: los términos de intercambio son una historia de INGRESO (poder
# adquisitivo), no de producción — por eso mueven poco el PBI y mucho el bienestar.
#
# Procedencia: datos BCRP PN38923BM (términos de intercambio, índice 2007=100),
# PM04901AA (PBI, millones S/2007) y PM04904AA (efecto términos de intercambio
# sobre el ingreso nacional, millones S/2007), muestra 2004-2024. La distinción
# PBI-volumen vs ingreso-real es contabilidad nacional estándar (SNA 2008,
# ganancias del intercambio); el BCRP publica la descomposición.

import numpy as np

from base import Ecuacion, Escenario, Ficha, Modelo, Parametro, Verificacion
from modelos.nivel_12 import _datos_bcrp
import config


def _series():
    anos, tdi = _datos_bcrp.serie("terminos_intercambio", anual=True)
    _, pbi = _datos_bcrp.serie("pbi_soles", anual=True)
    _, eti = _datos_bcrp.serie("efecto_ti", anual=True)
    ingreso = pbi + eti                             # ingreso real bruto (PBI + efecto TdI)
    gp = np.diff(pbi) / pbi[:-1] * 100
    gi = np.diff(ingreso) / ingreso[:-1] * 100
    return anos, tdi, pbi, eti, ingreso, gp, gi


def _idx_foco(anos, p):
    a = int(p["anio_foco"])
    ax = anos[1:]
    return int(np.clip(list(ax).index(a) if a in ax else len(ax) - 1, 0, len(ax) - 1))


def _curvas(p):
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    ax = anos[1:]
    i = _idx_foco(anos, p)
    return {"lineas": {"crecimiento del PBI (volumen, %)": (ax, gp, config.AZUL2),
                       "crecimiento del ingreso nacional (con efecto TdI, %)": (ax, gi, config.DORADO)},
            "puntos": [(float(ax[i]), float(gi[i]),
                        f"{int(ax[i])}: ingreso {gi[i]:+.1f}% vs PBI {gp[i]:+.1f}%")],
            "anotacion": (f"PBI (volumen) vs ingreso (PN38923BM, PM04901/04AA)\n"
                          f"superciclo: ingreso {gp[:9].mean():+.1f}→{gi[:9].mean():+.1f}% "
                          f"(windfall +{gi[:9].mean()-gp[:9].mean():.1f}pp)\n"
                          "la TdI mueve el INGRESO, no el volumen (m89)")}


def _resultados(p):
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    _, cobre = _datos_bcrp.serie("cobre", anual=True)
    i = _idx_foco(anos, p)
    iabs = list(anos).index(int(anos[1:][i]))
    dtdi = np.diff(tdi) / tdi[:-1] * 100
    return {"corr(términos de intercambio, cobre)": float(_datos_bcrp.correlacion(tdi, cobre)),
            "corr(Δ términos de intercambio, crecimiento PBI)": float(_datos_bcrp.correlacion(dtdi, gp)),
            "crecimiento PBI superciclo 2004-13 (%)": float(gp[:9].mean()),
            "crecimiento ingreso superciclo 2004-13 (%)": float(gi[:9].mean()),
            f"efecto TdI {int(anos[1:][i])} (millones S/2007)": float(eti[iabs]),
            f"crecimiento PBI {int(anos[1:][i])} (%)": float(gp[i]),
            f"crecimiento ingreso {int(anos[1:][i])} (%)": float(gi[i])}


def _ecuaciones_calibradas(p):
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    return [f"Ingreso $=$ PBI $+$ Efecto TdI; \\;superciclo: $g_{{ing}}={gi[:9].mean():.1f}\\% > g_{{PBI}}={gp[:9].mean():.1f}\\%$",
            f"Efecto TdI: $-27$ mil (2004) $\\to +56$ mil M S/ (2024): el PRECIO, no el volumen"]


_P0 = {"anio_foco": 2024.0}


def _v_cobre_mueve_ti():
    anos, tdi, *_ = _series()
    _, cobre = _datos_bcrp.serie("cobre", anual=True)
    c = _datos_bcrp.correlacion(tdi, cobre)
    return c > 0.7, \
        (f"el cobre MUEVE los términos de intercambio del Perú (corr {c:+.2f}): la TdI es, sobre todo, "
         "el precio del cobre (m103) más el oro — generaliza el canal de m103 al precio relativo agregado")


def _v_ti_debil_sobre_volumen():
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    dtdi = np.diff(tdi) / tdi[:-1] * 100
    c = _datos_bcrp.correlacion(dtdi, gp)
    return abs(c) < 0.25, \
        (f"la TdI casi no correlaciona con el PBI (corr {c:+.2f}): porque el PBI mide VOLUMEN, y una "
         "mejora de términos de intercambio es un efecto de PRECIO sobre el INGRESO (m89), no sobre la producción")


def _v_ingreso_mayor_superciclo():
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    return gi[:9].mean() > gp[:9].mean(), \
        (f"en el superciclo el INGRESO creció {gi[:9].mean():.1f}% > PBI {gp[:9].mean():.1f}%: la mejora de "
         f"términos de intercambio (m89) añadió +{gi[:9].mean()-gp[:9].mean():.1f}pp de ingreso — el windfall de precios")


def _v_2024_precio_no_volumen():
    anos, tdi, pbi, eti, ingreso, gp, gi = _series()
    i24 = list(anos[1:]).index(2024)
    eti_max = eti.max() == eti[list(anos).index(2024)]
    return eti_max and gi[i24] > gp[i24] + 2, \
        (f"2024: términos de intercambio en RÉCORD (efecto +{eti[list(anos).index(2024)]/1000:.0f} mil M S/), "
         f"PBI modesto (+{gp[i24]:.1f}%) pero INGRESO +{gi[i24]:.1f}%: la ganancia fue de PODER ADQUISITIVO "
         "(precio), no de producción (volumen) — se disuelve la paradoja 'TdI récord, poco crecimiento'")


MODELO = Modelo(
    id="m105", nivel=12,
    nombre="Términos de intercambio → PIB vs ingreso (BCRP)",
    xlabel="Año", ylabel="Crecimiento (%)",
    parametros=[
        Parametro("anio_foco", _P0["anio_foco"], 2005, 2024, 1, "Año a comparar (PBI vs ingreso)",
                  grupo="análisis", definicion="año a destacar para ver la brecha volumen-ingreso"),
    ],
    curvas=_curvas,
    resultados=_resultados,
    ecuaciones_calibradas=_ecuaciones_calibradas,
    ficha=Ficha(
        pregunta="Si en 2024 los términos de intercambio del Perú tocaron un récord, ¿por qué el PBI creció apenas 3.5%?",
        variables=[("TdI_t", "términos de intercambio, índice 2007=100 (BCRP PN38923BM)"),
                   ("PBI_t", "producto — el VOLUMEN de producción (PM04901AA)"),
                   ("Efecto TdI_t", "la ganancia/pérdida de INGRESO por precios (PM04904AA)"),
                   ("Ingreso_t", "PBI + efecto TdI: el poder adquisitivo de lo producido")],
        derivacion=["dato: \\;TdI_t \\;(PN38923BM), \\;PBI_t \\;(PM04901AA), \\;EfectoTdI_t \\;(PM04904AA)",
                    "Ingreso_t = PBI_t + EfectoTdI_t \\;(ganancias\\;del\\;intercambio, SNA)",
                    "corr(TdI, cobre) \\approx +0.85 \\;pero\\; corr(\\Delta TdI, g_{PBI}) \\approx 0",
                    "porque\\;PBI = VOLUMEN, \\;TdI \\to INGRESO \\;(precio)"],
        contexto=("Este modelo cierra el bloque del canal externo y resuelve una "
                  "paradoja que confunde a muchos lectores de datos peruanos. En "
                  "2024 los términos de intercambio del Perú —el precio de lo que "
                  "exporta dividido por el precio de lo que importa— tocaron un "
                  "récord histórico (índice 136, muy por encima del pico del "
                  "superciclo), empujados por el cobre y el oro en máximos. Y sin "
                  "embargo el PBI creció apenas 3.5%. ¿No debería un récord de "
                  "términos de intercambio disparar el crecimiento? La respuesta "
                  "enseña una de las distinciones más importantes de la "
                  "contabilidad nacional. Primero, el modelo confirma que el cobre "
                  "MUEVE los términos de intercambio del Perú: correlacionan +0.85, "
                  "así que la TdI es, en gran medida, el canal del cobre de m103 "
                  "generalizado al precio relativo agregado. Pero entonces aparece "
                  "lo sorprendente: mientras el cobre correlacionaba +0.45 con el "
                  "crecimiento (m103), los términos de intercambio agregados "
                  "correlacionan casi CERO con el PBI. La razón no es que el canal "
                  "no exista, sino que el PBI mide la cosa equivocada para esta "
                  "pregunta: el PBI mide el VOLUMEN de producción —cuántas "
                  "toneladas, cuántos servicios— y una mejora de términos de "
                  "intercambio no hace producir más toneladas; hace que cada "
                  "tonelada exportada COMPRE más importaciones. Es un efecto de "
                  "PRECIO sobre el INGRESO real, no sobre el volumen. El BCRP lo "
                  "mide explícitamente: el 'Efecto Términos de Intercambio' sobre el "
                  "ingreso nacional pasó de −27 mil millones de soles en 2004 "
                  "(cuando la TdI estaba muy por debajo del año base) a +56 mil "
                  "millones en 2024 (el récord). Sumado al PBI, da el ingreso real: "
                  "en el superciclo el INGRESO creció 8.1% anual frente a un PBI de "
                  "6.6% —el windfall de precios añadió 1.5 puntos de ingreso cada "
                  "año— y en 2024 el PBI creció 3.5% pero el ingreso 7.5%. La "
                  "paradoja se disuelve: el récord de términos de intercambio fue "
                  "real y valioso, pero se manifestó como PODER ADQUISITIVO (poder "
                  "importar más, invertir, consumir), no como más producción física "
                  "en el año. Los términos de intercambio son una historia de "
                  "ingreso, no de volumen."),
        autores=("Datos: BCRP (PN38923BM términos de intercambio, PM04901AA PBI, "
                 "PM04904AA efecto términos de intercambio); la distinción "
                 "volumen-vs-ingreso real (ganancias del intercambio): contabilidad "
                 "nacional estándar (SNA 2008) — el BCRP publica la descomposición."),
        supuestos=[
            "Ingreso real ≈ PBI + Efecto Términos de Intercambio (las 'ganancias del intercambio' del SNA): es la parte del ingreso nacional que la TdI explica; el ingreso disponible añade renta de factores y transferencias (que aquí se omiten).",
            "Los términos de intercambio (PN38923BM) son el precio agregado de exportaciones sobre importaciones (índice 2007=100): tratado como dato oficial.",
            "Correlaciones descriptivas, no causales (regla del pipeline): cuantifican co-movimiento y contabilidad, no un experimento.",
        ],
        ecuaciones=[
            Ecuacion("corr(TdI, \\; cobre) \\approx +0.85", "el cobre ES los términos de intercambio",
                     "los términos de intercambio del Perú siguen al cobre (más el oro): generaliza el "
                     "canal de m103 del cobre al precio relativo agregado — verificado."),
            Ecuacion("corr(\\Delta TdI, \\; g_{PBI}) \\approx 0 \\;\\neq\\; canal\\;inexistente", "volumen ≠ ingreso",
                     "la TdI casi no mueve el PBI porque el PBI mide VOLUMEN; el canal existe pero opera "
                     "sobre el INGRESO — el error es medir con la vara equivocada."),
            Ecuacion("Ingreso = PBI + EfectoTdI; \\;\\; g_{ing}^{superc} = 8.1\\% > g_{PBI}^{superc} = 6.6\\%",
                     "la TdI es una historia de ingreso",
                     "sumando el efecto términos de intercambio, el ingreso real creció más que el PBI en "
                     "el superciclo (+1.5pp) y en 2024 (7.5% vs 3.5%): el windfall de precios es poder adquisitivo."),
        ],
        intuicion=("La imagen es 2024: titulares de 'términos de intercambio en "
                   "máximos históricos' junto a 'la economía crece apenas 3%'. Para "
                   "el lector ingenuo, decepción o contradicción; para el "
                   "economista, la diferencia entre PRODUCIR y GANAR. El PBI cuenta "
                   "lo que el país PRODUCE en volumen; los términos de intercambio "
                   "cambian lo que ese volumen VALE en el mundo. Cuando el cobre y "
                   "el oro se disparan, el Perú no extrae de golpe más toneladas "
                   "(eso toma años de inversión, m26), pero cada tonelada le rinde "
                   "más dólares, más importaciones, más poder de compra: el ingreso "
                   "nacional sube aunque el PBI no. Por eso el 'Efecto Términos de "
                   "Intercambio' del BCRP es la pieza que falta para leer el "
                   "bienestar: en el superciclo agregó 1.5 puntos de ingreso por "
                   "año, y en 2024 la diferencia entre un PBI mediocre (3.5%) y un "
                   "ingreso robusto (7.5%) fue enteramente el precio de los "
                   "minerales. La lección se conecta con todo el bloque: m103 mostró "
                   "el canal del cobre sobre el crecimiento; m104, que sobre el tipo "
                   "de cambio se rompe; y m105 cierra mostrando que su efecto más "
                   "grande y más fiable no está en el PBI sino en el INGRESO. Un "
                   "país exportador de commodities puede tener años de PBI flojo e "
                   "ingreso boyante, y confundirlos es confundir la salud con la "
                   "suerte."),
        equilibrio=("No hay equilibrio que resolver: es la descomposición contable "
                    "del ingreso real. El resultado es que los términos de "
                    "intercambio (que el cobre gobierna, corr 0.85) mueven poco el "
                    "PBI-volumen (corr ~0) y mucho el ingreso (windfall de +1.5pp "
                    "en el superciclo, y 7.5% vs 3.5% en 2024)."),
        limitaciones=[
            "Ingreso ≈ PBI + efecto TdI omite renta de factores y transferencias (el ingreso nacional disponible completo): capta el canal de términos de intercambio, no todo el ingreso.",
            "El efecto TdI se mide respecto al año base 2007: su nivel (positivo/negativo) es relativo a ese base; lo informativo es su evolución y su signo reciente.",
            "Correlación agregada: la TdI mezcla el canal del cobre (ligado a inversión y crecimiento, m103) con el del oro (refugio, ligado a crisis) y los precios de importación — el ~0 con el PBI es en parte esa mezcla.",
        ],
        evolucion=("Cierra el bloque del canal externo (m103-m105): m103 el cobre "
                   "sobre el crecimiento, m104 sobre el tipo de cambio, m105 los "
                   "términos de intercambio sobre el ingreso. Prepara los shocks "
                   "externos extremos (m110 shock externo, m111 FED → capitales) y "
                   "conecta con la disciplina fiscal (m106-m108): un windfall de "
                   "términos de intercambio es justo lo que un fondo de "
                   "estabilización (m66) debería ahorrar para los años malos."),
    ),
    escenarios=[
        Escenario("record_2024", "el récord reciente (2024)",
                  {"anio_foco": 2024.0},
                  "2024: términos de intercambio en máximo histórico, PBI +3.5% pero "
                  "ingreso +7.5% — el récord fue poder adquisitivo (precio), no "
                  "producción (volumen). La paradoja resuelta.",
                  cadena=["cobre y oro en récord (2024)", "términos de intercambio en máximo histórico",
                          "el PBI (volumen) crece modesto (+3.5%)", "el INGRESO (precio) crece fuerte (+7.5%)",
                          "el windfall es poder adquisitivo, no producción (m89)"]),
        Escenario("superciclo_2011", "el pico del superciclo (2011)",
                  {"anio_foco": 2011.0},
                  "2011: en pleno superciclo el ingreso creció por encima del PBI — "
                  "la mejora de términos de intercambio añadía poder de compra año a "
                  "año, el windfall que financió el boom de consumo e inversión.",
                  cadena=["superciclo del cobre (2011)", "términos de intercambio altos y subiendo",
                          "efecto TdI positivo sobre el ingreso", "el ingreso crece más que el PBI",
                          "windfall que alimenta consumo e inversión (m26)"]),
        Escenario("covid_2020", "el shock COVID (2020)",
                  {"anio_foco": 2020.0},
                  "2020: caso opuesto útil — el PBI se desplomó (−10.9%) por un "
                  "shock de VOLUMEN (confinamiento), pero los términos de "
                  "intercambio ya subían (cobre, oro refugio), así que el ingreso "
                  "cayó menos (−8.4%): el precio amortiguó el golpe al volumen.",
                  cadena=["COVID: shock de volumen (confinamiento)", "el PBI cae fuerte (−10.9%)",
                          "pero cobre y oro suben (refugio)", "el efecto TdI positivo amortigua",
                          "el ingreso cae menos que el PBI (−8.4%)"]),
    ],
    verificaciones=[
        Verificacion("el cobre mueve los términos de intercambio (m103)", _v_cobre_mueve_ti),
        Verificacion("la TdI mueve poco el PBI-volumen (corr ~0)", _v_ti_debil_sobre_volumen),
        Verificacion("en el superciclo el ingreso creció más que el PBI", _v_ingreso_mayor_superciclo),
        Verificacion("2024: TdI récord = ingreso, no volumen", _v_2024_precio_no_volumen),
    ],
    notas="Los términos de intercambio son una historia de INGRESO, no de volumen: mueven poco el PBI (corr ~0) y mucho el ingreso (+1.5pp en el superciclo; 7.5% vs 3.5% en 2024). El cobre los gobierna (0.85).",
)
